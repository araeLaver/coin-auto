"""
20% 이상 상승 예측 전략 (Moon Shot Strategy)
- 급등 전조 패턴 감지
- 거래량/가격 동시 분석
- 조기 진입 → 20%+ 수익 목표
"""

from typing import Dict, Optional
from .base_strategy import BaseStrategy


class MoonShotStrategy(BaseStrategy):
    """20% 이상 급등 코인 조기 포착"""

    def __init__(self, parameters: Dict = None):
        default_params = {
            # 급등 전조 신호 파라미터 (현실적으로 완화)
            'min_volume_surge': 1.2,           # 거래량 1.2배 이상 (20% 증가)
            'price_momentum_threshold': 0.005, # 0.5% 이상 상승 모멘텀 (조기 포착)
            'consecutive_green_candles': 2,    # 2개 연속 양봉
            'volume_price_correlation': 0.5,   # 거래량-가격 상관관계

            # 목표 설정
            'target_profit': 0.20,             # 목표 수익 20%
            'min_profit': 0.10,                # 최소 수익 10%
            'stop_loss': 0.05,                 # 손절 5%

            # 필터링 (더 많은 기회 포착)
            'min_confidence': 0.50,            # 신뢰도 50% 이상
            'max_price_range': 1000,           # 최대 1000원 이하
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Moon Shot', 'high_gain', params)

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """20% 급등 가능성 높은 코인 탐색"""

        current_price = market_data.get('current_price', 0)
        if current_price <= 0 or current_price > self.parameters['max_price_range']:
            return None

        # 1. 거래량 체크 (완화)
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if volume_ratio < self.parameters['min_volume_surge']:
            return None

        # 2. 가격 상승 모멘텀 체크 (완화)
        price_change_5m = indicators.get('price_change_5m', 0)
        price_change_15m = indicators.get('price_change_15m', 0)

        # 최근 5분 상승 OR 15분 상승 (둘 중 하나만 OK)
        has_momentum = (price_change_5m >= self.parameters['price_momentum_threshold'] or
                       price_change_15m >= self.parameters['price_momentum_threshold'])

        if not has_momentum:
            return None

        # 3. RSI 체크 (범위 확대)
        rsi = indicators.get('rsi', 50)
        if rsi < 40 or rsi > 80:  # 40-80 구간 (더 넓게)
            return None

        # 4. MACD 조건 완화 (음수 아니면 OK)
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd < -1:  # 강한 하락 추세만 제외
            return None

        # 5. 볼린저 밴드 체크 완화
        bb_position = indicators.get('bb_position', 0.5)
        if bb_position < 0.4:  # 하단 40% 미만만 제외
            return None

        # 6. 호가창 매수 우세 (옵션)
        orderbook_imbalance = indicators.get('orderbook_imbalance', 1.0)

        # 신뢰도 계산 (모든 조건 종합)
        confidence = self._calculate_confidence(
            volume_ratio=volume_ratio,
            price_momentum=price_change_5m,
            rsi=rsi,
            macd_strength=macd - macd_signal,
            bb_position=bb_position,
            orderbook_imbalance=orderbook_imbalance
        )

        if confidence < self.parameters['min_confidence']:
            return None

        # 매수 신호 생성
        return {
            'signal_type': 'BUY',
            'strength': min(confidence * 100, 100),
            'confidence': confidence,
            'entry_price': current_price,
            'stop_loss': current_price * (1 - self.parameters['stop_loss']),
            'take_profit': current_price * (1 + self.parameters['target_profit']),
            'reasoning': f"급등예측 거래량x{volume_ratio:.1f} 모멘텀{price_change_5m*100:+.1f}%",
            'metadata': {
                'volume_ratio': volume_ratio,
                'price_change_5m': price_change_5m,
                'price_change_15m': price_change_15m,
                'rsi': rsi,
                'macd_strength': macd - macd_signal,
                'bb_position': bb_position,
                'orderbook_imbalance': orderbook_imbalance,
                'trigger': 'moon_shot'
            }
        }

    def _calculate_confidence(self, **factors) -> float:
        """신뢰도 계산 (0.0 ~ 1.0)"""
        scores = []

        # 거래량 점수 (가중치 30%)
        volume_ratio = factors.get('volume_ratio', 1.0)
        volume_score = min(volume_ratio / 5.0, 1.0)  # 5배면 만점
        scores.append(volume_score * 0.30)

        # 가격 모멘텀 점수 (가중치 25%)
        price_momentum = factors.get('price_momentum', 0)
        momentum_score = min(price_momentum / 0.05, 1.0)  # 5%면 만점
        scores.append(momentum_score * 0.25)

        # RSI 점수 (가중치 15%)
        rsi = factors.get('rsi', 50)
        rsi_score = (rsi - 50) / 25 if 50 <= rsi <= 75 else 0  # 50-75 구간
        scores.append(rsi_score * 0.15)

        # MACD 점수 (가중치 15%)
        macd_strength = factors.get('macd_strength', 0)
        macd_score = min(abs(macd_strength) / 2.0, 1.0) if macd_strength > 0 else 0
        scores.append(macd_score * 0.15)

        # 볼린저밴드 점수 (가중치 10%)
        bb_position = factors.get('bb_position', 0.5)
        bb_score = (bb_position - 0.5) / 0.5 if bb_position >= 0.5 else 0
        scores.append(bb_score * 0.10)

        # 호가창 점수 (가중치 5%)
        orderbook = factors.get('orderbook_imbalance', 1.0)
        orderbook_score = min((orderbook - 1.0) / 1.0, 1.0) if orderbook > 1.0 else 0
        scores.append(orderbook_score * 0.05)

        return sum(scores)

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """신호 유효성 검증 (완화)"""

        # 신뢰도 재확인
        if signal.get('confidence', 0) < self.parameters['min_confidence']:
            return False

        # 변동성 체크 제거 (거래 기회 확대)
        return True
