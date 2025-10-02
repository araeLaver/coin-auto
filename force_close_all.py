"""
모든 포지션 강제 청산
"""

from database import SessionLocal, Position
from core.order_executor import OrderExecutor
from datetime import datetime

db = SessionLocal()
executor = OrderExecutor()

# 모든 OPEN 포지션 조회
open_positions = db.query(Position).filter(Position.status == 'OPEN').all()

print(f"\n총 {len(open_positions)}개 포지션 청산 시작...\n")

for pos in open_positions:
    try:
        # OrderExecutor로 청산
        success = executor.close_position(pos, float(pos.entry_price), '수동청산')

        if success:
            print(f"[{pos.symbol}] OK 청산 완료")
        else:
            print(f"[{pos.symbol}] ERROR 청산 실패")

    except Exception as e:
        print(f"[{pos.symbol}] 에러: {str(e)}")

db.close()

print("\n청산 완료!")
