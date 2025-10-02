from database import SessionLocal, TradingSignal, Position, OHLCVData
from datetime import datetime, timedelta

db = SessionLocal()

# 최근 30분
recent = datetime.now() - timedelta(minutes=30)

signals_count = db.query(TradingSignal).filter(TradingSignal.timestamp >= recent).count()
positions_count = db.query(Position).filter(Position.status == 'OPEN').count()
ohlcv_count = db.query(OHLCVData).filter(OHLCVData.created_at >= recent).count()

print(f'\n최근 30분 상태:')
print(f'  시그널: {signals_count}개')
print(f'  오픈 포지션: {positions_count}개')
print(f'  수집된 OHLCV: {ohlcv_count}개')

# 최신 OHLCV
latest_ohlcv = db.query(OHLCVData).order_by(OHLCVData.created_at.desc()).first()
if latest_ohlcv:
    print(f'  최신 데이터: {latest_ohlcv.symbol} at {latest_ohlcv.created_at}')

# 최신 시그널 (전체)
latest_signal = db.query(TradingSignal).order_by(TradingSignal.timestamp.desc()).first()
if latest_signal:
    print(f'\n최신 시그널: {latest_signal.symbol} - {latest_signal.signal_type}')
    print(f'  시간: {latest_signal.timestamp}')
    print(f'  신뢰도: {float(latest_signal.confidence):.1%}')

# 전체 데이터 통계
total_ohlcv = db.query(OHLCVData).count()
total_signals = db.query(TradingSignal).count()
total_positions = db.query(Position).count()

print(f'\n전체 통계:')
print(f'  총 OHLCV: {total_ohlcv}개')
print(f'  총 시그널: {total_signals}개')
print(f'  총 포지션: {total_positions}개')

db.close()
