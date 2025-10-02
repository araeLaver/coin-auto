"""
변동성 돌파 + 모멘텀 전략
- 급등 코인 빠른 포착
- 빠른 익절/손절
"""

from typing import Dict, Optional
from .base_strategy import BaseStrategy


class MomentumBreakoutStrategy(BaseStrategy):
    """변동성 돌파 스캘핑"""

    def __init__(self, parameters: Dict = None):
        default_params = {
            'price_change_threshold': 0.015,  # 1.5% 이상 급등/급락
            'volume_surge_ratio': 2.0,        # 거래량 2배 이상
            'quick_profit': 0.008,            # 0.8% 익절
            'quick_stop': 0.004,              # 0.4% 손절
            'rsi_oversold': 30,               # RSI 과매도
            'rsi_overbought': 70,             # RSI 과매수
            'min_confidence': 0.65,
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Momentum Breakout', 'scalping', params)

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """모멘텀 돌파 시그널"""

        current_price = market_data.get('current_price', 0)
        if current_price <= 0:
            return None

        # 필수 지표
        rsi = indicators.get('rsi_14')
        ema_short = indicators.get('ema_9')
        ema_long = indicators.get('ema_21')
        volume_ratio = indicators.get('volume_ratio', 1.0)

        if not all([rsi, ema_short, ema_long]):
            return None

        # 가격 변화율 계산
        price_change = (current_price - ema_short) / ema_short if ema_short > 0 else 0

        # 전략 1: 급등 + 거래량 급증 (매수)
        if (price_change > self.parameters['price_change_threshold'] and
            volume_ratio > self.parameters['volume_surge_ratio'] and
            rsi < 65 and  # 과매수 아님
            current_price > ema_short > ema_long):  # 상승 추세

            strength = min((price_change / self.parameters['price_change_threshold']) * 50, 100)
            confidence = min(0.65 + (volume_ratio / 10), 0.95)

            return {
                'signal_type': 'BUY',
                'strength': strength,
                'confidence': confidence,
                'entry_price': current_price,
                'stop_loss': current_price * (1 - self.parameters['quick_stop']),
                'take_profit': current_price * (1 + self.parameters['quick_profit']),
                'reasoning': f"급등{price_change*100:.1f}% + 거래량{volume_ratio:.1f}배",
                'metadata': {
                    'price_change': price_change,
                    'volume_ratio': volume_ratio,
                    'rsi': rsi
                }
            }

        # 전략 2: 과매도 반등 (매수)
        elif (rsi < self.parameters['rsi_oversold'] and
              current_price < ema_short and
              volume_ratio > 1.5):  # 거래량 증가

            strength = min((self.parameters['rsi_oversold'] - rsi) * 2, 100)
            confidence = 0.70

            return {
                'signal_type': 'BUY',
                'strength': strength,
                'confidence': confidence,
                'entry_price': current_price,
                'stop_loss': current_price * (1 - self.parameters['quick_stop']),
                'take_profit': current_price * (1 + self.parameters['quick_profit']),
                'reasoning': f"과매도 반등 RSI {rsi:.0f}",
                'metadata': {
                    'rsi': rsi,
                    'volume_ratio': volume_ratio
                }
            }

        # 전략 3: 단기 하락 추세 (공매도 - 실제로는 사용 안함)
        elif (price_change < -self.parameters['price_change_threshold'] and
              volume_ratio > self.parameters['volume_surge_ratio'] and
              rsi > 35):  # 너무 과매도 아님

            # 실제로는 하락장에서 매수 안함 (보수적)
            return None

        return None

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """시그널 유효성 검증"""

        # 신뢰도 체크
        if signal.get('confidence', 0) < self.parameters['min_confidence']:
            return False

        # 거래량 체크
        metadata = signal.get('metadata', {})
        volume_ratio = metadata.get('volume_ratio', 0)

        if volume_ratio < 1.2:  # 최소 거래량 조건
            return False

        return True
