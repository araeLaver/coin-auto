"""
호가창 불균형 전략 (차별화 핵심)
매수/매도 벽 분석 및 불균형 기반 매매
"""

from typing import Dict, Optional, List
from .base_strategy import BaseStrategy


class OrderbookImbalanceStrategy(BaseStrategy):
    """호가창 불균형 전략"""

    def __init__(self, parameters: Dict = None):
        default_params = {
            'imbalance_threshold': 1.8,  # 불균형 비율
            'min_wall_size_ratio': 5.0,  # 평균 대비 배수
            'reaction_time_seconds': 3,
            'min_confidence': 0.7
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Orderbook Imbalance', 'microstructure', params)

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """호가창 불균형 시그널 생성"""

        # 호가창 데이터 확인
        orderbook = market_data.get('orderbook')
        if not orderbook:
            return None

        bid_total = orderbook.get('bid_total_volume', 0)
        ask_total = orderbook.get('ask_total_volume', 0)
        imbalance_ratio = orderbook.get('imbalance_ratio', 1.0)
        bid_walls = orderbook.get('bid_walls', [])
        ask_walls = orderbook.get('ask_walls', [])
        spread = orderbook.get('spread', 0)
        best_bid = orderbook.get('best_bid', 0)
        best_ask = orderbook.get('best_ask', 0)

        current_price = market_data.get('current_price', best_bid)

        signal_type = 'HOLD'
        strength = 0
        confidence = 0
        reasoning = []

        # 매수 우세 (매수 > 매도)
        if imbalance_ratio >= self.parameters['imbalance_threshold']:
            buy_conditions = 0
            buy_total = 0

            # 1. 강한 매수 불균형
            buy_conditions += 1
            reasoning.append(f"매수 우세 ({imbalance_ratio:.2f}x)")
            buy_total += 1

            # 2. 큰 매수 벽 존재
            if bid_walls:
                max_bid_wall = max(bid_walls, key=lambda x: x['ratio'])
                if max_bid_wall['ratio'] >= self.parameters['min_wall_size_ratio']:
                    buy_conditions += 1
                    reasoning.append(f"대형 매수벽 ({max_bid_wall['ratio']:.1f}x)")
            buy_total += 1

            # 3. 스프레드 좁음 (유동성 좋음)
            if spread > 0:
                spread_percent = (spread / current_price) * 100
                if spread_percent < 0.1:  # 0.1% 미만
                    buy_conditions += 1
                    reasoning.append("좁은 스프레드")
            buy_total += 1

            # 4. 매도벽 약함
            if not ask_walls or (ask_walls and max(w['ratio'] for w in ask_walls) < 3):
                buy_conditions += 1
                reasoning.append("약한 매도 저항")
            buy_total += 1

            buy_score = buy_conditions / buy_total if buy_total > 0 else 0

            if buy_score >= 0.75:
                signal_type = 'BUY'
                strength = min((imbalance_ratio / self.parameters['imbalance_threshold']) * 50 + buy_score * 50, 100)
                confidence = buy_score

                # 호가창 전략은 단기 매매
                stop_loss = current_price * 0.995  # 0.5% 손절
                take_profit = current_price * 1.015  # 1.5% 익절

        # 매도 우세 (매도 > 매수)
        elif imbalance_ratio <= (1 / self.parameters['imbalance_threshold']):
            sell_conditions = 0
            sell_total = 0

            # 1. 강한 매도 불균형
            sell_conditions += 1
            reasoning.append(f"매도 우세 ({imbalance_ratio:.2f}x)")
            sell_total += 1

            # 2. 큰 매도 벽 존재
            if ask_walls:
                max_ask_wall = max(ask_walls, key=lambda x: x['ratio'])
                if max_ask_wall['ratio'] >= self.parameters['min_wall_size_ratio']:
                    sell_conditions += 1
                    reasoning.append(f"대형 매도벽 ({max_ask_wall['ratio']:.1f}x)")
            sell_total += 1

            # 3. 스프레드 확대 (패닉)
            if spread > 0:
                spread_percent = (spread / current_price) * 100
                if spread_percent > 0.2:  # 0.2% 이상
                    sell_conditions += 1
                    reasoning.append("스프레드 확대")
            sell_total += 1

            # 4. 매수벽 약함
            if not bid_walls or (bid_walls and max(w['ratio'] for w in bid_walls) < 3):
                sell_conditions += 1
                reasoning.append("약한 매수 지지")
            sell_total += 1

            sell_score = sell_conditions / sell_total if sell_total > 0 else 0

            if sell_score >= 0.75:
                signal_type = 'SELL'
                strength = min(((1/imbalance_ratio) / self.parameters['imbalance_threshold']) * 50 + sell_score * 50, 100)
                confidence = sell_score

                stop_loss = current_price * 1.005
                take_profit = current_price * 0.985

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
                'imbalance_ratio': imbalance_ratio,
                'bid_total': bid_total,
                'ask_total': ask_total,
                'bid_walls_count': len(bid_walls),
                'ask_walls_count': len(ask_walls),
                'spread': spread
            }
        }

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """시그널 유효성 검증"""

        entry_price = signal.get('entry_price', 0)
        if entry_price <= 0:
            return False

        # 호가창 전략은 초단기이므로 높은 유동성 필수
        spread = signal.get('metadata', {}).get('spread', float('inf'))
        spread_percent = (spread / entry_price) * 100 if entry_price > 0 else float('inf')

        if spread_percent > 0.3:  # 0.3% 이상이면 위험
            return False

        return True
