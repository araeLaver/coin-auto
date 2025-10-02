"""
빠른 데이터 수집 - 우선순위 코인만
"""

import time
from datetime import datetime
from api.bithumb_client import BithumbAPI
from database import SessionLocal, OHLCVData
from decimal import Decimal
import config

api = BithumbAPI()
db = SessionLocal()

# 우선순위 코인만 (14개)
symbols = config.PRIORITY_PAIRS

print(f"우선순위 코인 {len(symbols)}개 데이터 수집 중...")

total = 0
for symbol in symbols:
    for tf in ['1m', '5m', '15m']:
        try:
            result = api.get_candlestick(symbol, tf)

            if result.get('status') == '0000':
                candles = result['data']
                saved = 0

                for candle in candles[:50]:  # 최근 50개
                    try:
                        timestamp = datetime.fromtimestamp(int(candle[0]) / 1000)

                        # 중복 체크
                        exists = db.query(OHLCVData).filter(
                            OHLCVData.symbol == symbol,
                            OHLCVData.timeframe == tf,
                            OHLCVData.timestamp == timestamp
                        ).first()

                        if not exists:
                            ohlcv = OHLCVData(
                                symbol=symbol,
                                timeframe=tf,
                                timestamp=timestamp,
                                open=Decimal(str(candle[1])),
                                high=Decimal(str(candle[3])),
                                low=Decimal(str(candle[4])),
                                close=Decimal(str(candle[2])),
                                volume=Decimal(str(candle[5]))
                            )
                            db.add(ohlcv)
                            saved += 1
                    except:
                        continue

                db.commit()
                print(f"  {symbol} {tf}: {saved}개")
                total += saved

        except Exception as e:
            print(f"  {symbol} {tf} 실패: {e}")

        time.sleep(0.3)

db.close()

print(f"\n총 {total}개 캔들 수집 완료!")
