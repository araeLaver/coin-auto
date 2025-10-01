"""
추세 추종 전략
EMA 크로스오버, MACD, ADX를 활용한 추세 매매
"""

from typing import Dict, Optional
from .base_strategy import BaseStrategy


class TrendFollowingStrategy(BaseStrategy):
    """추세 추종 전략"""

    def __init__(self, parameters: Dict = None):
        default_params = {
            'ema_short': 9,
            'ema_long': 21,
            'use_macd': True,
            'min_trend_strength': 25,  # ADX 최소값
            'min_confidence': 0.6
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Trend Following', 'trend_following', params)

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """추세 추종 시그널 생성"""

        # 필수 지표 확인
        required = ['ema_9', 'ema_21', 'ema_50', 'macd', 'macd_signal', 'adx_14', 'rsi_14']
        if not all(indicators.get(k) for k in required):
            return None

        ema_short = indicators['ema_9']
        ema_long = indicators['ema_21']
        ema_trend = indicators['ema_50']
        macd = indicators['macd']
        macd_signal = indicators['macd_signal']
        adx = indicators['adx_14']
        rsi = indicators['rsi_14']
        current_price = market_data.get('current_price', 0)

        # ADX로 추세 강도 확인
        if adx < self.parameters['min_trend_strength']:
            return None  # 추세가 약함

        signal_type = 'HOLD'
        strength = 0
        confidence = 0
        reasoning = []

        # 매수 조건
        buy_conditions = 0
        buy_total = 0

        # 1. EMA 골든크로스
        if ema_short > ema_long and current_price > ema_trend:
            buy_conditions += 1
            reasoning.append("EMA 골든크로스")
        buy_total += 1

        # 2. MACD 매수 신호
        if self.parameters['use_macd'] and macd > macd_signal and macd > 0:
            buy_conditions += 1
            reasoning.append("MACD 상승")
        buy_total += 1

        # 3. RSI 과매도 아님 (너무 낮지 않음)
        if 40 < rsi < 70:
            buy_conditions += 1
            reasoning.append("RSI 정상 범위")
        buy_total += 1

        # 4. 강한 상승 추세 (ADX)
        if adx > 30:
            buy_conditions += 1
            reasoning.append(f"강한 추세 (ADX {adx:.1f})")
        buy_total += 1

        # 매도 조건
        sell_conditions = 0
        sell_total = 0

        # 1. EMA 데드크로스
        if ema_short < ema_long or current_price < ema_trend:
            sell_conditions += 1
            reasoning.append("EMA 데드크로스")
        sell_total += 1

        # 2. MACD 매도 신호
        if self.parameters['use_macd'] and macd < macd_signal:
            sell_conditions += 1
            reasoning.append("MACD 하락")
        sell_total += 1

        # 3. RSI 과매수
        if rsi > 70:
            sell_conditions += 1
            reasoning.append("RSI 과매수")
        sell_total += 1

        # 시그널 결정
        buy_score = buy_conditions / buy_total if buy_total > 0 else 0
        sell_score = sell_conditions / sell_total if sell_total > 0 else 0

        if buy_score >= 0.75:  # 75% 이상 조건 충족
            signal_type = 'BUY'
            strength = min(buy_score * 100, 100)
            confidence = buy_score

            # 손절/익절 가격 계산
            stop_loss = current_price * 0.98  # 2% 손절
            take_profit = current_price * 1.06  # 6% 익절

        elif sell_score >= 0.66:  # 66% 이상 조건 충족
            signal_type = 'SELL'
            strength = min(sell_score * 100, 100)
            confidence = sell_score

            stop_loss = current_price * 1.02
            take_profit = current_price * 0.94

        else:
            return None  # 신뢰도 부족

        # 최소 신뢰도 체크
        if confidence < self.parameters['min_confidence']:
            return None

        return {
            'signal_type': signal_type,
            'strength': strength,
            'confidence': confidence,
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reasoning': ' | '.join(reasoning),
            'metadata': {
                'ema_short': ema_short,
                'ema_long': ema_long,
                'macd': macd,
                'adx': adx,
                'rsi': rsi
            }
        }

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """시그널 유효성 검증"""

        # 1. 가격 범위 체크
        entry_price = signal.get('entry_price', 0)
        if entry_price <= 0:
            return False

        # 2. 손절/익절 가격 유효성
        stop_loss = signal.get('stop_loss', 0)
        take_profit = signal.get('take_profit', 0)

        if signal['signal_type'] == 'BUY':
            if stop_loss >= entry_price or take_profit <= entry_price:
                return False
        elif signal['signal_type'] == 'SELL':
            if stop_loss <= entry_price or take_profit >= entry_price:
                return False

        # 3. 시장 변동성 체크
        volatility = market_conditions.get('volatility', 0)
        if volatility > 0.1:  # 10% 이상 변동성이면 위험
            return False

        return True
