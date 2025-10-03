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
            # 초단기 스캘핑 최적화 (회전율 극대화)
            'instant_profit_target': 0.012,    # 1.2% 익절 (수수료 0.5% 제외 0.7% 순익)
            'quick_profit_target': 0.015,      # 1.5% 익절
            'ultra_quick_stop': 0.015,         # 1.5% 손절 (빠른 손절)
            'price_spike_threshold': 0.008,    # 0.8% 급등 포착
            'min_volume_ratio': 1.5,           # 거래량 조건 강화
            'min_confidence': 0.70,            # 신뢰도 상향
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Hyper Scalping', 'ultra_fast', params)
        self.last_check_time = {}
        self.last_prices = {}  # 이전 가격 캐시

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """실시간 수익률 기반 시그널 - 지표 없이도 작동"""

        current_price = market_data.get('current_price', 0)
        if current_price <= 0:
            return None

        # 실시간 체크 (1초 이내 중복 방지)
        now = time.time()
        if symbol in self.last_check_time:
            if now - self.last_check_time[symbol] < 1:
                return None
        self.last_check_time[symbol] = now

        # 거래량 체크 (옵션)
        volume_ratio = indicators.get('volume_ratio', 1.5)  # 기본값 1.5로 통과

        # 캐시된 이전 가격과 비교
        if symbol not in self.last_prices:
            self.last_prices[symbol] = current_price
            return None

        prev_price = self.last_prices[symbol]
        self.last_prices[symbol] = current_price

        # 실시간 가격 변동률 계산 (이전 체크 대비)
        price_change_1m = (current_price - prev_price) / prev_price if prev_price > 0 else 0

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

        # 전략 2: 상승 추세 (0.3% 이상 포착)
        elif price_change_1m > 0.003:  # 0.3% 이상 상승
            if volume_ratio > 1.2:  # 거래량 확인
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

        # 전략 3: 순간 반등 (가격 하락 후 반등) - RSI 없이도 작동
        elif -0.005 < price_change_1m < -0.001:  # 약간 하락
            if volume_ratio > 1.3:
                return {
                    'signal_type': 'BUY',
                    'strength': 55,
                    'confidence': 0.65,
                    'entry_price': current_price,
                    'stop_loss': current_price * (1 - self.parameters['ultra_quick_stop']),
                    'take_profit': current_price * (1 + self.parameters['instant_profit_target']),
                    'reasoning': f"반등기회 {price_change_1m*100:.2f}%",
                    'metadata': {
                        'price_change_1m': price_change_1m,
                        'volume_ratio': volume_ratio,
                        'trigger': 'bounce'
                    }
                }

        return None

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """시그널 유효성 검증 (거의 모든 신호 통과)"""

        # 신뢰도 체크 (매우 완화)
        if signal.get('confidence', 0) < self.parameters['min_confidence']:
            return False

        # 모든 신호 통과 (조건 최소화)
        return True
