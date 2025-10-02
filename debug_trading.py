"""
자동매매 디버깅 스크립트
왜 시그널이 있는데 매수가 안 되는지 확인
"""

from database import SessionLocal, TradingSignal
from core.risk_manager import RiskManager
from core.order_executor import OrderExecutor
from datetime import datetime, timedelta

db = SessionLocal()

print("=" * 70)
print("자동매매 디버깅")
print("=" * 70)

# 1. 최근 시그널 확인
print("\n1. 최근 30분 시그널:")
recent_time = datetime.now() - timedelta(minutes=30)
recent_signals = db.query(TradingSignal).filter(
    TradingSignal.timestamp >= recent_time
).order_by(TradingSignal.timestamp.desc()).limit(10).all()

print(f"   총 {len(recent_signals)}개 시그널 발견\n")

if recent_signals:
    for sig in recent_signals[:5]:
        print(f"   {sig.symbol} - {sig.signal_type}")
        print(f"   전략: {sig.strategy_id}")
        print(f"   신뢰도: {float(sig.confidence):.1%}")
        print(f"   강도: {float(sig.strength)}")
        print(f"   진입가: {float(sig.entry_price):,.0f}원")
        print()

# 2. 계좌 잔고 확인
print("2. 계좌 잔고:")
executor = OrderExecutor()
balance = executor.get_account_balance()

print(f"   총 자산: {balance.get('total_value', 0):,.0f}원")
print(f"   가용 KRW: {balance.get('available_krw', 0):,.0f}원")
print(f"   코인 평가액: {balance.get('total_crypto_value', 0):,.0f}원")

available = balance.get('available_krw', 0)
meets_min = "OK" if available >= 10000 else "FAIL"
print(f"\n   최소 주문금액(10,000원) 충족: {meets_min}")

# 3. 리스크 검증 테스트
print("\n3. 리스크 검증 테스트:")
risk_manager = RiskManager()

if recent_signals:
    test_signal = {
        'signal_type': recent_signals[0].signal_type,
        'entry_price': float(recent_signals[0].entry_price),
        'stop_loss': float(recent_signals[0].stop_loss),
        'take_profit': float(recent_signals[0].take_profit),
        'confidence': float(recent_signals[0].confidence),
        'strength': float(recent_signals[0].strength)
    }

    print(f"   테스트 시그널: {recent_signals[0].symbol}")

    # 일일 손실 한도 체크
    daily_ok = risk_manager.check_daily_loss_limit()
    daily_status = "PASS" if daily_ok else "FAIL"
    print(f"   일일 손실 한도: {daily_status}")

    # 최대 포지션 수 체크
    position_ok = risk_manager.check_max_open_positions()
    position_status = "PASS" if position_ok else "FAIL"
    print(f"   최대 포지션 수: {position_status}")

    # 시그널 리스크 검증
    is_valid, reason = risk_manager.validate_signal_risk(test_signal, available)
    signal_status = "PASS" if is_valid else "FAIL"
    print(f"   시그널 검증: {signal_status}")
    if not is_valid:
        print(f"   실패 이유: {reason}")

    # 포지션 크기 계산
    if is_valid:
        position_size = risk_manager.calculate_position_size(test_signal, available)
        print(f"   계산된 포지션 크기: {position_size:,.0f}원")

    # 리스크/보상 비율 계산
    entry = test_signal['entry_price']
    sl = test_signal['stop_loss']
    tp = test_signal['take_profit']

    loss_distance = abs(entry - sl)
    profit_distance = abs(tp - entry)
    rr_ratio = profit_distance / loss_distance if loss_distance > 0 else 0

    print(f"\n   리스크/보상 비율: {rr_ratio:.2f}")
    print(f"   손절 거리: {loss_distance:,.0f}원 ({loss_distance/entry*100:.2f}%)")
    print(f"   익절 거리: {profit_distance:,.0f}원 ({profit_distance/entry*100:.2f}%)")
    rr_status = "PASS" if rr_ratio >= 1.2 else "FAIL"
    print(f"   최소 요구: 1.2 - {rr_status}")

# 4. 현재 설정
print("\n4. 현재 시스템 설정:")
import config
print(f"   모드: {config.TRADE_MODE}")
print(f"   최대 포지션 크기: {config.MAX_POSITION_SIZE * 100}%")
print(f"   최대 동시 포지션: {config.MAX_OPEN_POSITIONS}개")
print(f"   손절: {config.STOP_LOSS_PERCENT * 100}%")
print(f"   익절: {config.TAKE_PROFIT_PERCENT * 100}%")
print(f"   일일 손실 한도: {config.MAX_DAILY_LOSS * 100}%")

print("\n" + "=" * 70)
print("디버깅 완료")
print("=" * 70)

db.close()
