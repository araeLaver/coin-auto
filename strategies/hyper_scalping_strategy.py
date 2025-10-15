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
            # 손절만 엄격, 익절은 무제한 (트레일링 스톱으로 추종)
            'instant_profit_target': 10.0,     # 1000% (사실상 무제한)
            'quick_profit_target': 10.0,       # 1000% (사실상 무제한)
            'ultra_quick_stop': 0.015,         # 1.5% 손절 (엄격)
            'price_spike_threshold': 0.008,    # 0.8% 급등 포착 (신중)
            'min_volume_ratio': 1.5,           # 거래량 1.5배 이상
            'min_confidence': 0.70,            # 신뢰도 70% 이상
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Trailing Only', 'trailing_only', params)
        self.last_check_time = {}
        self.last_prices = {}  # 이전 가격 캐시

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """실시간 수익률 기반 시그널 - 지표 없이도 작동"""

        current_price = market_data.get('current_price', 0)
        if current_price <= 0:
            return None

        # 거래량 체크 (옵션)
        volume_ratio = indicators.get('volume_ratio', 1.0)  # 기본값 1.0로 통과

        # 캐시된 이전 가격과 비교
        if symbol not in self.last_prices:
            self.last_prices[symbol] = current_price
            return None

        prev_price = self.last_prices[symbol]
        self.last_prices[symbol] = current_price

        # 실시간 가격 변동률 계산 (이전 체크 대비)
        price_change_1m = (current_price - prev_price) / prev_price if prev_price > 0 else 0

        # 전략 1: 강한 급등 포착 (0.8% 이상 + 거래량 확인)
        if price_change_1m >= self.parameters['price_spike_threshold']:
            # 거래량 조건 체크
            if volume_ratio < self.parameters['min_volume_ratio']:
                return None

            # RSI 체크 (과매수 구간 제외)
            rsi = indicators.get('rsi', 50)
            if rsi > 70:  # 과매수 구간
                return None

            strength = min(price_change_1m * 100, 100)
            confidence = min(0.70 + (volume_ratio / 20), 0.90)

            return {
                'signal_type': 'BUY',
                'strength': strength,
                'confidence': confidence,
                'entry_price': current_price,
                'stop_loss': current_price * (1 - self.parameters['ultra_quick_stop']),
                'take_profit': current_price * (1 + self.parameters['instant_profit_target']),
                'reasoning': f"급등{price_change_1m*100:+.2f}% 거래량{volume_ratio:.1f}배",
                'metadata': {
                    'price_change_1m': price_change_1m,
                    'volume_ratio': volume_ratio,
                    'rsi': rsi,
                    'trigger': 'strong_spike'
                }
            }

        # 전략 2: RSI 과매도 반등 (더 신중)
        rsi = indicators.get('rsi', 50)
        if 30 < rsi < 40 and volume_ratio > 1.8:  # RSI 과매도 구간 + 강한 거래량
            if price_change_1m > 0.003:  # 0.3% 이상 상승 중
                return {
                    'signal_type': 'BUY',
                    'strength': 65,
                    'confidence': 0.75,
                    'entry_price': current_price,
                    'stop_loss': current_price * (1 - self.parameters['ultra_quick_stop']),
                    'take_profit': current_price * (1 + self.parameters['instant_profit_target']),
                    'reasoning': f"RSI반등 {rsi:.0f} 거래량{volume_ratio:.1f}배",
                    'metadata': {
                        'price_change_1m': price_change_1m,
                        'volume_ratio': volume_ratio,
                        'rsi': rsi,
                        'trigger': 'rsi_bounce'
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
