"""
모든 보유 코인 전량 매도
"""

from api import BithumbAPI
import config
import time

api = BithumbAPI()

# 실제 잔고 조회
balance = api.get_balance('ALL')
if balance.get('status') != '0000':
    print("잔고 조회 실패")
    exit()

data = balance.get('data', {})

print("\n=== 전량 매도 시작 ===\n")

sold_count = 0
total_value = 0

for symbol in config.TARGET_PAIRS[:100]:  # 상위 100개만 확인
    coin_balance = float(data.get(f'total_{symbol.lower()}', 0))

    if coin_balance > 0:
        # 현재가 조회
        ticker = api.get_ticker(symbol)
        if ticker.get('status') != '0000':
            continue

        current_price = float(ticker['data']['closing_price'])
        value = coin_balance * current_price

        # 5000원 이상만 매도
        if value >= 5000:
            print(f"[{symbol}] 매도: {coin_balance:.8f}개 (약 {value:,.0f}원)")

            # 시장가 매도 (현재가보다 1% 낮게 지정가)
            order_price = int(current_price * 0.99)
            result = api.place_order(symbol, 'ask', coin_balance, order_price)

            if result.get('status') == '0000':
                print(f"  OK 매도 성공")
                sold_count += 1
                total_value += value
            else:
                print(f"  ERROR {result.get('message')}")

            time.sleep(0.5)  # API 제한 방지

print(f"\n=== 매도 완료 ===")
print(f"매도 종목: {sold_count}개")
print(f"총 매도금액: 약 {total_value:,.0f}원")
