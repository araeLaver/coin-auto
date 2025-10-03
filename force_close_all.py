"""
모든 오픈 포지션 강제 청산
"""
from database import SessionLocal, Position
from core.order_executor import OrderExecutor
from datetime import datetime

db = SessionLocal()
executor = OrderExecutor()

try:
    # 모든 오픈 포지션 조회
    positions = db.query(Position).filter(Position.status == 'OPEN').all()

    print(f"총 {len(positions)}개 오픈 포지션 강제 청산 시작...")

    for pos in positions:
        try:
            # 현재가 조회
            ticker = executor.api.get_ticker(pos.symbol)
            if ticker.get('status') == '0000':
                current_price = float(ticker['data'].get('closing_price', 0))

                print(f"\n청산 중: {pos.symbol} @ {current_price:,.0f}원")

                # 강제 청산
                success = executor.close_position(pos, current_price, 'FORCE_CLOSE')

                if success:
                    print(f"  ✅ 청산 완료")
                else:
                    print(f"  ❌ 청산 실패")
        except Exception as e:
            print(f"  ❌ 에러: {str(e)}")

    print(f"\n\n전체 청산 완료!")

except Exception as e:
    print(f"에러: {str(e)}")
finally:
    db.close()
