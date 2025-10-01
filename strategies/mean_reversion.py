"""
평균 회귀 전략
볼린저 밴드와 RSI를 활용한 과매수/과매도 매매
"""

from typing import Dict, Optional
from .base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """평균 회귀 전략"""

    def __init__(self, parameters: Dict = None):
        default_params = {
            'bb_period': 20,
            'bb_std': 2,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'min_confidence': 0.65
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Mean Reversion', 'mean_reversion', params)

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """평균 회귀 시그널 생성"""

        # 필수 지표 확인
        required = ['bb_upper', 'bb_middle', 'bb_lower', 'rsi_14', 'stoch_k']
        if not all(indicators.get(k) for k in required):
            return None

        bb_upper = indicators['bb_upper']
        bb_middle = indicators['bb_middle']
        bb_lower = indicators['bb_lower']
        rsi = indicators['rsi_14']
        stoch_k = indicators['stoch_k']
        current_price = market_data.get('current_price', 0)

        signal_type = 'HOLD'
        strength = 0
        confidence = 0
        reasoning = []

        # 볼린저 밴드 위치 계산
        bb_range = bb_upper - bb_lower
        if bb_range <= 0:
            return None

        bb_position = (current_price - bb_lower) / bb_range  # 0~1

        # 매수 조건 (과매도)
        buy_conditions = 0
        buy_total = 0

        # 1. 볼린저 밴드 하단 근처
        if bb_position < 0.2:  # 하단 20% 이내
            buy_conditions += 1
            reasoning.append(f"BB 하단 근처 ({bb_position*100:.0f}%)")
        buy_total += 1

        # 2. RSI 과매도
        if rsi < self.parameters['rsi_oversold']:
            buy_conditions += 1
            reasoning.append(f"RSI 과매도 ({rsi:.1f})")
        buy_total += 1

        # 3. 스토캐스틱 과매도
        if stoch_k and stoch_k < 20:
            buy_conditions += 1
            reasoning.append(f"스토캐스틱 과매도 ({stoch_k:.1f})")
        buy_total += 1

        # 4. 가격이 중심선 아래
        if current_price < bb_middle:
            buy_conditions += 1
            reasoning.append("중심선 아래")
        buy_total += 1

        # 매도 조건 (과매수)
        sell_conditions = 0
        sell_total = 0

        # 1. 볼린저 밴드 상단 근처
        if bb_position > 0.8:  # 상단 20% 이내
            sell_conditions += 1
            reasoning.append(f"BB 상단 근처 ({bb_position*100:.0f}%)")
        sell_total += 1

        # 2. RSI 과매수
        if rsi > self.parameters['rsi_overbought']:
            sell_conditions += 1
            reasoning.append(f"RSI 과매수 ({rsi:.1f})")
        sell_total += 1

        # 3. 스토캐스틱 과매수
        if stoch_k and stoch_k > 80:
            sell_conditions += 1
            reasoning.append(f"스토캐스틱 과매수 ({stoch_k:.1f})")
        sell_total += 1

        # 4. 가격이 중심선 위
        if current_price > bb_middle:
            sell_conditions += 1
            reasoning.append("중심선 위")
        sell_total += 1

        # 시그널 결정
        buy_score = buy_conditions / buy_total if buy_total > 0 else 0
        sell_score = sell_conditions / sell_total if sell_total > 0 else 0

        if buy_score >= 0.75:
            signal_type = 'BUY'
            strength = min(buy_score * 100, 100)
            confidence = buy_score

            # 목표: 중심선 복귀
            stop_loss = current_price * 0.97  # 3% 손절
            take_profit = bb_middle * 1.02  # 중심선 + 2%

        elif sell_score >= 0.75:
            signal_type = 'SELL'
            strength = min(sell_score * 100, 100)
            confidence = sell_score

            stop_loss = current_price * 1.03
            take_profit = bb_middle * 0.98  # 중심선 - 2%

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
                'bb_position': bb_position,
                'rsi': rsi,
                'stoch_k': stoch_k,
                'bb_middle': bb_middle
            }
        }

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """시그널 유효성 검증"""

        entry_price = signal.get('entry_price', 0)
        if entry_price <= 0:
            return False

        # 평균 회귀 전략은 횡보장에서 유리
        # 추세장에서는 위험
        trend_strength = market_conditions.get('trend_strength', 0)
        if trend_strength > 30:  # 강한 추세
            return False

        return True
