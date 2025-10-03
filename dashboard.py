"""
자동매매 모니터링 대시보드
실시간 포지션, 거래내역, 성과 확인
"""

from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from decimal import Decimal
from database import SessionLocal, Position, Trade, DailyPerformance, TradingSignal, Strategy, AccountBalance
from sqlalchemy import func, desc
import config

app = Flask(__name__)


@app.route('/')
def dashboard():
    """메인 대시보드 페이지"""
    return render_template('dashboard.html')


@app.route('/api/version')
def get_version():
    """버전 확인 (배포 확인용)"""
    import subprocess
    try:
        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
    except:
        commit = 'unknown'
    return jsonify({
        'version': '2.0-fast',
        'commit': commit,
        'interval': 10,
        'max_positions': 3,
        'timeout': '1min'
    })


@app.route('/api/status')
def get_status():
    """시스템 상태"""
    db = SessionLocal()
    try:
        # 현재 잔고
        latest_balance = db.query(AccountBalance).order_by(
            AccountBalance.timestamp.desc()
        ).first()

        # 오픈 포지션 수
        open_positions_count = db.query(Position).filter(
            Position.status == 'OPEN'
        ).count()

        # 오늘 거래 수
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_trades = db.query(Trade).filter(
            Trade.closed_at >= today_start
        ).count()

        # 실제 계좌 잔고 조회 (live 모드일 때)
        from core.order_executor import OrderExecutor
        executor = OrderExecutor()
        balance_info = executor.get_account_balance()

        return jsonify({
            'status': 'running',
            'mode': config.TRADE_MODE,
            'balance': balance_info.get('total_value', 0),
            'available_krw': balance_info.get('available_krw', 0),
            'crypto_value': balance_info.get('total_crypto_value', 0),
            'open_positions': open_positions_count,
            'today_trades': today_trades,
            'last_update': datetime.now().isoformat()
        })
    finally:
        db.close()


@app.route('/api/holdings')
def get_holdings():
    """실제 보유 코인 목록"""
    from core.order_executor import OrderExecutor
    executor = OrderExecutor()
    balance_info = executor.get_account_balance()

    holdings = balance_info.get('crypto_holdings', {})

    result = []
    for symbol, data in holdings.items():
        result.append({
            'symbol': symbol,
            'balance': data['balance'],
            'current_price': data['price'],
            'value': data['value']
        })

    return jsonify(result)


@app.route('/api/positions')
def get_positions():
    """현재 오픈 포지션"""
    db = SessionLocal()
    try:
        positions = db.query(Position).filter(
            Position.status == 'OPEN'
        ).order_by(Position.opened_at.desc()).all()

        result = []
        for pos in positions:
            pnl = float(pos.unrealized_pnl) if pos.unrealized_pnl else 0
            entry_value = float(pos.entry_price) * float(pos.quantity)
            pnl_percent = (pnl / entry_value * 100) if entry_value > 0 else 0

            result.append({
                'id': pos.id,
                'symbol': pos.symbol,
                'type': pos.position_type,
                'entry_price': float(pos.entry_price),
                'current_price': float(pos.current_price) if pos.current_price else float(pos.entry_price),
                'quantity': float(pos.quantity),
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'stop_loss': float(pos.stop_loss) if pos.stop_loss else None,
                'take_profit': float(pos.take_profit) if pos.take_profit else None,
                'opened_at': pos.opened_at.isoformat(),
                'holding_time': str(datetime.now() - pos.opened_at)
            })

        return jsonify(result)
    finally:
        db.close()


@app.route('/api/trades')
def get_trades():
    """최근 거래 내역 (50건)"""
    db = SessionLocal()
    try:
        trades = db.query(Trade).order_by(
            Trade.closed_at.desc()
        ).limit(50).all()

        result = []
        for trade in trades:
            result.append({
                'id': trade.id,
                'symbol': trade.symbol,
                'entry_price': float(trade.entry_price),
                'exit_price': float(trade.exit_price),
                'quantity': float(trade.quantity),
                'pnl': float(trade.pnl),
                'pnl_percent': float(trade.pnl_percent),
                'exit_reason': trade.exit_reason,
                'holding_time': trade.holding_time_minutes,
                'opened_at': trade.opened_at.isoformat(),
                'closed_at': trade.closed_at.isoformat()
            })

        return jsonify(result)
    finally:
        db.close()


@app.route('/api/performance')
def get_performance():
    """일일 실제 거래 기반 성과 (최근 30일)"""
    from datetime import date, timedelta
    from api import BithumbAPI

    db = SessionLocal()
    api = BithumbAPI()

    try:
        today = date.today()
        result = []

        for i in range(29, -1, -1):
            target_date = today - timedelta(days=i)

            # 해당일 청산 완료된 거래
            day_trades = db.query(Trade).filter(
                Trade.closed_at >= datetime.combine(target_date, datetime.min.time()),
                Trade.closed_at < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
            ).all()

            if not day_trades:
                continue

            day_pnl = sum(float(t.pnl) for t in day_trades)
            winning = len([t for t in day_trades if float(t.pnl) > 0])
            losing = len([t for t in day_trades if float(t.pnl) <= 0])

            result.append({
                'date': target_date.isoformat(),
                'pnl': day_pnl,
                'total_trades': len(day_trades),
                'winning_trades': winning,
                'losing_trades': losing,
                'win_rate': (winning / len(day_trades) * 100) if day_trades else 0
            })

        return jsonify(result)
    finally:
        db.close()


@app.route('/api/signals')
def get_signals():
    """최근 시그널 (20건)"""
    db = SessionLocal()
    try:
        signals = db.query(TradingSignal, Strategy).join(
            Strategy, TradingSignal.strategy_id == Strategy.id
        ).order_by(
            TradingSignal.timestamp.desc()
        ).limit(20).all()

        result = []
        for signal, strategy in signals:
            result.append({
                'id': signal.id,
                'strategy': strategy.name,
                'symbol': signal.symbol,
                'signal_type': signal.signal_type,
                'strength': float(signal.strength),
                'confidence': float(signal.confidence),
                'entry_price': float(signal.entry_price),
                'reasoning': signal.reasoning,
                'timestamp': signal.timestamp.isoformat()
            })

        return jsonify(result)
    finally:
        db.close()


@app.route('/api/strategies')
def get_strategies():
    """전략별 성과"""
    db = SessionLocal()
    try:
        # 전략별 거래 통계
        from sqlalchemy import case
        stats = db.query(
            Strategy.name,
            func.count(Trade.id).label('total_trades'),
            func.sum(Trade.pnl).label('total_pnl'),
            func.avg(Trade.pnl_percent).label('avg_pnl_percent'),
            func.sum(case((Trade.pnl > 0, 1), else_=0)).label('winning_trades')
        ).join(
            Trade, Strategy.id == Trade.strategy_id
        ).group_by(
            Strategy.name
        ).all()

        result = []
        for stat in stats:
            win_rate = (stat.winning_trades / stat.total_trades * 100) if stat.total_trades > 0 else 0
            result.append({
                'strategy': stat.name,
                'total_trades': stat.total_trades,
                'total_pnl': float(stat.total_pnl) if stat.total_pnl else 0,
                'avg_pnl_percent': float(stat.avg_pnl_percent) if stat.avg_pnl_percent else 0,
                'win_rate': win_rate
            })

        return jsonify(result)
    finally:
        db.close()


@app.route('/api/summary')
def get_summary():
    """전체 요약 통계"""
    db = SessionLocal()
    try:
        # 전체 거래 통계
        total_trades = db.query(Trade).count()
        winning_trades = db.query(Trade).filter(Trade.pnl > 0).count()
        total_pnl = db.query(func.sum(Trade.pnl)).scalar() or 0

        # 최근 30일 성과
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_trades = db.query(Trade).filter(
            Trade.closed_at >= thirty_days_ago
        ).all()

        recent_pnl = sum(float(t.pnl) for t in recent_trades)
        recent_count = len(recent_trades)
        recent_wins = sum(1 for t in recent_trades if float(t.pnl) > 0)

        # 최고/최저 거래
        best_trade = db.query(Trade).order_by(Trade.pnl.desc()).first()
        worst_trade = db.query(Trade).order_by(Trade.pnl.asc()).first()

        # 현재 잔고
        latest_balance = db.query(AccountBalance).order_by(
            AccountBalance.timestamp.desc()
        ).first()

        current_value = float(latest_balance.total_value) if latest_balance else config.INITIAL_CAPITAL
        initial_value = config.INITIAL_CAPITAL
        total_return = ((current_value - initial_value) / initial_value * 100) if initial_value > 0 else 0

        return jsonify({
            'total_trades': total_trades,
            'total_pnl': float(total_pnl),
            'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
            'current_value': current_value,
            'initial_value': initial_value,
            'total_return': total_return,
            'recent_30d': {
                'trades': recent_count,
                'pnl': recent_pnl,
                'win_rate': (recent_wins / recent_count * 100) if recent_count > 0 else 0
            },
            'best_trade': {
                'symbol': best_trade.symbol if best_trade else None,
                'pnl': float(best_trade.pnl) if best_trade else 0,
                'pnl_percent': float(best_trade.pnl_percent) if best_trade else 0
            } if best_trade else None,
            'worst_trade': {
                'symbol': worst_trade.symbol if worst_trade else None,
                'pnl': float(worst_trade.pnl) if worst_trade else 0,
                'pnl_percent': float(worst_trade.pnl_percent) if worst_trade else 0
            } if worst_trade else None
        })
    finally:
        db.close()


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
