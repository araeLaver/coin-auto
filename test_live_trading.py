"""
실시간 트레이딩 엔진 테스트
데이터 수집 -> 지표 계산 -> 시그널 생성 -> 주문 실행
"""

import time
from datetime import datetime
from core.trading_engine_v2 import TradingEngineV2
from database import SessionLocal, OHLCVData, TechnicalIndicator, TradingSignal

print("=" * 70)
print("실시간 트레이딩 엔진 테스트")
print("=" * 70)

# 엔진 생성
engine = TradingEngineV2()

print("\n[1단계] 데이터 수집 시작...")
engine.start_data_collection()
print("   데이터 수집 스레드 시작됨")

# 10초 대기 (데이터 수집)
print("\n[대기] 10초간 데이터 수집 중...")
time.sleep(10)

# 데이터 확인
db = SessionLocal()
recent_ohlcv = db.query(OHLCVData).filter(
    OHLCVData.created_at >= datetime.now()
).count()
print(f"\n   수집된 OHLCV: {recent_ohlcv}개")

print("\n[2단계] 트레이딩 사이클 실행...")
engine.execute_trading_cycle()

# 새 시그널 확인
new_signals = db.query(TradingSignal).filter(
    TradingSignal.timestamp >= datetime.now()
).all()

print(f"\n[결과] 생성된 시그널: {len(new_signals)}개")
for sig in new_signals[:5]:
    print(f"  - {sig.symbol}: {sig.signal_type}")
    print(f"    신뢰도: {float(sig.confidence):.1%}, 강도: {float(sig.strength)}")
    print(f"    진입가: {float(sig.entry_price):,.0f}원")

db.close()

print("\n" + "=" * 70)
print("테스트 완료")
print("=" * 70)
