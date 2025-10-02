"""
일일별 수익률 그래프 생성
"""

from database import SessionLocal, Trade, AccountBalance
from datetime import datetime, date, timedelta
import config
from api import BithumbAPI


def generate_daily_profit_graph():
    """일일 수익률 그래프 데이터 생성"""
    db = SessionLocal()
    api = BithumbAPI()

    # 최근 30일 데이터
    today = date.today()
    days = []
    profits = []
    balances = []

    print("=" * 80)
    print("일일 수익률 그래프 (최근 30일)")
    print("=" * 80)
    print(f"\n{'날짜':<12} {'거래수':<8} {'손익':<15} {'수익률':<10} {'잔고':<15}")
    print("-" * 80)

    for i in range(29, -1, -1):
        target_date = today - timedelta(days=i)

        # 해당일 거래 조회
        day_trades = db.query(Trade).filter(
            Trade.closed_at >= datetime.combine(target_date, datetime.min.time()),
            Trade.closed_at < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        ).all()

        # 해당일 손익
        day_pnl = sum(float(t.pnl) for t in day_trades)

        # 해당일 종료 잔고
        day_end_balance = db.query(AccountBalance).filter(
            AccountBalance.timestamp < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        ).order_by(AccountBalance.timestamp.desc()).first()

        if day_end_balance:
            balance = float(day_end_balance.total_value)
        elif target_date == today:
            # 오늘은 실시간 조회
            result = api.get_balance('ALL')
            if result.get('status') == '0000':
                data = result.get('data', {})
                current_krw = float(data.get('total_krw', 0))
                total_crypto = 0
                for symbol in config.TARGET_PAIRS[:10]:  # 상위 10개만
                    coin_balance = float(data.get(f'total_{symbol.lower()}', 0))
                    if coin_balance > 0:
                        ticker = api.get_ticker(symbol)
                        if ticker.get('status') == '0000':
                            price = float(ticker['data'].get('closing_price', 0))
                            total_crypto += coin_balance * price
                balance = current_krw + total_crypto
            else:
                balance = 0
        else:
            balance = 0

        # 수익률 계산
        if balance > 0 and day_pnl != 0:
            day_pnl_percent = (day_pnl / (balance - day_pnl)) * 100
        else:
            day_pnl_percent = 0

        days.append(target_date.strftime('%m/%d'))
        profits.append(day_pnl)
        balances.append(balance)

        # 출력
        if len(day_trades) > 0 or day_pnl != 0:
            print(f"{target_date.strftime('%Y-%m-%d'):<12} {len(day_trades):<8} "
                  f"{day_pnl:>+13,.0f}원 {day_pnl_percent:>+8.2f}% {balance:>13,.0f}원")

    # 간단한 ASCII 그래프
    print("\n" + "=" * 80)
    print("수익률 추이 (최근 10일)")
    print("=" * 80)

    recent_profits = profits[-10:]
    recent_days = days[-10:]
    max_abs = max(abs(p) for p in recent_profits) if recent_profits else 1

    for i, (day, profit) in enumerate(zip(recent_days, recent_profits)):
        if max_abs > 0:
            bar_length = int((abs(profit) / max_abs) * 40)
        else:
            bar_length = 0

        if profit >= 0:
            bar = "+" + "=" * bar_length
            print(f"{day} {bar} {profit:>+10,.0f}원")
        else:
            bar = "-" + "=" * bar_length
            print(f"{day} {bar} {profit:>+10,.0f}원")

    # 총계
    total_profit = sum(profits)
    start_balance = balances[0] - profits[0] if balances else 0
    end_balance = balances[-1] if balances else 0

    total_profit_percent = (total_profit / start_balance * 100) if start_balance > 0 else 0

    print("\n" + "=" * 80)
    print(f"30일 총 손익: {total_profit:+,.0f}원 ({total_profit_percent:+.2f}%)")
    print(f"시작 잔고: {start_balance:,.0f}원")
    print(f"현재 잔고: {end_balance:,.0f}원")
    print("=" * 80)

    db.close()


if __name__ == "__main__":
    generate_daily_profit_graph()
