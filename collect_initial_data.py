"""
초기 데이터 수집 스크립트
자동매매 시작 전에 최소 1시간 데이터 수집
"""

import time
from datetime import datetime, timedelta
from api.bithumb_client import BithumbAPI
from database import SessionLocal, OHLCVData
from decimal import Decimal
import config

def collect_historical_candles(symbol, timeframe='1m', limit=60):
    """
    과거 캔들 데이터 수집
    빗썸은 candlestick API로 최근 데이터 가져오기
    """
    api = BithumbAPI()
    db = SessionLocal()

    print(f"\n[{symbol}] {timeframe} 캔들 수집 중...")

    try:
        # 빗썸 candlestick API 호출
        result = api.get_candlestick(symbol, timeframe)

        if result.get('status') == '0000':
            candles = result.get('data', [])

            saved_count = 0
            for candle in candles[:limit]:
                try:
                    timestamp = datetime.fromtimestamp(int(candle[0]) / 1000)

                    # 중복 체크
                    exists = db.query(OHLCVData).filter(
                        OHLCVData.symbol == symbol,
                        OHLCVData.timeframe == timeframe,
                        OHLCVData.timestamp == timestamp
                    ).first()

                    if not exists:
                        ohlcv = OHLCVData(
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=timestamp,
                            open=Decimal(str(candle[1])),
                            high=Decimal(str(candle[3])),
                            low=Decimal(str(candle[4])),
                            close=Decimal(str(candle[2])),
                            volume=Decimal(str(candle[5]))
                        )
                        db.add(ohlcv)
                        saved_count += 1
                except Exception as e:
                    print(f"  캔들 저장 에러: {e}")
                    continue

            db.commit()
            print(f"  ✓ {saved_count}개 캔들 저장")
            return saved_count
        else:
            print(f"  ✗ API 에러: {result.get('message')}")
            return 0

    except Exception as e:
        print(f"  ✗ 수집 실패: {e}")
        return 0
    finally:
        db.close()


def collect_realtime_data():
    """실시간 데이터 수집 (1분봉)"""
    api = BithumbAPI()
    db = SessionLocal()

    print("\n실시간 1분봉 수집 시작...")

    for symbol in config.TARGET_PAIRS:
        try:
            ticker = api.get_ticker(symbol)

            if ticker.get('status') == '0000':
                data = ticker['data']

                # 현재 시간 (분 단위로 정규화)
                now = datetime.now()
                timestamp = now.replace(second=0, microsecond=0)

                # 중복 체크
                exists = db.query(OHLCVData).filter(
                    OHLCVData.symbol == symbol,
                    OHLCVData.timeframe == '1m',
                    OHLCVData.timestamp == timestamp
                ).first()

                if not exists:
                    price = Decimal(str(data.get('closing_price', 0)))
                    volume = Decimal(str(data.get('units_traded_24H', 0)))

                    ohlcv = OHLCVData(
                        symbol=symbol,
                        timeframe='1m',
                        timestamp=timestamp,
                        open=price,
                        high=price,
                        low=price,
                        close=price,
                        volume=volume
                    )
                    db.add(ohlcv)
                    print(f"  [{symbol}] {timestamp} - {price}")

        except Exception as e:
            print(f"  [{symbol}] 에러: {e}")

    db.commit()
    db.close()


def main():
    print("=" * 70)
    print("초기 데이터 수집 시작")
    print("=" * 70)

    # 1. 과거 데이터 수집 (각 타임프레임별)
    timeframes = ['1m', '5m', '15m', '1h']
    limits = {'1m': 100, '5m': 100, '15m': 100, '1h': 50}

    total_saved = 0

    for symbol in config.TARGET_PAIRS:
        for tf in timeframes:
            count = collect_historical_candles(symbol, tf, limits[tf])
            total_saved += count
            time.sleep(0.5)  # API 제한 방지

    print(f"\n총 {total_saved}개 캔들 수집 완료")

    # 2. 실시간 수집 10분간
    print("\n실시간 데이터 10분간 수집...")

    for i in range(10):
        print(f"\n[{i+1}/10분]")
        collect_realtime_data()

        if i < 9:
            print("60초 대기...")
            time.sleep(60)

    print("\n" + "=" * 70)
    print("✓ 데이터 수집 완료!")
    print("이제 자동매매를 시작할 수 있습니다: python main.py --mode run")
    print("=" * 70)


if __name__ == "__main__":
    main()
