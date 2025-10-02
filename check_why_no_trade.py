"""
왜 시그널이 있는데 매매가 안 되는지 확인
"""

from database import SessionLocal, TradingSignal
from core.risk_manager import RiskManager
from core.order_executor import OrderExecutor
from datetime import datetime, timedelta

db = SessionLocal()

# 최근 10분 시그널
recent = datetime.now() - timedelta(minutes=10)
recent_signals = db.query(TradingSignal).filter(
    TradingSignal.timestamp >= recent
).order_by(TradingSignal.timestamp.desc()).limit(5).all()

print("=" * 70)
print("시그널이 있는데 왜 매매가 안 되는지 분석")
print("=" * 70)

print(f"\n최근 10분 시그널: {len(recent_signals)}개")

if recent_signals:
    for i, sig in enumerate(recent_signals, 1):
        print(f"\n[시그널 {i}] {sig.symbol} - {sig.signal_type}")
        print(f"  시간: {sig.timestamp}")
        print(f"  신뢰도: {float(sig.confidence):.1%}")
        print(f"  강도: {float(sig.strength)}")
        print(f"  진입가: {float(sig.entry_price):,.0f}원")

# 계좌 확인
executor = OrderExecutor()
balance = executor.get_account_balance()

print(f"\n계좌 상태:")
print(f"  총 자산: {balance.get('total_value', 0):,.0f}원")
print(f"  가용 KRW: {balance.get('available_krw', 0):,.0f}원")

available = balance.get('available_krw', 0)

# 리스크 매니저 확인
risk_manager = RiskManager()

print(f"\n리스크 검증:")
daily_ok = risk_manager.check_daily_loss_limit()
position_ok = risk_manager.check_max_open_positions()

print(f"  일일 손실 한도: {'PASS' if daily_ok else 'FAIL'}")
print(f"  최대 포지션 수: {'PASS' if position_ok else 'FAIL'}")
print(f"  최소 주문금액(10,000원): {'PASS' if available >= 10000 else 'FAIL'}")

# 최근 시그널로 테스트
if recent_signals:
    test_signal = {
        'signal_type': recent_signals[0].signal_type,
        'entry_price': float(recent_signals[0].entry_price),
        'stop_loss': float(recent_signals[0].stop_loss),
        'take_profit': float(recent_signals[0].take_profit),
        'confidence': float(recent_signals[0].confidence),
        'strength': float(recent_signals[0].strength)
    }

    is_valid, reason = risk_manager.validate_signal_risk(test_signal, available)

    print(f"\n시그널 검증 테스트:")
    print(f"  테스트 대상: {recent_signals[0].symbol}")
    print(f"  결과: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"  실패 이유: {reason}")
    else:
        position_size = risk_manager.calculate_position_size(test_signal, available)
        print(f"  계산된 포지션 크기: {position_size:,.0f}원")

        # R/R 비율
        entry = test_signal['entry_price']
        sl = test_signal['stop_loss']
        tp = test_signal['take_profit']

        loss_dist = abs(entry - sl)
        profit_dist = abs(tp - entry)
        rr = profit_dist / loss_dist if loss_dist > 0 else 0

        print(f"  R/R 비율: {rr:.2f} (최소 1.2 필요)")

print("\n" + "=" * 70)

db.close()
