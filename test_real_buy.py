"""
실제 매수 주문 테스트 (5,000원)
"""

import os
os.environ['TRADE_MODE'] = 'live'

from core.order_executor import OrderExecutor
from database import SessionLocal, TradingSignal, Position
from decimal import Decimal
from api.bithumb_client import BithumbAPI

# 현재 XRP 가격 확인
api = BithumbAPI()
ticker = api.get_ticker('XRP')
current_price = float(ticker['data']['closing_price'])

print("=" * 70)
print("실제 매수 주문 테스트")
print("=" * 70)
print(f"\n현재 XRP 가격: {current_price:,.0f}원")

executor = OrderExecutor()
balance = executor.get_account_balance()
print(f"가용 KRW: {balance.get('available_krw', 0):,.0f}원")

# 최소 금액 5,000원으로 테스트 시그널
test_signal = TradingSignal(
    strategy_id=1,
    symbol='XRP',
    signal_type='BUY',
    entry_price=Decimal(str(current_price)),
    stop_loss=Decimal(str(current_price * 0.98)),
    take_profit=Decimal(str(current_price * 1.05)),
    confidence=Decimal('0.75'),
    strength=Decimal('80')
)

position_size = 5500  # 최소 금액보다 약간 크게

print(f"\n주문 실행 (5,500원)...")
position = executor.execute_signal(test_signal, position_size)

if position:
    print(f"\n[SUCCESS] 실제 매수 성공!")
    print(f"  포지션 ID: {position.id}")
    print(f"  심볼: {position.symbol}")
    print(f"  진입가: {float(position.entry_price):,.2f}원")
    print(f"  수량: {float(position.quantity):.4f}")

    # DB 확인
    db = SessionLocal()
    latest = db.query(Position).filter(Position.id == position.id).first()
    print(f"\nDB 확인:")
    print(f"  상태: {latest.status}")
    print(f"  타입: {latest.position_type}")
    db.close()
else:
    print(f"\n[FAIL] 주문 실패")
