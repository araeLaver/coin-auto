"""
Auto Coin Trading - 메인 실행 파일
"""

import sys
import argparse
from core.trading_engine import TradingEngine
from database.init_db import main as init_database
from utils.telegram_notifier import TelegramNotifier


def main():
    parser = argparse.ArgumentParser(description='Auto Coin Trading System')
    parser.add_argument('--mode', choices=['init', 'run', 'collect'], default='run',
                       help='실행 모드 (init: DB 초기화, run: 트레이딩 실행, collect: 데이터 수집)')
    parser.add_argument('--interval', type=int, default=60,
                       help='트레이딩 주기 (초, 기본값: 60)')

    args = parser.parse_args()

    if args.mode == 'init':
        print("데이터베이스 초기화 중...")
        init_database()

    elif args.mode == 'run':
        print("트레이딩 시스템 시작...")

        # 텔레그램 알림
        notifier = TelegramNotifier()
        notifier.notify_system_start()

        try:
            engine = TradingEngine()
            engine.run(interval=args.interval)
        except KeyboardInterrupt:
            print("\n시스템 종료 중...")
            notifier.notify_system_stop()
        except Exception as e:
            print(f"치명적 에러: {str(e)}")
            notifier.notify_error(f"치명적 에러: {str(e)}")

    elif args.mode == 'collect':
        print("데이터 수집 모드...")
        from collectors.orderbook_collector import OrderbookCollector
        from collectors.price_collector import PriceCollector
        from analysis.indicators import IndicatorEngine
        import config
        import threading

        # 멀티스레드로 데이터 수집
        def run_orderbook_collector():
            collector = OrderbookCollector()
            collector.run_collection_loop(config.TARGET_PAIRS, interval=1)

        def run_price_collector():
            collector = PriceCollector()
            collector.run_collection_loop(config.TARGET_PAIRS, interval=5)

        def run_indicator_engine():
            engine = IndicatorEngine()
            timeframes = ['5m', '15m', '1h']
            engine.run_calculation_loop(config.TARGET_PAIRS, timeframes, interval=60)

        threads = [
            threading.Thread(target=run_orderbook_collector, daemon=True),
            threading.Thread(target=run_price_collector, daemon=True),
            threading.Thread(target=run_indicator_engine, daemon=True)
        ]

        for thread in threads:
            thread.start()

        print("데이터 수집 중... (Ctrl+C로 종료)")

        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("\n데이터 수집 종료")


if __name__ == "__main__":
    main()
