"""
모의 거래 테스트
"""

import os
os.environ['TRADE_MODE'] = 'paper'

from core.order_executor import OrderExecutor
from database import SessionLocal, Position

executor = OrderExecutor()

import config
print(f"거래 모드: {config.TRADE_MODE}")
print(f"\n계좌 잔고:")
balance = executor.get_account_balance()
print(f"  가용 KRW: {balance.get('available_krw', 0):,.0f}원")

# 테스트 시그널 (TradingSignal 객체 생성)
from database import TradingSignal
from decimal import Decimal

test_signal = TradingSignal(
    strategy_id=1,
    symbol='BTC',
    signal_type='BUY',
    entry_price=Decimal('168000000'),
    stop_loss=Decimal('164640000'),
    take_profit=Decimal('176400000'),
    confidence=Decimal('0.75'),
    strength=Decimal('80')
)

position_size = 11000

print(f"\n테스트 주문 실행...")
print(f"  코인: {test_signal.symbol}")
print(f"  타입: {test_signal.signal_type}")
print(f"  금액: {position_size:,.0f}원")

position = executor.execute_signal(test_signal, position_size)

if position:
    print(f"\n[SUCCESS] 주문 성공!")
    print(f"  포지션 ID: {position.id}")
    print(f"  진입가: {float(position.entry_price):,.0f}원")
    print(f"  수량: {float(position.quantity):.8f}")
else:
    print(f"\n[FAIL] 주문 실패")

# DB 확인
db = SessionLocal()
latest_position = db.query(Position).order_by(Position.id.desc()).first()
if latest_position:
    print(f"\nDB 최신 포지션:")
    print(f"  {latest_position.symbol} {latest_position.position_type}")
    print(f"  상태: {latest_position.status}")
db.close()
