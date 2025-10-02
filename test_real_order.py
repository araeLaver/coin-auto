"""
실제 빗썸 API 주문 테스트
작은 금액으로 실제 주문이 되는지 확인
"""

from api.bithumb_client import BithumbAPI

api = BithumbAPI()

print("=" * 70)
print("빗썸 실제 주문 테스트")
print("=" * 70)

# 1. 지정가 매수 테스트 (최소 금액)
print("\n[테스트 1] 지정가 매수 (1,000원)")
result1 = api.place_order(
    symbol='XRP',  # XRP는 가격이 낮아서 테스트하기 좋음
    order_type='bid',  # 지정가 매수
    quantity=0.5,  # 0.5개 (약 2,000원)
    price=4000  # 4,000원에 매수
)
print(f"  Status: {result1.get('status')}")
print(f"  Message: {result1.get('message')}")
if result1.get('status') != '0000':
    print(f"  Full: {result1}")

# 2. 빗썸 시장가 매수는 어떻게?
print("\n[테스트 2] 빗썸 API 잔고 확인")
balance = api.get_balance('XRP')
print(f"  Status: {balance.get('status')}")
print(f"  Available KRW: {balance.get('data', {}).get('available_krw', 'N/A')}")

# 3. 빗썸 최신 공시사항 확인
print("\n빗썸 API 주문 규칙:")
print("  - 지정가 매수: type='bid', units=수량, price=가격")
print("  - 시장가 매수: 빗썸은 시장가를 지원하지 않을 수도 있음")
print("  - 최소 주문: 1,000원 이상")
