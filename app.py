"""
Koyeb 배포용 통합 앱
대시보드 + 자동매매 엔진 동시 실행
"""

import os
import threading
import sys
from dashboard import app as dashboard_app
from core.trading_engine_v2 import TradingEngineV2
from database.init_db import main as init_database

def run_trading_engine():
    """백그라운드에서 자동매매 엔진 실행"""
    print("🤖 자동매매 엔진 시작...")
    try:
        # DB 초기화 (최초 1회)
        try:
            init_database()
            print("✅ 데이터베이스 초기화 완료")
        except Exception as e:
            print(f"⚠️  DB 초기화 스킵: {str(e)}")

        # 초기 데이터 수집 (OHLCV 데이터가 없으면)
        from database import SessionLocal, OHLCVData
        db = SessionLocal()
        ohlcv_count = db.query(OHLCVData).count()
        db.close()

        if ohlcv_count < 50:
            print(f"📊 OHLCV 데이터 부족 ({ohlcv_count}개) - 초기 수집 시작...")
            from collect_initial_data import collect_historical_candles, collect_realtime_data
            import config

            # 각 코인별로 최근 100개 캔들 수집
            for symbol in config.TARGET_PAIRS:
                for tf in ['1m', '5m', '15m']:
                    collect_historical_candles(symbol, tf, 100)
                    import time
                    time.sleep(0.5)

            print("✅ 초기 데이터 수집 완료")

        # 트레이딩 엔진 실행
        engine = TradingEngineV2()
        engine.run(interval=60)
    except Exception as e:
        print(f"❌ 자동매매 엔진 에러: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Auto Coin Trading System - Koyeb Deployment")
    print("=" * 70)

    # 환경 변수에서 포트 가져오기 (Koyeb는 PORT 환경변수 제공)
    port = int(os.environ.get('PORT', 8000))

    print(f"✅ 대시보드 시작: 포트 {port}")
    print(f"✅ 자동매매 백그라운드 시작")
    print("=" * 70)

    # 자동매매 엔진을 백그라운드 스레드로 실행
    trading_thread = threading.Thread(target=run_trading_engine, daemon=True)
    trading_thread.start()

    # Flask 대시보드를 메인 프로세스에서 실행 (Koyeb의 health check 대상)
    dashboard_app.run(host='0.0.0.0', port=port, debug=False)
