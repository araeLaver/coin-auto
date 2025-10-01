"""
빗썸 API 연동 테스트
실제 계정 잔고 및 API 키 유효성 확인
"""

import sys
import os

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from api import BithumbAPI
import config

def test_api_connection():
    """API 연결 및 키 유효성 테스트"""
    print("=" * 70)
    print("빗썸 API 연동 테스트")
    print("=" * 70)

    api = BithumbAPI()

    # 1. 공개 API 테스트 (티커 조회)
    print("\n[1/4] 공개 API 테스트 (현재가 조회)...")
    try:
        ticker = api.get_ticker('BTC')
        if ticker.get('status') == '0000':
            price = float(ticker['data']['closing_price'])
            print(f"  ✓ BTC 현재가: {price:,.0f}원")
        else:
            print(f"  ✗ 오류: {ticker.get('message')}")
            return False
    except Exception as e:
        print(f"  ✗ 예외 발생: {str(e)}")
        return False

    # 2. 개인 정보 API 테스트 (잔고 조회)
    print("\n[2/4] 개인 API 테스트 (잔고 조회)...")
    try:
        balance = api.get_balance('BTC')

        if balance.get('status') == '0000':
            data = balance['data']
            krw = float(data.get('total_krw', 0))
            btc = float(data.get('total_btc', 0))
            available_krw = float(data.get('available_krw', 0))

            print(f"  ✓ API 인증 성공!")
            print(f"  ✓ 보유 KRW: {krw:,.0f}원")
            print(f"  ✓ 사용 가능 KRW: {available_krw:,.0f}원")
            print(f"  ✓ 보유 BTC: {btc:.8f} BTC")

            if available_krw < 5000:
                print(f"\n  ⚠️ 경고: 사용 가능 잔고가 5,000원 미만입니다.")
                print(f"  ⚠️ 최소 5,000원 이상 입금을 권장합니다.")
        else:
            error_msg = balance.get('message', 'Unknown error')
            print(f"  ✗ API 인증 실패: {error_msg}")
            print(f"\n  가능한 원인:")
            print(f"  - API 키가 잘못되었습니다")
            print(f"  - API 키 권한 설정이 잘못되었습니다 (자산조회 권한 필요)")
            print(f"  - API 키가 비활성화되었습니다")
            return False

    except Exception as e:
        print(f"  ✗ 예외 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # 3. 거래 가능 여부 확인
    print("\n[3/4] 거래 가능 여부 확인...")
    try:
        if available_krw >= 5000:
            print(f"  ✓ 거래 가능 (최소 5,000원 이상)")
        else:
            print(f"  ⚠️ 거래 불가 (잔고 부족: {available_krw:,.0f}원)")
            print(f"  최소 5,000원 이상 필요합니다.")
    except:
        print(f"  ⚠️ 잔고 확인 불가")

    # 4. 설정 확인
    print("\n[4/4] 거래 설정 확인...")
    print(f"  거래 모드: {config.TRADE_MODE}")
    print(f"  초기 자본: {config.INITIAL_CAPITAL:,.0f}원")
    print(f"  최대 포지션 크기: {config.MAX_POSITION_SIZE * 100:.0f}%")
    print(f"  손절 비율: {config.STOP_LOSS_PERCENT * 100:.0f}%")
    print(f"  익절 비율: {config.TAKE_PROFIT_PERCENT * 100:.0f}%")
    print(f"  일일 최대 손실: {config.MAX_DAILY_LOSS * 100:.0f}%")

    if config.TRADE_MODE == 'live':
        print(f"\n  ⚠️⚠️⚠️ 실전 모드 활성화됨 ⚠️⚠️⚠️")
        print(f"  실제 자금이 거래됩니다!")
    else:
        print(f"\n  ℹ️ 페이퍼 트레이딩 모드")
        print(f"  실제 거래는 실행되지 않습니다.")

    print("\n" + "=" * 70)
    print("✅ 모든 API 테스트 통과!")
    print("=" * 70)

    print("\n다음 단계:")
    print("  1. python main.py --mode init     # DB 초기화")
    print("  2. python test_system.py          # 시스템 통합 테스트")
    print("  3. python main.py --mode run      # 자동매매 시작")

    if config.TRADE_MODE == 'live':
        print("\n⚠️ 주의사항:")
        print("  - 소액(5만원 이하)으로 먼저 테스트하세요")
        print("  - 시스템을 모니터링하세요")
        print("  - 손실이 발생할 수 있습니다")

    return True


if __name__ == "__main__":
    try:
        success = test_api_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
        sys.exit(1)
    except Exception as e:
        print(f"\n예상치 못한 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
