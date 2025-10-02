"""
자동매매 시스템 + 대시보드 동시 실행
"""

import threading
import sys
import os
from dashboard import app as dashboard_app
from core.trading_engine_v2 import TradingEngineV2

def run_dashboard():
    """대시보드 웹서버 실행"""
    print("🌐 대시보드 서버 시작: http://localhost:8080")
    dashboard_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

def run_trading():
    """자동매매 엔진 실행"""
    print("🤖 자동매매 엔진 시작...")
    try:
        engine = TradingEngineV2()
        engine.run(interval=60)
    except KeyboardInterrupt:
        print("\n자동매매 엔진 중단")
    except Exception as e:
        print(f"자동매매 엔진 에러: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 70)
    print("🚀 Auto Coin Trading System - Full Stack")
    print("=" * 70)
    print("")
    print("✅ 대시보드: http://localhost:8080")
    print("✅ 자동매매: 60초 주기")
    print("")
    print("Ctrl+C로 종료")
    print("=" * 70)
    print("")

    # 대시보드 스레드
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()

    # 자동매매는 메인 스레드에서 실행 (KeyboardInterrupt 처리)
    try:
        run_trading()
    except KeyboardInterrupt:
        print("\n\n시스템 종료 중...")
        sys.exit(0)

if __name__ == "__main__":
    main()
