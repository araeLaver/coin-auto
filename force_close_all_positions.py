"""
모든 OPEN 포지션 강제 종료 스크립트
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

from database import SessionLocal, Position, Trade
from datetime import datetime
from decimal import Decimal

def force_close_all():
    db = SessionLocal()
    try:
        # 모든 OPEN 포지션 조회
        positions = db.query(Position).filter(Position.status == 'OPEN').all()

        print(f"총 {len(positions)}개 포지션을 강제 종료합니다...")

        for pos in positions:
            # 포지션 종료
            pos.status = 'CLOSED'
            pos.closed_at = datetime.now()

            # 거래 기록
            trade = Trade(
                position_id=pos.id,
                symbol=pos.symbol,
                entry_price=pos.entry_price,
                exit_price=pos.current_price or pos.entry_price,
                quantity=pos.quantity,
                pnl=Decimal('0'),
                pnl_percent=Decimal('0'),
                exit_reason='FORCE_CLOSE_ALL',
                opened_at=pos.opened_at,
                closed_at=datetime.now(),
                holding_time_minutes=int((datetime.now() - pos.opened_at).total_seconds() / 60),
                strategy_id=pos.strategy_id
            )
            db.add(trade)
            print(f"✓ {pos.symbol} 종료")

        db.commit()
        print(f"\n✅ {len(positions)}개 포지션 모두 종료 완료!")

    except Exception as e:
        print(f"❌ 에러: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    force_close_all()
