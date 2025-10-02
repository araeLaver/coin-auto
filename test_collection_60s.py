"""
60초간 데이터 수집 테스트
"""

import time
from datetime import datetime, timedelta
from core.trading_engine_v2 import TradingEngineV2
from database import SessionLocal, OHLCVData

print("=" * 70)
print("60초 데이터 수집 테스트")
print("=" * 70)

# 엔진 생성 및 시작
engine = TradingEngineV2()
engine.start_data_collection()

print("\n데이터 수집 시작됨...")
print("60초 대기 중 (1분봉 생성 대기)...")

for i in range(6):
    time.sleep(10)
    print(f"  {(i+1)*10}초 경과...")

print("\n수집된 데이터 확인...")

# 새로운 DB 세션 생성
db2 = SessionLocal()

# 최근 2분간 데이터 확인
recent_time = datetime.now() - timedelta(minutes=2)
recent_ohlcv = db2.query(OHLCVData).filter(
    OHLCVData.created_at >= recent_time
).all()

print(f"\n최근 2분간 저장된 OHLCV: {len(recent_ohlcv)}개")

if recent_ohlcv:
    for ohlcv in recent_ohlcv[:10]:
        print(f"  {ohlcv.symbol} {ohlcv.timeframe} - {ohlcv.timestamp} (price: {float(ohlcv.close):,.0f})")
else:
    print("  데이터 없음")

    # 전체 최신 데이터 확인
    latest = db2.query(OHLCVData).order_by(OHLCVData.created_at.desc()).first()
    if latest:
        print(f"\n  DB 최신 데이터: {latest.symbol} at {latest.created_at}")

    # 타임프레임별 확인
    for tf in ['1m', '5m', '15m']:
        count = db2.query(OHLCVData).filter(OHLCVData.timeframe == tf).count()
        print(f"  {tf} 데이터: {count}개")

db2.close()

# 엔진 종료
engine.stop()

print("\n" + "=" * 70)
print("테스트 완료")
print("=" * 70)
