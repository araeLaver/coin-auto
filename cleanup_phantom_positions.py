"""
팬텀 포지션 정리 스크립트
DB에는 있지만 거래소에는 없는 포지션 제거
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

from database import SessionLocal, Position
from api import BithumbAPI
from datetime import datetime
from decimal import Decimal

def cleanup_phantom_positions():
    """거래소 잔고와 DB 포지션 비교하여 팬텀 제거"""
    db = SessionLocal()
    api = BithumbAPI()

    try:
        # 모든 OPEN 포지션 조회
        open_positions = db.query(Position).filter(Position.status == 'OPEN').all()

        print(f"📊 총 {len(open_positions)}개 오픈 포지션 체크 중...")

        cleaned_count = 0
        error_count = 0

        for position in open_positions:
            try:
                symbol = position.symbol
                db_quantity = float(position.quantity)

                # 거래소 실제 잔고 조회
                balance = api.get_balance(symbol)

                if balance.get('status') != '0000':
                    print(f"⚠️  {symbol}: 잔고 조회 실패 - {balance.get('message')}")
                    error_count += 1
                    continue

                # 실제 보유 수량
                available_coins = float(balance['data'].get(f'available_{symbol.lower()}', 0))

                # 팬텀 포지션 체크 (DB에 있지만 거래소에 없음)
                if available_coins < db_quantity * 0.01:  # 1% 미만이면 팬텀으로 간주
                    print(f"🔴 팬텀 발견: {symbol}")
                    print(f"   DB 수량: {db_quantity:.8f}")
                    print(f"   실제 수량: {available_coins:.8f}")
                    print(f"   보유 시간: {datetime.now() - position.opened_at}")

                    # 포지션 강제 종료 (손실로 기록)
                    position.status = 'CLOSED'
                    position.closed_at = datetime.now()
                    position.exit_reason = 'PHANTOM_CLEANUP'

                    # 거래 기록 생성
                    from database import Trade
                    trade = Trade(
                        position_id=position.id,
                        symbol=position.symbol,
                        entry_price=position.entry_price,
                        exit_price=position.current_price or position.entry_price,
                        quantity=position.quantity,
                        pnl=Decimal('-0.01'),  # 소액 손실로 기록
                        pnl_percent=Decimal('-0.01'),
                        exit_reason='PHANTOM_CLEANUP',
                        opened_at=position.opened_at,
                        closed_at=datetime.now(),
                        holding_time_minutes=int((datetime.now() - position.opened_at).total_seconds() / 60),
                        strategy_id=position.strategy_id
                    )
                    db.add(trade)

                    cleaned_count += 1

            except Exception as e:
                print(f"❌ {position.symbol} 처리 에러: {str(e)}")
                error_count += 1
                continue

        # 변경사항 커밋
        db.commit()

        print("\n" + "=" * 60)
        print(f"✅ 정리 완료!")
        print(f"   제거된 팬텀 포지션: {cleaned_count}개")
        print(f"   에러 발생: {error_count}개")
        print(f"   남은 유효 포지션: {len(open_positions) - cleaned_count}개")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 전체 프로세스 에러: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    print("🧹 팬텀 포지션 정리 시작...")
    cleanup_phantom_positions()
