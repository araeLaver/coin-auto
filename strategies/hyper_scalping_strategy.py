"""
초고속 실시간 수익률 스캘핑 전략
- 1-3초 실시간 가격 변동 추적
- 0.3-0.5% 초단타 익절
- 모든 코인 동시 모니터링
"""

from typing import Dict, Optional
from .base_strategy import BaseStrategy
import time


class HyperScalpingStrategy(BaseStrategy):
    """초고속 실시간 수익률 스캘핑"""

    def __init__(self, parameters: Dict = None):
        default_params = {
            # 초단타 설정
            'instant_profit_target': 0.003,    # 0.3% 익절
            'quick_profit_target': 0.005,      # 0.5% 익절
            'ultra_quick_stop': 0.002,         # 0.2% 손절
            'price_spike_threshold': 0.008,    # 0.8% 급등 감지
            'min_volume_ratio': 1.3,           # 최소 거래량
            'min_confidence': 0.60,
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Hyper Scalping', 'ultra_fast', params)
        self.last_check_time = {}

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """실시간 수익률 기반 시그널"""

        current_price = market_data.get('current_price', 0)
        if current_price <= 0:
            return None

        # 실시간 체크 (1초 이내 중복 방지)
        now = time.time()
        if symbol in self.last_check_time:
            if now - self.last_check_time[symbol] < 1:
                return None
        self.last_check_time[symbol] = now

        # 거래량 체크
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if volume_ratio < self.parameters['min_volume_ratio']:
            return None

        # 실시간 가격 변동률 계산 (최근 1분)
        ema_short = indicators.get('ema_9', current_price)
        price_change_1m = (current_price - ema_short) / ema_short if ema_short > 0 else 0

        # 전략 1: 급등 순간 포착 (0.8% 이상)
        if price_change_1m > self.parameters['price_spike_threshold']:
            strength = min(price_change_1m * 100, 100)
            confidence = min(0.60 + (volume_ratio / 10), 0.90)

            return {
                'signal_type': 'BUY',
                'strength': strength,
                'confidence': confidence,
                'entry_price': current_price,
                'stop_loss': current_price * (1 - self.parameters['ultra_quick_stop']),
                'take_profit': current_price * (1 + self.parameters['instant_profit_target']),
                'reasoning': f"급등{price_change_1m*100:.2f}% 순간포착",
                'metadata': {
                    'price_change_1m': price_change_1m,
                    'volume_ratio': volume_ratio,
                    'trigger': 'spike'
                }
            }

        # 전략 2: 작은 상승 추세 (0.3-0.8%)
        elif 0.003 < price_change_1m <= 0.008:
            if volume_ratio > 1.5:  # 거래량 증가 확인
                strength = 60
                confidence = 0.65

                return {
                    'signal_type': 'BUY',
                    'strength': strength,
                    'confidence': confidence,
                    'entry_price': current_price,
                    'stop_loss': current_price * (1 - self.parameters['ultra_quick_stop']),
                    'take_profit': current_price * (1 + self.parameters['quick_profit_target']),
                    'reasoning': f"상승추세{price_change_1m*100:.2f}%",
                    'metadata': {
                        'price_change_1m': price_change_1m,
                        'volume_ratio': volume_ratio,
                        'trigger': 'trend'
                    }
                }

        # 전략 3: 순간 반등 (가격 하락 후 반등)
        elif -0.005 < price_change_1m < -0.001:  # 약간 하락
            # RSI 체크 (있으면)
            rsi = indicators.get('rsi_14')
            if rsi and rsi < 40 and volume_ratio > 1.4:
                return {
                    'signal_type': 'BUY',
                    'strength': 55,
                    'confidence': 0.65,
                    'entry_price': current_price,
                    'stop_loss': current_price * (1 - self.parameters['ultra_quick_stop']),
                    'take_profit': current_price * (1 + self.parameters['instant_profit_target']),
                    'reasoning': f"반등기회 RSI{rsi:.0f}",
                    'metadata': {
                        'price_change_1m': price_change_1m,
                        'volume_ratio': volume_ratio,
                        'rsi': rsi,
                        'trigger': 'bounce'
                    }
                }

        return None

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """시그널 유효성 검증 (매우 느슨함)"""

        # 신뢰도 체크
        if signal.get('confidence', 0) < self.parameters['min_confidence']:
            return False

        # 거래량만 체크 (다른 조건 최소화)
        metadata = signal.get('metadata', {})
        volume_ratio = metadata.get('volume_ratio', 0)

        if volume_ratio < 1.2:
            return False

        return True
