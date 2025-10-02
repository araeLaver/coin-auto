"""
호가창 기반 초단타 스캘핑 전략
남들이 안 쓰는 선행 지표 활용
"""

from typing import Dict, Optional
from .base_strategy import BaseStrategy


class OrderbookScalpingStrategy(BaseStrategy):
    """호가창 실시간 분석 스캘핑"""

    def __init__(self, parameters: Dict = None):
        default_params = {
            'wall_size_threshold': 3.0,  # 매수/매도 벽 기준 (평균 대비)
            'imbalance_threshold': 1.5,   # 호가 불균형 비율
            'spread_threshold': 0.003,    # 최대 스프레드 0.3%
            'min_wall_distance': 0.008,   # 벽까지 최소 거리 0.8%
            'quick_profit_target': 0.008, # 익절 0.8% (수수료 0.5% 포함)
            'stop_loss': 0.008,           # 손절 0.8%
            'fee_rate': 0.005,            # 빗썸 왕복 수수료 0.5%
        }
        params = {**default_params, **(parameters or {})}
        super().__init__('Orderbook Scalping', 'scalping', params)

    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """호가창 기반 시그널 생성"""

        orderbook = market_data.get('orderbook')
        if not orderbook:
            return None

        current_price = market_data.get('current_price', 0)
        if current_price <= 0:
            return None

        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])

        if not bids or not asks:
            return None

        best_bid = float(bids[0]['price']) if bids else 0
        best_ask = float(asks[0]['price']) if asks else 0

        # 1. 스프레드 확인 (너무 크면 거래 안함)
        spread = (best_ask - best_bid) / best_bid if best_bid > 0 else 999
        if spread > self.parameters['spread_threshold']:
            return None  # 스프레드 너무 큼

        # 2. 호가 불균형 계산
        bid_volume = sum(float(b['quantity']) for b in bids[:10])
        ask_volume = sum(float(a['quantity']) for a in asks[:10])

        if ask_volume <= 0:
            return None

        imbalance_ratio = bid_volume / ask_volume

        # 3. 매수벽/매도벽 감지
        avg_bid_size = bid_volume / 10
        avg_ask_size = ask_volume / 10

        buy_walls = []  # 큰 매수 주문들
        sell_walls = []  # 큰 매도 주문들

        for bid in bids[:20]:
            qty = float(bid['quantity'])
            if qty > avg_bid_size * self.parameters['wall_size_threshold']:
                buy_walls.append({
                    'price': float(bid['price']),
                    'quantity': qty,
                    'distance': (current_price - float(bid['price'])) / current_price
                })

        for ask in asks[:20]:
            qty = float(ask['quantity'])
            if qty > avg_ask_size * self.parameters['wall_size_threshold']:
                sell_walls.append({
                    'price': float(ask['price']),
                    'quantity': qty,
                    'distance': (float(ask['price']) - current_price) / current_price
                })

        # 4. 전략 로직
        signal_type = 'HOLD'
        reasoning = []
        strength = 0
        confidence = 0

        # 전략 A: 매수벽 근처 + 호가 불균형 (매수 우세)
        if buy_walls and imbalance_ratio > self.parameters['imbalance_threshold']:
            # 가까운 매수벽 찾기
            nearest_buy_wall = min(buy_walls, key=lambda x: x['distance'])

            if nearest_buy_wall['distance'] < self.parameters['min_wall_distance']:
                signal_type = 'BUY'
                strength = min(imbalance_ratio * 30, 100)
                confidence = min(imbalance_ratio / 3, 0.95)
                reasoning.append(f"매수벽 지지 ({nearest_buy_wall['distance']*100:.2f}% 아래)")
                reasoning.append(f"호가 불균형 {imbalance_ratio:.2f}:1")

                # 초단타: 매수벽 위에서 빠른 익절
                entry_price = current_price
                stop_loss = nearest_buy_wall['price'] * 0.998  # 벽 아래 0.2%
                take_profit = current_price * (1 + self.parameters['quick_profit_target'])

        # 전략 B: 매도벽 돌파 + 매수 압력
        elif sell_walls and imbalance_ratio > self.parameters['imbalance_threshold']:
            # 가까운 매도벽 찾기
            nearest_sell_wall = min(sell_walls, key=lambda x: x['distance'])

            if nearest_sell_wall['distance'] < self.parameters['min_wall_distance']:
                # 매수 압력이 강하면 벽 돌파 예상
                signal_type = 'BUY'
                strength = min(imbalance_ratio * 25, 100)
                confidence = min(imbalance_ratio / 3.5, 0.9)
                reasoning.append(f"매도벽 돌파 시도 ({nearest_sell_wall['distance']*100:.2f}% 위)")
                reasoning.append(f"매수 압력 {imbalance_ratio:.2f}:1")

                entry_price = current_price
                stop_loss = current_price * 0.995  # 0.5% 손절
                take_profit = nearest_sell_wall['price'] * 1.003  # 벽 위 0.3%

        # 전략 C: 매도벽 근처 + 호가 불균형 (매도 우세)
        elif sell_walls and imbalance_ratio < (1 / self.parameters['imbalance_threshold']):
            nearest_sell_wall = min(sell_walls, key=lambda x: x['distance'])

            if nearest_sell_wall['distance'] < self.parameters['min_wall_distance']:
                signal_type = 'SELL'
                strength = min((1/imbalance_ratio) * 30, 100)
                confidence = min((1/imbalance_ratio) / 3, 0.9)
                reasoning.append(f"매도벽 저항 ({nearest_sell_wall['distance']*100:.2f}% 위)")
                reasoning.append(f"매도 우세 {imbalance_ratio:.2f}:1")

                entry_price = current_price
                stop_loss = current_price * 1.005
                take_profit = current_price * (1 - self.parameters['quick_profit_target'])

        else:
            return None

        if signal_type == 'HOLD':
            return None

        return {
            'signal_type': signal_type,
            'strength': strength,
            'confidence': confidence,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reasoning': ' | '.join(reasoning),
            'metadata': {
                'imbalance_ratio': imbalance_ratio,
                'spread': spread,
                'buy_walls_count': len(buy_walls),
                'sell_walls_count': len(sell_walls),
                'best_bid': best_bid,
                'best_ask': best_ask
            }
        }

    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """시그널 유효성 검증"""

        # 스프레드 재확인
        metadata = signal.get('metadata', {})
        spread = metadata.get('spread', 999)

        if spread > self.parameters['spread_threshold']:
            return False

        # 호가 불균형 확인
        imbalance = metadata.get('imbalance_ratio', 1.0)

        if signal['signal_type'] == 'BUY':
            return imbalance > self.parameters['imbalance_threshold']
        elif signal['signal_type'] == 'SELL':
            return imbalance < (1 / self.parameters['imbalance_threshold'])

        return True
