from database import SessionLocal, OHLCVData, TechnicalIndicator
from datetime import datetime, timedelta

db = SessionLocal()
recent = datetime.now() - timedelta(minutes=10)

ohlcv = db.query(OHLCVData).filter(OHLCVData.created_at >= recent).count()
indicators = db.query(TechnicalIndicator).filter(TechnicalIndicator.created_at >= recent).count()

print(f'OHLCV records (last 10min): {ohlcv}')
print(f'Indicator records (last 10min): {indicators}')

latest_ohlcv = db.query(OHLCVData).order_by(OHLCVData.created_at.desc()).first()
if latest_ohlcv:
    print(f'Latest OHLCV: {latest_ohlcv.symbol} at {latest_ohlcv.timestamp} (created: {latest_ohlcv.created_at})')

latest_indicator = db.query(TechnicalIndicator).order_by(TechnicalIndicator.created_at.desc()).first()
if latest_indicator:
    print(f'Latest Indicator: {latest_indicator.symbol} at {latest_indicator.timestamp}')

db.close()
