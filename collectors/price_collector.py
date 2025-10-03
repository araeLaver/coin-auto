"""
OHLCV 가격 데이터 수집 모듈
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict
from decimal import Decimal
from api import BithumbAPI
from database import SessionLocal, OHLCVData, SystemLog
import config


class PriceCollector:
    """가격 데이터 수집"""

    def __init__(self):
        self.api = BithumbAPI()
        self.db = SessionLocal()
        self.timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']

    def collect_ticker(self, symbol: str) -> Dict:
        """현재가 정보 수집"""
        try:
            response = self.api.get_ticker(symbol)

            if response.get('status') == '0000':
                data = response['data']
                return {
                    'symbol': symbol,
                    'timestamp': datetime.now(),
                    'opening_price': float(data.get('opening_price', 0)),
                    'closing_price': float(data.get('closing_price', 0)),
                    'min_price': float(data.get('min_price', 0)),
                    'max_price': float(data.get('max_price', 0)),
                    'units_traded': float(data.get('units_traded', 0)),
                    'acc_trade_value': float(data.get('acc_trade_value', 0)),
                    'prev_closing_price': float(data.get('prev_closing_price', 0)),
                    'units_traded_24H': float(data.get('units_traded_24H', 0)),
                    'acc_trade_value_24H': float(data.get('acc_trade_value_24H', 0)),
                    'fluctate_24H': float(data.get('fluctate_24H', 0)),
                    'fluctate_rate_24H': float(data.get('fluctate_rate_24H', 0)),
                }
            return None

        except Exception as e:
            self._log_error(f"Ticker 수집 에러: {symbol} - {str(e)}")
            return None

    def collect_candlestick(self, symbol: str, interval: str = '1m') -> List[Dict]:
        """캔들스틱 데이터 수집"""
        try:
            # 빗썸 API interval 매핑
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '10m',  # 빗썸은 10m 지원
                '1h': '1h',
                '4h': '6h',    # 빗썸은 6h 지원
                '1d': '24h'
            }

            api_interval = interval_map.get(interval, '1m')
            response = self.api.get_candlestick(symbol, api_interval)

            if response.get('status') == '0000':
                candles = response.get('data', [])
                result = []

                for candle in candles:
                    result.append({
                        'symbol': symbol,
                        'timeframe': interval,
                        'timestamp': datetime.fromtimestamp(int(candle[0]) / 1000),
                        'open': float(candle[1]),
                        'close': float(candle[2]),
                        'high': float(candle[3]),
                        'low': float(candle[4]),
                        'volume': float(candle[5])
                    })

                return result

            return []

        except Exception as e:
            self._log_error(f"Candlestick 수집 에러: {symbol} {interval} - {str(e)}")
            return []

    def save_ohlcv(self, candle_data: Dict):
        """OHLCV 데이터 저장"""
        from sqlalchemy.exc import IntegrityError

        try:
            # 기존 데이터 확인
            existing = self.db.query(OHLCVData).filter(
                OHLCVData.symbol == candle_data['symbol'],
                OHLCVData.timeframe == candle_data['timeframe'],
                OHLCVData.timestamp == candle_data['timestamp']
            ).first()

            if existing:
                # 업데이트
                existing.open = Decimal(str(candle_data['open']))
                existing.high = Decimal(str(candle_data['high']))
                existing.low = Decimal(str(candle_data['low']))
                existing.close = Decimal(str(candle_data['close']))
                existing.volume = Decimal(str(candle_data['volume']))
            else:
                # 신규 삽입
                ohlcv = OHLCVData(
                    symbol=candle_data['symbol'],
                    timeframe=candle_data['timeframe'],
                    timestamp=candle_data['timestamp'],
                    open=Decimal(str(candle_data['open'])),
                    high=Decimal(str(candle_data['high'])),
                    low=Decimal(str(candle_data['low'])),
                    close=Decimal(str(candle_data['close'])),
                    volume=Decimal(str(candle_data['volume']))
                )
                self.db.add(ohlcv)

            self.db.commit()

        except IntegrityError as e:
            # UniqueViolation 에러 무시 (동시성 문제)
            self.db.rollback()
        except Exception as e:
            self.db.rollback()
            self._log_error(f"OHLCV 저장 실패: {str(e)}")

    def run_collection_loop(self, symbols: List[str], interval: int = None):
        """지속적인 가격 데이터 수집"""
        interval = interval or config.PRICE_INTERVAL

        print(f"가격 데이터 수집 시작: {symbols}, 주기: {interval}초")

        while True:
            try:
                for symbol in symbols:
                    # Ticker 정보 수집
                    ticker = self.collect_ticker(symbol)
                    if ticker:
                        print(f"[{symbol}] 현재가: {ticker['closing_price']:,.0f}원, "
                              f"24h 변동: {ticker['fluctate_rate_24H']:.2f}%")

                    # 캔들 데이터 수집
                    for tf in self.timeframes:
                        candles = self.collect_candlestick(symbol, tf)
                        for candle in candles[-1:]:  # 최신 1개만 저장
                            self.save_ohlcv(candle)

                time.sleep(interval)

            except KeyboardInterrupt:
                print("\n수집 중단됨")
                break
            except Exception as e:
                self._log_error(f"수집 루프 에러: {str(e)}")
                time.sleep(interval)

    def _log_error(self, message: str):
        """에러 로그 기록"""
        print(f"ERROR: {message}")
        try:
            log = SystemLog(
                log_level='ERROR',
                module='PriceCollector',
                message=message
            )
            self.db.add(log)
            self.db.commit()
        except:
            pass

    def __del__(self):
        """소멸자"""
        self.db.close()


if __name__ == "__main__":
    collector = PriceCollector()
    collector.run_collection_loop(config.TARGET_PAIRS)
