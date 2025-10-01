"""
호가창 데이터 수집 및 불균형 분석
핵심 차별화 모듈 - 대부분의 개인 투자자가 활용하지 않는 데이터
"""

import time
from datetime import datetime
from typing import Dict, List, Tuple
from decimal import Decimal
from api import BithumbAPI
from database import SessionLocal, OrderbookSnapshot, OrderbookAnomaly, SystemLog
import config


class OrderbookCollector:
    """호가창 데이터 수집 및 실시간 분석"""

    def __init__(self):
        self.api = BithumbAPI()
        self.db = SessionLocal()
        self.last_orderbooks = {}  # 이전 호가창 저장

    def collect_orderbook(self, symbol: str) -> Dict:
        """
        호가창 데이터 수집
        Args:
            symbol: 코인 심볼 (예: "BTC")
        Returns:
            호가창 데이터
        """
        try:
            response = self.api.get_orderbook(symbol)

            if response.get('status') == '0000':
                data = response.get('data', {})
                return {
                    'symbol': symbol,
                    'timestamp': datetime.now(),
                    'bids': data.get('bids', []),  # 매수 호가
                    'asks': data.get('asks', []),  # 매도 호가
                }
            else:
                self._log_error(f"호가 조회 실패: {symbol} - {response.get('message')}")
                return None

        except Exception as e:
            self._log_error(f"호가 수집 에러: {symbol} - {str(e)}")
            return None

    def analyze_orderbook(self, orderbook: Dict) -> Dict:
        """
        호가창 분석 - 불균형, 벽, 스프레드 등
        Args:
            orderbook: 호가창 데이터
        Returns:
            분석 결과
        """
        bids = orderbook['bids']
        asks = orderbook['asks']

        # 매수/매도 총 물량 계산
        bid_total_volume = sum(float(bid['quantity']) for bid in bids)
        ask_total_volume = sum(float(ask['quantity']) for ask in asks)

        # 불균형 비율 (매수 / 매도)
        imbalance_ratio = bid_total_volume / ask_total_volume if ask_total_volume > 0 else 0

        # 스프레드 (최고 매수가 - 최저 매도가)
        best_bid = float(bids[0]['price']) if bids else 0
        best_ask = float(asks[0]['price']) if asks else 0
        spread = best_ask - best_bid

        # 가격별 물량 분포 분석
        bid_walls = self._detect_walls(bids, 'bid')
        ask_walls = self._detect_walls(asks, 'ask')

        return {
            'bid_total_volume': bid_total_volume,
            'ask_total_volume': ask_total_volume,
            'imbalance_ratio': imbalance_ratio,
            'spread': spread,
            'best_bid': best_bid,
            'best_ask': best_ask,
            'bid_walls': bid_walls,
            'ask_walls': ask_walls,
        }

    def _detect_walls(self, orders: List[Dict], side: str) -> List[Dict]:
        """
        호가창 벽(대량 주문) 감지
        Args:
            orders: 호가 리스트
            side: 'bid' 또는 'ask'
        Returns:
            감지된 벽 리스트
        """
        if not orders:
            return []

        walls = []
        avg_quantity = sum(float(o['quantity']) for o in orders) / len(orders)

        for order in orders:
            quantity = float(order['quantity'])
            price = float(order['price'])

            # 평균의 3배 이상이면 벽으로 간주
            if quantity > avg_quantity * 3:
                walls.append({
                    'price': price,
                    'quantity': quantity,
                    'ratio': quantity / avg_quantity,
                    'side': side
                })

        return walls

    def detect_anomalies(self, symbol: str, current: Dict, previous: Dict = None) -> List[Dict]:
        """
        호가창 이상 패턴 감지
        Args:
            symbol: 코인 심볼
            current: 현재 분석 결과
            previous: 이전 분석 결과
        Returns:
            감지된 이상 패턴 리스트
        """
        anomalies = []

        # 1. 극단적 불균형 (매수/매도 비율이 2:1 이상)
        if current['imbalance_ratio'] > 2.0:
            anomalies.append({
                'type': 'extreme_bid_imbalance',
                'severity': min((current['imbalance_ratio'] - 2.0) * 20, 100),
                'details': {
                    'imbalance_ratio': current['imbalance_ratio'],
                    'bid_volume': current['bid_total_volume'],
                    'ask_volume': current['ask_total_volume']
                }
            })
        elif current['imbalance_ratio'] < 0.5:
            anomalies.append({
                'type': 'extreme_ask_imbalance',
                'severity': min((2.0 - 1/current['imbalance_ratio']) * 20, 100) if current['imbalance_ratio'] > 0 else 100,
                'details': {
                    'imbalance_ratio': current['imbalance_ratio'],
                    'bid_volume': current['bid_total_volume'],
                    'ask_volume': current['ask_total_volume']
                }
            })

        # 2. 대형 벽 감지 (Whale Wall)
        all_walls = current['bid_walls'] + current['ask_walls']
        for wall in all_walls:
            if wall['ratio'] > 5:  # 평균의 5배 이상
                anomalies.append({
                    'type': 'whale_wall',
                    'severity': min(wall['ratio'] * 10, 100),
                    'details': {
                        'side': wall['side'],
                        'price': wall['price'],
                        'quantity': wall['quantity'],
                        'ratio': wall['ratio']
                    }
                })

        # 3. 스프레드 급등 (이전 대비)
        if previous and current['spread'] > 0:
            if previous['spread'] > 0:
                spread_change = (current['spread'] - previous['spread']) / previous['spread']
                if spread_change > 0.5:  # 50% 이상 증가
                    anomalies.append({
                        'type': 'spread_spike',
                        'severity': min(spread_change * 100, 100),
                        'details': {
                            'current_spread': current['spread'],
                            'previous_spread': previous['spread'],
                            'change_percent': spread_change * 100
                        }
                    })

        # 4. 물량 급증
        if previous:
            total_volume = current['bid_total_volume'] + current['ask_total_volume']
            prev_total_volume = previous['bid_total_volume'] + previous['ask_total_volume']

            if prev_total_volume > 0:
                volume_change = (total_volume - prev_total_volume) / prev_total_volume
                if volume_change > 1.0:  # 100% 이상 증가
                    anomalies.append({
                        'type': 'volume_surge',
                        'severity': min(volume_change * 50, 100),
                        'details': {
                            'current_volume': total_volume,
                            'previous_volume': prev_total_volume,
                            'change_percent': volume_change * 100
                        }
                    })

        return anomalies

    def save_to_db(self, symbol: str, orderbook: Dict, analysis: Dict):
        """데이터베이스에 저장"""
        try:
            # 호가창 스냅샷 저장
            snapshot = OrderbookSnapshot(
                symbol=symbol,
                timestamp=orderbook['timestamp'],
                bids=orderbook['bids'],
                asks=orderbook['asks'],
                bid_total_volume=Decimal(str(analysis['bid_total_volume'])),
                ask_total_volume=Decimal(str(analysis['ask_total_volume'])),
                imbalance_ratio=Decimal(str(analysis['imbalance_ratio'])),
                spread=Decimal(str(analysis['spread']))
            )
            self.db.add(snapshot)
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            self._log_error(f"DB 저장 실패: {str(e)}")

    def save_anomalies(self, symbol: str, anomalies: List[Dict], current_price: float):
        """이상 패턴 저장"""
        try:
            for anomaly in anomalies:
                anomaly_record = OrderbookAnomaly(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    anomaly_type=anomaly['type'],
                    severity=Decimal(str(anomaly['severity'])),
                    details=anomaly['details'],
                    price_before=Decimal(str(current_price)),
                    price_after=Decimal(str(current_price))  # 추후 업데이트
                )
                self.db.add(anomaly_record)

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            self._log_error(f"이상 패턴 저장 실패: {str(e)}")

    def run_collection_loop(self, symbols: List[str], interval: int = None):
        """
        지속적인 데이터 수집 루프
        Args:
            symbols: 수집할 코인 심볼 리스트
            interval: 수집 주기 (초), None이면 config 사용
        """
        interval = interval or config.ORDERBOOK_INTERVAL

        print(f"호가창 데이터 수집 시작: {symbols}, 주기: {interval}초")

        while True:
            try:
                for symbol in symbols:
                    # 호가창 수집
                    orderbook = self.collect_orderbook(symbol)
                    if not orderbook:
                        continue

                    # 분석
                    analysis = self.analyze_orderbook(orderbook)

                    # 이상 패턴 감지
                    previous = self.last_orderbooks.get(symbol)
                    anomalies = self.detect_anomalies(symbol, analysis, previous)

                    # 저장
                    self.save_to_db(symbol, orderbook, analysis)

                    if anomalies:
                        current_price = analysis['best_bid']
                        self.save_anomalies(symbol, anomalies, current_price)
                        print(f"[{symbol}] {len(anomalies)}개 이상 패턴 감지!")

                    # 현재 상태 저장
                    self.last_orderbooks[symbol] = analysis

                    # 디버그 출력
                    print(f"[{symbol}] 불균형: {analysis['imbalance_ratio']:.2f}, "
                          f"스프레드: {analysis['spread']:.0f}, "
                          f"벽: 매수{len(analysis['bid_walls'])} 매도{len(analysis['ask_walls'])}")

                time.sleep(interval)

            except KeyboardInterrupt:
                print("\n수집 중단됨")
                break
            except Exception as e:
                self._log_error(f"수집 루프 에러: {str(e)}")
                time.sleep(interval)

    def _log_error(self, message: str):
        """에러 로그 기록"""
        print(f"ERROR: {message}")
        try:
            log = SystemLog(
                log_level='ERROR',
                module='OrderbookCollector',
                message=message
            )
            self.db.add(log)
            self.db.commit()
        except:
            pass

    def __del__(self):
        """소멸자"""
        self.db.close()


# 실행 스크립트
if __name__ == "__main__":
    collector = OrderbookCollector()
    collector.run_collection_loop(config.TARGET_PAIRS, interval=1)
