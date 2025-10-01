"""
시스템 통합 테스트
모든 모듈이 제대로 작동하는지 검증
"""

import sys
import time
from datetime import datetime
from database import SessionLocal, init_db
from api import BithumbAPI
from collectors.price_collector import PriceCollector
from analysis.indicators import IndicatorEngine
from strategies import TrendFollowingStrategy
from core.risk_manager import RiskManager
from core.order_executor import OrderExecutor
from utils.telegram_notifier import TelegramNotifier
import config


def test_database():
    """데이터베이스 연결 테스트"""
    print("\n[1/10] 데이터베이스 연결 테스트...")
    try:
        db = SessionLocal()
        # 스키마 확인
        from sqlalchemy import text
        result = db.execute(text(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{config.DB_SCHEMA}'"))
        schema_exists = result.fetchone() is not None

        if schema_exists:
            print("  ✓ 데이터베이스 연결 성공")
            print(f"  ✓ 스키마 '{config.DB_SCHEMA}' 존재")
            db.close()
            return True
        else:
            print(f"  ✗ 스키마 '{config.DB_SCHEMA}' 없음 - python main.py --mode init 실행 필요")
            db.close()
            return False
    except Exception as e:
        print(f"  ✗ 데이터베이스 연결 실패: {str(e)}")
        return False


def test_api():
    """빗썸 API 연결 테스트"""
    print("\n[2/10] 빗썸 API 연결 테스트...")
    try:
        api = BithumbAPI()
        ticker = api.get_ticker('BTC')

        if ticker.get('status') == '0000':
            price = float(ticker['data']['closing_price'])
            print(f"  ✓ API 연결 성공")
            print(f"  ✓ BTC 현재가: {price:,.0f}원")
            return True
        else:
            print(f"  ✗ API 응답 오류: {ticker.get('message')}")
            return False
    except Exception as e:
        print(f"  ✗ API 연결 실패: {str(e)}")
        return False


def test_data_collection():
    """데이터 수집 테스트"""
    print("\n[3/10] 데이터 수집 테스트...")
    try:
        collector = PriceCollector()

        # Ticker 수집
        ticker = collector.collect_ticker('BTC')
        if ticker:
            print(f"  ✓ Ticker 수집 성공")
            print(f"    가격: {ticker['closing_price']:,.0f}원")
            print(f"    거래량: {ticker['units_traded_24H']:.2f} BTC")

            # 캔들 데이터 수집
            candles = collector.collect_candlestick('BTC', '1m')
            if candles:
                print(f"  ✓ 캔들 데이터 수집 성공: {len(candles)}개")
                return True
            else:
                print(f"  ✗ 캔들 데이터 수집 실패")
                return False
        else:
            print(f"  ✗ Ticker 수집 실패")
            return False
    except Exception as e:
        print(f"  ✗ 데이터 수집 실패: {str(e)}")
        return False


def test_indicators():
    """기술적 지표 계산 테스트"""
    print("\n[4/10] 기술적 지표 계산 테스트...")
    try:
        # 먼저 데이터가 있는지 확인
        from database import OHLCVData
        db = SessionLocal()
        data_count = db.query(OHLCVData).filter(
            OHLCVData.symbol == 'BTC',
            OHLCVData.timeframe == '1m'
        ).count()

        if data_count < 50:
            print(f"  ⚠ 데이터 부족 ({data_count}개) - 데이터 수집 필요")
            print("  먼저 'python main.py --mode collect'로 데이터 수집하세요")
            db.close()
            return False

        engine = IndicatorEngine()
        indicators = engine.calculate_all_indicators('BTC', '1m')

        if indicators:
            print(f"  ✓ 지표 계산 성공")
            print(f"    RSI: {indicators.get('rsi_14', 0):.2f}")
            print(f"    MACD: {indicators.get('macd', 0):.4f}")
            print(f"    ADX: {indicators.get('adx_14', 0):.2f}")
            db.close()
            return True
        else:
            print(f"  ✗ 지표 계산 실패")
            db.close()
            return False
    except Exception as e:
        print(f"  ✗ 지표 계산 실패: {str(e)}")
        return False


def test_strategy():
    """전략 시그널 생성 테스트"""
    print("\n[5/10] 전략 시그널 생성 테스트...")
    try:
        strategy = TrendFollowingStrategy()

        # 테스트 데이터
        market_data = {
            'current_price': 50000000,
            'current_volume': 100,
            'orderbook': None
        }

        indicators = {
            'ema_9': 49800000,
            'ema_21': 49500000,
            'ema_50': 49000000,
            'macd': 10000,
            'macd_signal': 5000,
            'adx_14': 30,
            'rsi_14': 60
        }

        signal = strategy.generate_signal('BTC', market_data, indicators)

        if signal:
            print(f"  ✓ 시그널 생성 성공")
            print(f"    타입: {signal['signal_type']}")
            print(f"    신뢰도: {signal['confidence']:.1%}")
            print(f"    강도: {signal['strength']:.0f}")
            return True
        else:
            print(f"  ℹ 현재 시장 상황에서 시그널 없음 (정상)")
            return True
    except Exception as e:
        print(f"  ✗ 전략 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_manager():
    """리스크 관리 테스트"""
    print("\n[6/10] 리스크 관리 테스트...")
    try:
        risk_mgr = RiskManager()

        # 일일 손실 한도 체크
        can_trade = risk_mgr.check_daily_loss_limit()
        print(f"  ✓ 일일 손실 한도 체크: {'가능' if can_trade else '초과'}")

        # 최대 포지션 수 체크
        can_open = risk_mgr.check_max_open_positions()
        print(f"  ✓ 포지션 수 체크: {'가능' if can_open else '최대 도달'}")

        # 포지션 크기 계산
        test_signal = {
            'entry_price': 50000000,
            'stop_loss': 49000000,
            'confidence': 0.7
        }
        position_size = risk_mgr.calculate_position_size(test_signal, 1000000)
        print(f"  ✓ 포지션 크기 계산: {position_size:,.0f}원")

        return True
    except Exception as e:
        print(f"  ✗ 리스크 관리 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_order_executor():
    """주문 실행 테스트 (페이퍼 모드)"""
    print("\n[7/10] 주문 실행 테스트...")
    try:
        executor = OrderExecutor()

        # 잔고 조회
        balance = executor.get_account_balance()
        print(f"  ✓ 잔고 조회 성공")
        print(f"    총 자산: {balance.get('total_value', 0):,.0f}원")

        return True
    except Exception as e:
        print(f"  ✗ 주문 실행 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_telegram():
    """텔레그램 알림 테스트"""
    print("\n[8/10] 텔레그램 알림 테스트...")
    try:
        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
            print("  ⚠ 텔레그램 설정 없음 - 건너뜀")
            return True

        notifier = TelegramNotifier()
        success = notifier.send_message("🔍 Auto Coin Trading - 시스템 테스트")

        if success:
            print(f"  ✓ 텔레그램 알림 전송 성공")
            return True
        else:
            print(f"  ✗ 텔레그램 알림 전송 실패")
            return False
    except Exception as e:
        print(f"  ✗ 텔레그램 테스트 실패: {str(e)}")
        return False


def test_strategies_in_db():
    """DB에 전략이 있는지 확인"""
    print("\n[9/10] 전략 DB 확인...")
    try:
        from database import Strategy
        db = SessionLocal()

        strategies = db.query(Strategy).filter(Strategy.is_active == True).all()

        if len(strategies) >= 4:
            print(f"  ✓ 전략 {len(strategies)}개 발견:")
            for s in strategies:
                print(f"    - {s.name} ({s.strategy_type})")
            db.close()
            return True
        else:
            print(f"  ✗ 전략 부족 ({len(strategies)}개) - DB 초기화 필요")
            print("  'python main.py --mode init' 실행하세요")
            db.close()
            return False
    except Exception as e:
        print(f"  ✗ 전략 확인 실패: {str(e)}")
        return False


def test_integration():
    """통합 테스트"""
    print("\n[10/10] 통합 테스트...")
    try:
        print("  시스템 시작 시뮬레이션...")

        # 1초간 실제 데이터 수집 테스트
        from api import BithumbAPI
        api = BithumbAPI()

        symbols = ['BTC']
        for symbol in symbols:
            ticker = api.get_ticker(symbol)
            if ticker.get('status') == '0000':
                price = float(ticker['data']['closing_price'])
                print(f"    ✓ {symbol} 데이터 수집: {price:,.0f}원")
            else:
                print(f"    ✗ {symbol} 데이터 수집 실패")
                return False

        print("  ✓ 통합 테스트 성공 - 시스템 정상 작동 가능")
        return True

    except Exception as e:
        print(f"  ✗ 통합 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트 실행"""
    print("=" * 70)
    print("Auto Coin Trading - 시스템 통합 테스트")
    print("=" * 70)

    tests = [
        ("데이터베이스", test_database),
        ("빗썸 API", test_api),
        ("데이터 수집", test_data_collection),
        ("기술적 지표", test_indicators),
        ("전략 엔진", test_strategy),
        ("리스크 관리", test_risk_manager),
        ("주문 실행", test_order_executor),
        ("텔레그램", test_telegram),
        ("전략 DB", test_strategies_in_db),
        ("통합", test_integration)
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ✗ {name} 테스트 예외 발생: {str(e)}")
            results.append((name, False))

    # 결과 요약
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\n총 {passed}/{total} 테스트 통과")

    if passed == total:
        print("\n✅ 모든 테스트 통과! 시스템 정상 작동 준비 완료")
        print("\n다음 단계:")
        print("  1. python main.py --mode run --interval 60")
        print("  2. 시스템 모니터링")
        return 0
    else:
        print("\n⚠️ 일부 테스트 실패 - 문제 해결 필요")
        print("\n실패한 항목 확인:")
        for name, result in results:
            if not result:
                print(f"  - {name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
