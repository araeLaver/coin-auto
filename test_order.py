"""
주문 API 직접 테스트
"""

from api.bithumb_client import BithumbAPI

api = BithumbAPI()

# 아주 작은 주문으로 테스트
print("빗썸 주문 API 테스트")
print("=" * 70)

# BTC 시장가 매수 (10,000원)
result = api.place_order(
    symbol='BTC',
    order_type='market_bid',  # 시장가 매수
    quantity=10000,  # KRW 금액
    price=None
)

print(f"\n결과:")
print(f"  Status: {result.get('status')}")
print(f"  Message: {result.get('message')}")
print(f"  Full Response: {result}")
