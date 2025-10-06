"""
기술적 지표 계산 엔진
TA-Lib 및 pandas_ta 활용
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from decimal import Decimal
from datetime import datetime, timedelta
from database import SessionLocal, OHLCVData, TechnicalIndicator
import config

# TA 라이브러리
try:
    import ta
except ImportError:
    print("Warning: 'ta' library not installed. Run: pip install ta")


class IndicatorEngine:
    """기술적 지표 계산 엔진"""

    def __init__(self):
        self.db = SessionLocal()

    def get_ohlcv_data(self, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """
        데이터베이스에서 OHLCV 데이터 조회
        Args:
            symbol: 코인 심볼
            timeframe: 타임프레임
            limit: 조회할 캔들 개수
        Returns:
            DataFrame
        """
        try:
            query = self.db.query(OHLCVData).filter(
                OHLCVData.symbol == symbol,
                OHLCVData.timeframe == timeframe
            ).order_by(OHLCVData.timestamp.desc()).limit(limit)

            data = query.all()

            if not data:
                return pd.DataFrame()

            df = pd.DataFrame([{
                'timestamp': d.timestamp,
                'open': float(d.open),
                'high': float(d.high),
                'low': float(d.low),
                'close': float(d.close),
                'volume': float(d.volume)
            } for d in data])

            df = df.sort_values('timestamp').reset_index(drop=True)
            return df

        except Exception as e:
            print(f"OHLCV 조회 실패: {str(e)}")
            return pd.DataFrame()

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """RSI (Relative Strength Index) 계산"""
        if len(df) < period:
            return pd.Series([None] * len(df))

        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD 계산"""
        if len(df) < slow:
            return {'macd': None, 'signal': None, 'histogram': None}

        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }

    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict:
        """볼린저 밴드 계산"""
        if len(df) < period:
            return {'upper': None, 'middle': None, 'lower': None}

        middle = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }

    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """EMA (Exponential Moving Average) 계산"""
        if len(df) < period:
            return pd.Series([None] * len(df))

        return df['close'].ewm(span=period, adjust=False).mean()

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ATR (Average True Range) 계산"""
        if len(df) < period + 1:
            return pd.Series([None] * len(df))

        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ADX (Average Directional Index) 계산"""
        if len(df) < period + 1:
            return pd.Series([None] * len(df))

        # +DM, -DM 계산
        high_diff = df['high'].diff()
        low_diff = -df['low'].diff()

        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        # ATR 계산
        atr = self.calculate_atr(df, period)

        # +DI, -DI 계산
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # DX, ADX 계산
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx

    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict:
        """스토캐스틱 계산"""
        if len(df) < k_period:
            return {'k': None, 'd': None}

        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()

        k = 100 * (df['close'] - low_min) / (high_max - low_min)
        d = k.rolling(window=d_period).mean()

        return {'k': k, 'd': d}

    def calculate_all_indicators(self, symbol: str, timeframe: str) -> Dict:
        """
        모든 지표 계산
        Args:
            symbol: 코인 심볼
            timeframe: 타임프레임
        Returns:
            계산된 지표 딕셔너리
        """
        df = self.get_ohlcv_data(symbol, timeframe, limit=200)

        if df.empty or len(df) < 50:
            print(f"데이터 부족: {symbol} {timeframe}")
            return None

        try:
            # RSI
            rsi = self.calculate_rsi(df, 14)

            # MACD
            macd_data = self.calculate_macd(df)

            # 볼린저 밴드
            bb_data = self.calculate_bollinger_bands(df)

            # EMA
            ema_9 = self.calculate_ema(df, 9)
            ema_21 = self.calculate_ema(df, 21)
            ema_50 = self.calculate_ema(df, 50)
            ema_200 = self.calculate_ema(df, 200)

            # 거래량 이동평균
            volume_sma = df['volume'].rolling(window=20).mean()

            # ATR
            atr = self.calculate_atr(df, 14)

            # ADX
            adx = self.calculate_adx(df, 14)

            # 스토캐스틱
            stoch_data = self.calculate_stochastic(df)

            # 최신 값 추출
            latest_idx = -1

            # 가격 변동률 계산 (급등 감지용)
            price_change_5m = (df.iloc[-1]['close'] - df.iloc[-5]['close']) / df.iloc[-5]['close'] if len(df) >= 5 else 0
            price_change_15m = (df.iloc[-1]['close'] - df.iloc[-15]['close']) / df.iloc[-15]['close'] if len(df) >= 15 else 0

            # 볼린저밴드 포지션 (0~1, 0.5=중간)
            current_price = df.iloc[-1]['close']
            bb_range = bb_data['upper'].iloc[-1] - bb_data['lower'].iloc[-1] if pd.notna(bb_data['upper'].iloc[-1]) else 1
            bb_position = (current_price - bb_data['lower'].iloc[-1]) / bb_range if bb_range > 0 and pd.notna(bb_data['lower'].iloc[-1]) else 0.5

            indicators = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': df.iloc[latest_idx]['timestamp'],
                'rsi_14': float(rsi.iloc[latest_idx]) if pd.notna(rsi.iloc[latest_idx]) else None,
                'macd': float(macd_data['macd'].iloc[latest_idx]) if pd.notna(macd_data['macd'].iloc[latest_idx]) else None,
                'macd_signal': float(macd_data['signal'].iloc[latest_idx]) if pd.notna(macd_data['signal'].iloc[latest_idx]) else None,
                'macd_histogram': float(macd_data['histogram'].iloc[latest_idx]) if pd.notna(macd_data['histogram'].iloc[latest_idx]) else None,
                'bb_upper': float(bb_data['upper'].iloc[latest_idx]) if pd.notna(bb_data['upper'].iloc[latest_idx]) else None,
                'bb_middle': float(bb_data['middle'].iloc[latest_idx]) if pd.notna(bb_data['middle'].iloc[latest_idx]) else None,
                'bb_lower': float(bb_data['lower'].iloc[latest_idx]) if pd.notna(bb_data['lower'].iloc[latest_idx]) else None,
                'bb_position': float(bb_position),
                'ema_9': float(ema_9.iloc[latest_idx]) if pd.notna(ema_9.iloc[latest_idx]) else None,
                'ema_21': float(ema_21.iloc[latest_idx]) if pd.notna(ema_21.iloc[latest_idx]) else None,
                'ema_50': float(ema_50.iloc[latest_idx]) if pd.notna(ema_50.iloc[latest_idx]) else None,
                'ema_200': float(ema_200.iloc[latest_idx]) if pd.notna(ema_200.iloc[latest_idx]) else None,
                'volume_sma_20': float(volume_sma.iloc[latest_idx]) if pd.notna(volume_sma.iloc[latest_idx]) else None,
                'atr_14': float(atr.iloc[latest_idx]) if pd.notna(atr.iloc[latest_idx]) else None,
                'adx_14': float(adx.iloc[latest_idx]) if pd.notna(adx.iloc[latest_idx]) else None,
                'stoch_k': float(stoch_data['k'].iloc[latest_idx]) if pd.notna(stoch_data['k'].iloc[latest_idx]) else None,
                'stoch_d': float(stoch_data['d'].iloc[latest_idx]) if pd.notna(stoch_data['d'].iloc[latest_idx]) else None,
                'price_change_5m': float(price_change_5m),
                'price_change_15m': float(price_change_15m),
            }

            return indicators

        except Exception as e:
            print(f"지표 계산 실패: {symbol} {timeframe} - {str(e)}")
            return None

    def save_indicators(self, indicators: Dict):
        """지표를 데이터베이스에 저장"""
        try:
            indicator_record = TechnicalIndicator(
                symbol=indicators['symbol'],
                timeframe=indicators['timeframe'],
                timestamp=indicators['timestamp'],
                rsi_14=Decimal(str(indicators['rsi_14'])) if indicators['rsi_14'] else None,
                macd=Decimal(str(indicators['macd'])) if indicators['macd'] else None,
                macd_signal=Decimal(str(indicators['macd_signal'])) if indicators['macd_signal'] else None,
                macd_histogram=Decimal(str(indicators['macd_histogram'])) if indicators['macd_histogram'] else None,
                bb_upper=Decimal(str(indicators['bb_upper'])) if indicators['bb_upper'] else None,
                bb_middle=Decimal(str(indicators['bb_middle'])) if indicators['bb_middle'] else None,
                bb_lower=Decimal(str(indicators['bb_lower'])) if indicators['bb_lower'] else None,
                ema_9=Decimal(str(indicators['ema_9'])) if indicators['ema_9'] else None,
                ema_21=Decimal(str(indicators['ema_21'])) if indicators['ema_21'] else None,
                ema_50=Decimal(str(indicators['ema_50'])) if indicators['ema_50'] else None,
                ema_200=Decimal(str(indicators['ema_200'])) if indicators['ema_200'] else None,
                volume_sma_20=Decimal(str(indicators['volume_sma_20'])) if indicators['volume_sma_20'] else None,
                atr_14=Decimal(str(indicators['atr_14'])) if indicators['atr_14'] else None,
                adx_14=Decimal(str(indicators['adx_14'])) if indicators['adx_14'] else None,
                stoch_k=Decimal(str(indicators['stoch_k'])) if indicators['stoch_k'] else None,
                stoch_d=Decimal(str(indicators['stoch_d'])) if indicators['stoch_d'] else None,
            )

            self.db.merge(indicator_record)
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            print(f"지표 저장 실패: {str(e)}")

    def run_calculation_loop(self, symbols: List[str], timeframes: List[str], interval: int = None):
        """지속적인 지표 계산 루프"""
        import time

        interval = interval or config.INDICATOR_INTERVAL

        print(f"지표 계산 시작: {symbols}, 타임프레임: {timeframes}, 주기: {interval}초")

        while True:
            try:
                for symbol in symbols:
                    for tf in timeframes:
                        indicators = self.calculate_all_indicators(symbol, tf)
                        if indicators:
                            self.save_indicators(indicators)
                            print(f"[{symbol} {tf}] RSI: {indicators['rsi_14']:.2f}, "
                                  f"MACD: {indicators['macd']:.2f}, "
                                  f"ADX: {indicators['adx_14']:.2f}")

                time.sleep(interval)

            except KeyboardInterrupt:
                print("\n계산 중단됨")
                break
            except Exception as e:
                print(f"계산 루프 에러: {str(e)}")
                time.sleep(interval)

    def __del__(self):
        """소멸자"""
        self.db.close()


if __name__ == "__main__":
    engine = IndicatorEngine()
    timeframes = ['5m', '15m', '1h']
    engine.run_calculation_loop(config.TARGET_PAIRS, timeframes)
