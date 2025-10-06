"""
Pre-Pump Hunter Strategy
급등 전 선제 매수 전략 - 20% 상승 전에 미리 사두기

핵심 아이디어:
1. 하락 후 저점 다지는 코인 = 반등 준비
2. 거래량 많으면서 하락 = 세력 매집 가능성
3. 저가 코인 (변동성 크다) = 한번 터지면 20%+
"""

from typing import Dict, Optional
from .base_strategy import BaseStrategy


class PrePumpHunter(BaseStrategy):
    """급등 전 선제 매수 - 상승 전에 미리 사두기"""

    def __init__(self, parameters: Dict = None):
        default_params = {
            # 선제 매수 조건
            'dip_min': -0.10,              # 최소 -10% 하락
            'dip_max': -0.01,              # 최대 -1% 하락 (저점 다지기)
            'volume_surge_min': 1.3,       # 거래량 1.3배 이상 (세력 개입)
            'max_price': 500,              # 최대 500원 (고변동성)

            # RSI 과매도 구간 (반등 가능성)
            'rsi_oversold': 35,            # RSI 35 이하
            'rsi_max': 50,                 # RSI 50 이하 (아직 안 오름)

            # 목표
            'target_profit': 0.20,         # 목표 20%
            'min_profit': 0.10,            # 최소 10%
            'stop_loss': 0.07,             # 손절 7% (여유)

            # 필터
            'min_confidence': 0.40,        # 신뢰도 40% (공격적)
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Pre-Pump Hunter', 'predictive', params)

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """급등 전 패턴 감지 - 선제 매수"""

        current_price = market_data.get('current_price', 0)
        if current_price <= 0 or current_price > self.parameters['max_price']:
            return None

        # 1. 24시간 하락 체크 (저점 다지기 구간)
        # price_change_24h가 없으면 API에서 직접 계산 필요
        # 일단 indicators에서 가져오기 시도
        price_change_24h = indicators.get('price_change_24h', 0)

        # 하락 구간 필터 (-10% ~ -1%)
        if not (self.parameters['dip_min'] <= price_change_24h <= self.parameters['dip_max']):
            # 대안: 15분/5분 하락도 체크
            price_change_15m = indicators.get('price_change_15m', 0)
            if not (self.parameters['dip_min'] <= price_change_15m <= self.parameters['dip_max']):
                return None

        # 2. 거래량 급증 (세력 매집 가능성)
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if volume_ratio < self.parameters['volume_surge_min']:
            return None

        # 3. RSI 과매도 구간 (반등 준비)
        rsi = indicators.get('rsi', 50)
        if rsi > self.parameters['rsi_max']:  # 이미 오르기 시작 = 늦음
            return None

        # RSI 과매도일수록 가산점
        rsi_bonus = 0
        if rsi < self.parameters['rsi_oversold']:
            rsi_bonus = 0.15  # 과매도 보너스

        # 4. 볼린저 하단 근처 (저점)
        bb_position = indicators.get('bb_position', 0.5)
        if bb_position > 0.4:  # 하단 40% 이하만
            return None

        # 5. MACD 골든크로스 임박 (선행지표)
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_cross_soon = (macd > macd_signal * 0.8) and (macd < macd_signal)  # 거의 교차

        # 신뢰도 계산
        confidence = self._calculate_confidence(
            price_change=price_change_24h,
            volume_ratio=volume_ratio,
            rsi=rsi,
            bb_position=bb_position,
            macd_cross_soon=macd_cross_soon
        )

        confidence += rsi_bonus

        if confidence < self.parameters['min_confidence']:
            return None

        # 선제 매수 신호
        return {
            'signal_type': 'BUY',
            'strength': min(confidence * 100, 100),
            'confidence': confidence,
            'entry_price': current_price,
            'stop_loss': current_price * (1 - self.parameters['stop_loss']),
            'take_profit': current_price * (1 + self.parameters['target_profit']),
            'reasoning': f"저점매수 {price_change_24h*100:.1f}% 거래량x{volume_ratio:.1f} RSI{rsi:.0f}",
            'metadata': {
                'price_change_24h': price_change_24h,
                'volume_ratio': volume_ratio,
                'rsi': rsi,
                'bb_position': bb_position,
                'macd_cross_soon': macd_cross_soon,
                'trigger': 'pre_pump'
            }
        }

    def _calculate_confidence(self, **factors) -> float:
        """신뢰도 계산"""
        scores = []

        # 1. 하락폭 점수 (30%) - 하락할수록 반등 가능성
        price_change = factors.get('price_change', 0)
        dip_score = min(abs(price_change) / 0.10, 1.0)  # -10%면 만점
        scores.append(dip_score * 0.30)

        # 2. 거래량 점수 (30%)
        volume_ratio = factors.get('volume_ratio', 1.0)
        volume_score = min((volume_ratio - 1.0) / 1.0, 1.0)  # 2배면 만점
        scores.append(volume_score * 0.30)

        # 3. RSI 과매도 점수 (20%)
        rsi = factors.get('rsi', 50)
        rsi_score = (50 - rsi) / 20 if rsi < 50 else 0  # 30이면 만점
        scores.append(max(rsi_score, 0) * 0.20)

        # 4. 볼린저 하단 점수 (10%)
        bb_position = factors.get('bb_position', 0.5)
        bb_score = (0.4 - bb_position) / 0.4 if bb_position < 0.4 else 0
        scores.append(max(bb_score, 0) * 0.10)

        # 5. MACD 골든크로스 임박 (10%)
        macd_cross = factors.get('macd_cross_soon', False)
        scores.append(0.10 if macd_cross else 0)

        return sum(scores)

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """신호 검증 (완화)"""

        # 신뢰도만 체크
        if signal.get('confidence', 0) < self.parameters['min_confidence']:
            return False

        return True
