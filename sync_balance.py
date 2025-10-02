"""
DB 잔고를 실제 빗썸 잔고와 동기화
"""

from database import SessionLocal, Position, AccountBalance
from api import BithumbAPI
from datetime import datetime
from decimal import Decimal
import config

db = SessionLocal()
api = BithumbAPI()

print("=" * 60)
print("DB 잔고 동기화")
print("=" * 60)

# 1. 실제 빗썸 잔고 조회
result = api.get_balance('ALL')

if result.get('status') != '0000':
    print(f"잔고 조회 실패: {result.get('message')}")
    exit(1)

data = result.get('data', {})
total_krw = float(data.get('total_krw', 0))
available_krw = float(data.get('available_krw', 0))

print(f"\n실제 빗썸 잔고:")
print(f"  KRW: {total_krw:,.0f}원")

# 2. 실제 보유 코인 확인
real_coins = {}
total_crypto_value = 0

for symbol in config.TARGET_PAIRS:
    coin_key = f'total_{symbol.lower()}'
    coin_balance = float(data.get(coin_key, 0))

    if coin_balance > 0:
        ticker = api.get_ticker(symbol)
        if ticker.get('status') == '0000':
            current_price = float(ticker['data'].get('closing_price', 0))
            coin_value = coin_balance * current_price
            total_crypto_value += coin_value

            real_coins[symbol] = {
                'balance': coin_balance,
                'price': current_price,
                'value': coin_value
            }
            print(f"  {symbol}: {coin_balance:.8f} 개 (평가액: {coin_value:,.0f}원)")

total_value = total_krw + total_crypto_value

print(f"\n총 자산: {total_value:,.0f}원")

# 3. DB의 OPEN 포지션 확인
db_positions = db.query(Position).filter(Position.status == 'OPEN').all()

print(f"\n\nDB OPEN 포지션: {len(db_positions)}개")

for pos in db_positions:
    print(f"  {pos.symbol}: {float(pos.quantity):.8f} 개 (진입가: {float(pos.entry_price):,.0f}원)")

    # 실제로 보유하고 있는지 확인
    if pos.symbol in real_coins:
        real_qty = real_coins[pos.symbol]['balance']
        db_qty = float(pos.quantity)

        if abs(real_qty - db_qty) > 0.00000001:  # 오차 범위
            print(f"    ⚠️  수량 불일치! DB: {db_qty:.8f}, 실제: {real_qty:.8f}")
    else:
        print(f"    ❌ 실제 보유하고 있지 않음 -> 포지션 삭제")
        # 포지션 삭제
        db.delete(pos)

# 4. DB에 새 잔고 기록
new_balance = AccountBalance(
    timestamp=datetime.now(),
    total_krw=Decimal(str(total_krw)),
    total_crypto_value=Decimal(str(total_crypto_value)),
    total_value=Decimal(str(total_value)),
    available_krw=Decimal(str(available_krw)),
    positions_value=Decimal(str(total_crypto_value)),
    unrealized_pnl=Decimal('0')
)

db.add(new_balance)
db.commit()

print(f"\n\n✅ DB 동기화 완료!")
print(f"  동기화된 잔고: {total_value:,.0f}원")

db.close()
