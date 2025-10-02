"""
실시간 자동매매 엔진 실행
"""

import time
from datetime import datetime
from core.trading_engine_v2 import TradingEngineV2

print("=" * 70)
print(f"실시간 자동매매 시작 - {datetime.now()}")
print("=" * 70)

engine = TradingEngineV2()

# 데이터 수집 시작
print("\n데이터 수집 시작...")
engine.start_data_collection()

print("60초 대기 (초기 데이터 수집)...")
time.sleep(60)

print("\n트레이딩 사이클 시작 (60초마다 반복)...")

try:
    cycle = 0
    while True:
        cycle += 1
        print(f"\n{'='*70}")
        print(f"[사이클 {cycle}] {datetime.now()}")
        print(f"{'='*70}")

        engine.execute_trading_cycle()

        print(f"\n다음 사이클까지 60초 대기...")
        time.sleep(60)

except KeyboardInterrupt:
    print("\n\n자동매매 중지...")
    engine.stop()
    print("종료됨")
