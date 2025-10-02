"""
당일 수익률 조회 스크립트
"""

from database import SessionLocal, Trade, AccountBalance
from datetime import datetime, date
import config


def get_daily_profit():
    """당일 실제 거래 기반 수익률 출력"""
    from api import BithumbAPI

    db = SessionLocal()
    api = BithumbAPI()
    today = date.today()

    print("=" * 60)
    print(f"당일 수익률 현황 - {today}")
    print("=" * 60)

    # 실제 현재 잔고
    result = api.get_balance('ALL')
    if result.get('status') == '0000':
        data = result.get('data', {})
        current_krw = float(data.get('total_krw', 0))

        # 보유 코인 평가액
        total_crypto = 0
        for symbol in config.TARGET_PAIRS:
            coin_balance = float(data.get(f'total_{symbol.lower()}', 0))
            if coin_balance > 0:
                ticker = api.get_ticker(symbol)
                if ticker.get('status') == '0000':
                    price = float(ticker['data'].get('closing_price', 0))
                    total_crypto += coin_balance * price

        current_value = current_krw + total_crypto
    else:
        current_value = 0

    # 당일 청산된 거래만 조회
    today_trades = db.query(Trade).filter(
        Trade.closed_at >= datetime.combine(today, datetime.min.time())
    ).all()

    # 당일 총 손익 (청산된 거래만)
    total_pnl = sum(float(t.pnl) for t in today_trades)
    winning_trades = [t for t in today_trades if float(t.pnl) > 0]
    losing_trades = [t for t in today_trades if float(t.pnl) <= 0]

    # 시작 잔고 = 현재 - 당일 손익
    start_balance = current_value - total_pnl

    # 수익률 계산
    pnl_percent = (total_pnl / start_balance * 100) if start_balance > 0 else 0

    print(f"\n시작 잔고: {start_balance:,.0f}원")
    print(f"현재 잔고: {current_value:,.0f}원")
    print(f"당일 손익: {total_pnl:+,.0f}원 ({pnl_percent:+.2f}%)")
    print(f"\n거래 내역 (청산 완료):")
    print(f"  총 거래: {len(today_trades)}건")
    print(f"  수익 거래: {len(winning_trades)}건")
    print(f"  손실 거래: {len(losing_trades)}건")

    if len(today_trades) > 0:
        win_rate = len(winning_trades) / len(today_trades) * 100
        print(f"  승률: {win_rate:.1f}%")

        # 수수료 계산 (왕복 0.5%)
        total_fee = sum(abs(float(t.pnl)) * 0.005 for t in today_trades)
        print(f"  총 수수료: {total_fee:,.0f}원 (예상)")

    print(f"\n상세 거래:")
    for trade in today_trades:
        pnl_emoji = "+" if float(trade.pnl) > 0 else ""
        print(f"  {trade.symbol}: {pnl_emoji}{float(trade.pnl):,.0f}원 ({float(trade.pnl_percent):+.2f}%) - {trade.closed_at.strftime('%H:%M:%S')}")

    db.close()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    get_daily_profit()
