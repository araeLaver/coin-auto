"""
트레이딩 엔진 1회 실행 테스트
시그널 생성 -> 매매 실행까지 확인
"""

import time
from datetime import datetime
from core.trading_engine_v2 import TradingEngineV2
from database import SessionLocal, TradingSignal, Position

print("=" * 70)
print(f"트레이딩 엔진 테스트 - {datetime.now()}")
print("=" * 70)

# 이전 시그널 카운트
db = SessionLocal()
before_signals = db.query(TradingSignal).count()
before_positions = db.query(Position).count()
db.close()

print(f"\n실행 전:")
print(f"  총 시그널: {before_signals}개")
print(f"  총 포지션: {before_positions}개")

# 엔진 실행
print(f"\n트레이딩 엔진 시작...")
engine = TradingEngineV2()

print(f"데이터 수집 시작...")
engine.start_data_collection()

print(f"10초 대기 (데이터 수집)...")
time.sleep(10)

print(f"\n트레이딩 사이클 실행...")
engine.execute_trading_cycle()

# 결과 확인
db = SessionLocal()
after_signals = db.query(TradingSignal).count()
after_positions = db.query(Position).count()

new_signals = db.query(TradingSignal).order_by(TradingSignal.timestamp.desc()).limit(5).all()
new_positions = db.query(Position).order_by(Position.created_at.desc()).limit(5).all()

print(f"\n실행 후:")
print(f"  총 시그널: {after_signals}개 (+{after_signals - before_signals})")
print(f"  총 포지션: {after_positions}개 (+{after_positions - before_positions})")

if new_signals:
    print(f"\n최근 시그널:")
    for sig in new_signals[:3]:
        print(f"  - {sig.symbol} {sig.signal_type} (신뢰도: {float(sig.confidence):.1%})")

if new_positions:
    print(f"\n최근 포지션:")
    for pos in new_positions[:3]:
        print(f"  - {pos.symbol} {pos.position_type} (진입가: {float(pos.entry_price):,.0f}원)")

db.close()

# 엔진 종료
engine.stop()

print("\n" + "=" * 70)
print("테스트 완료")
print("=" * 70)
