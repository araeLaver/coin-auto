"""
모멘텀 돌파 전략
거래량과 변동성 기반 돌파 매매
"""

from typing import Dict, Optional
from .base_strategy import BaseStrategy


class MomentumBreakoutStrategy(BaseStrategy):
    """모멘텀 돌파 전략"""

    def __init__(self, parameters: Dict = None):
        default_params = {
            'volume_threshold': 1.5,  # 평균 대비 배수
            'atr_multiplier': 2.0,
            'confirmation_candles': 2,
            'min_confidence': 0.7
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Momentum Breakout', 'momentum', params)

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """모멘텀 돌파 시그널 생성"""

        # 필수 지표 확인
        required = ['ema_21', 'ema_50', 'atr_14', 'volume_sma_20', 'rsi_14']
        if not all(indicators.get(k) for k in required):
            return None

        ema_21 = indicators['ema_21']
        ema_50 = indicators['ema_50']
        atr = indicators['atr_14']
        volume_avg = indicators['volume_sma_20']
        rsi = indicators['rsi_14']

        current_price = market_data.get('current_price', 0)
        current_volume = market_data.get('current_volume', 0)

        signal_type = 'HOLD'
        strength = 0
        confidence = 0
        reasoning = []

        # 거래량 급증 확인
        if volume_avg <= 0:
            return None

        volume_ratio = current_volume / volume_avg

        if volume_ratio < self.parameters['volume_threshold']:
            return None  # 거래량 부족

        # 상승 돌파 조건
        buy_conditions = 0
        buy_total = 0

        # 1. 가격이 이동평균선 위
        if current_price > ema_21 > ema_50:
            buy_conditions += 1
            reasoning.append("이동평균선 상승 배열")
        buy_total += 1

        # 2. 거래량 폭발
        if volume_ratio >= self.parameters['volume_threshold']:
            buy_conditions += 1
            reasoning.append(f"거래량 급증 ({volume_ratio:.1f}x)")
        buy_total += 1

        # 3. RSI 강세 (하지만 과매수 아님)
        if 50 < rsi < 75:
            buy_conditions += 1
            reasoning.append("RSI 강세")
        buy_total += 1

        # 4. ATR 기반 변동성 증가
        price_change_percent = abs(current_price - ema_21) / ema_21 if ema_21 > 0 else 0
        atr_percent = atr / current_price if current_price > 0 else 0

        if price_change_percent > atr_percent * self.parameters['atr_multiplier']:
            buy_conditions += 1
            reasoning.append("변동성 증가")
        buy_total += 1

        # 하락 돌파 조건
        sell_conditions = 0
        sell_total = 0

        # 1. 가격이 이동평균선 아래
        if current_price < ema_21 < ema_50:
            sell_conditions += 1
            reasoning.append("이동평균선 하락 배열")
        sell_total += 1

        # 2. 거래량 폭발 (하락)
        if volume_ratio >= self.parameters['volume_threshold']:
            sell_conditions += 1
            reasoning.append(f"거래량 급증 ({volume_ratio:.1f}x)")
        sell_total += 1

        # 3. RSI 약세
        if rsi < 50:
            sell_conditions += 1
            reasoning.append("RSI 약세")
        sell_total += 1

        # 시그널 결정
        buy_score = buy_conditions / buy_total if buy_total > 0 else 0
        sell_score = sell_conditions / sell_total if sell_total > 0 else 0

        if buy_score >= 0.75:
            signal_type = 'BUY'
            strength = min(buy_score * 100, 100)
            confidence = buy_score * (min(volume_ratio / 2, 1))  # 거래량 가중

            # 돌파 전략은 수익 크게, 손실 작게
            stop_loss = current_price - (atr * 1.5)
            take_profit = current_price + (atr * 3)

        elif sell_score >= 0.75:
            signal_type = 'SELL'
            strength = min(sell_score * 100, 100)
            confidence = sell_score * (min(volume_ratio / 2, 1))

            stop_loss = current_price + (atr * 1.5)
            take_profit = current_price - (atr * 3)

        else:
            return None

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
                'volume_ratio': volume_ratio,
                'atr': atr,
                'rsi': rsi,
                'ema_21': ema_21,
                'ema_50': ema_50
            }
        }

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """시그널 유효성 검증"""

        entry_price = signal.get('entry_price', 0)
        if entry_price <= 0:
            return False

        # 모멘텀 전략은 충분한 거래량 필수
        volume_ratio = signal.get('metadata', {}).get('volume_ratio', 0)
        if volume_ratio < self.parameters['volume_threshold']:
            return False

        return True
