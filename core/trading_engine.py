"""
메인 트레이딩 엔진
모든 모듈을 통합하여 자동매매 실행
"""

import time
from typing import Dict, List
from datetime import datetime
from database import SessionLocal, TradingSignal, Position, Strategy
from strategies import (
    TrendFollowingStrategy,
    MeanReversionStrategy,
    MomentumBreakoutStrategy,
    OrderbookImbalanceStrategy
)
from strategies.strategy_selector import StrategySelector
from core.risk_manager import RiskManager
from core.order_executor import OrderExecutor
from collectors.orderbook_collector import OrderbookCollector
from collectors.price_collector import PriceCollector
from analysis.indicators import IndicatorEngine
from api import BithumbAPI
import config


class TradingEngine:
    """메인 트레이딩 엔진"""

    def __init__(self):
        self.db = SessionLocal()
        self.api = BithumbAPI()

        # 전략 초기화
        self.strategies = {
            'trend_following': TrendFollowingStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'momentum': MomentumBreakoutStrategy(),
            'microstructure': OrderbookImbalanceStrategy()
        }

        # 핵심 모듈
        self.strategy_selector = StrategySelector()
        self.risk_manager = RiskManager()
        self.order_executor = OrderExecutor()
        self.indicator_engine = IndicatorEngine()
        self.orderbook_collector = OrderbookCollector()
        self.price_collector = PriceCollector()

        # 상태
        self.is_running = False
        self.symbols = config.TARGET_PAIRS

    def analyze_market(self, symbol: str) -> Dict:
        """
        시장 분석
        Args:
            symbol: 코인 심볼
        Returns:
            시장 데이터 및 지표
        """
        # 현재가 조회
        ticker = self.price_collector.collect_ticker(symbol)
        if not ticker:
            return {}

        current_price = ticker['closing_price']
        current_volume = ticker['units_traded_24H']

        # 호가창 데이터
        orderbook_data = self.orderbook_collector.collect_orderbook(symbol)
        orderbook_analysis = None

        if orderbook_data:
            orderbook_analysis = self.orderbook_collector.analyze_orderbook(orderbook_data)

        # 기술적 지표
        indicators = self.indicator_engine.calculate_all_indicators(symbol, '15m')

        # 시장 상태 계산
        market_conditions = {
            'trend_strength': indicators.get('adx_14', 0) if indicators else 0,
            'volatility': ticker.get('fluctate_rate_24H', 0) / 100 if ticker else 0,
            'volume_ratio': current_volume / indicators.get('volume_sma_20', 1) if indicators and indicators.get('volume_sma_20') else 1.0,
            'orderbook_imbalance': orderbook_analysis.get('imbalance_ratio', 1.0) if orderbook_analysis else 1.0
        }

        return {
            'symbol': symbol,
            'current_price': current_price,
            'current_volume': current_volume,
            'orderbook': orderbook_analysis,
            'indicators': indicators,
            'market_conditions': market_conditions
        }

    def generate_signals(self, symbol: str) -> List[Dict]:
        """
        모든 전략으로부터 시그널 생성
        Args:
            symbol: 코인 심볼
        Returns:
            시그널 리스트
        """
        market_data = self.analyze_market(symbol)

        if not market_data or not market_data.get('indicators'):
            return []

        signals = []

        # 각 전략에서 시그널 생성
        for strategy_name, strategy in self.strategies.items():
            try:
                signal = strategy.generate_signal(
                    symbol,
                    market_data,
                    market_data['indicators']
                )

                if signal:
                    # 시그널 유효성 검증
                    if strategy.validate_signal(signal, market_data['market_conditions']):
                        signal['strategy_name'] = strategy_name
                        signals.append(signal)

            except Exception as e:
                print(f"전략 {strategy_name} 시그널 생성 실패: {str(e)}")

        return signals

    def select_best_signal(self, signals: List[Dict], symbol: str, market_conditions: Dict) -> Dict:
        """
        최적 시그널 선택
        Args:
            signals: 시그널 리스트
            symbol: 코인 심볼
            market_conditions: 시장 상황
        Returns:
            선택된 시그널
        """
        if not signals:
            return None

        # AI 기반 전략 선택
        best_strategy_id, confidence = self.strategy_selector.select_best_strategy(
            symbol,
            market_conditions
        )

        # 전략별 시그널 점수 계산
        scored_signals = []

        for signal in signals:
            # 기본 점수: 신뢰도 * 강도
            score = signal['confidence'] * (signal['strength'] / 100)

            # 전략 가중치 적용
            strategy_weight = self.strategy_selector.strategies_weights.get(
                signal.get('strategy_id'),
                0.25
            )
            score *= (1 + strategy_weight)

            scored_signals.append((score, signal))

        # 최고 점수 시그널 선택
        scored_signals.sort(key=lambda x: x[0], reverse=True)
        best_signal = scored_signals[0][1] if scored_signals else None

        return best_signal

    def execute_trading_cycle(self):
        """트레이딩 사이클 실행"""

        for symbol in self.symbols:
            try:
                # 1. 시장 분석
                market_data = self.analyze_market(symbol)
                if not market_data:
                    continue

                print(f"\n[{symbol}] 가격: {market_data['current_price']:,.0f}원")

                # 2. 기존 포지션 관리
                self.manage_positions(symbol, market_data['current_price'])

                # 3. 일일 손실 한도 체크
                if not self.risk_manager.check_daily_loss_limit():
                    print("일일 손실 한도 초과 - 거래 중단")
                    continue

                # 4. 최대 포지션 수 체크
                if not self.risk_manager.check_max_open_positions():
                    continue

                # 5. 시그널 생성
                signals = self.generate_signals(symbol)

                if not signals:
                    continue

                print(f"  시그널 {len(signals)}개 생성")

                # 6. 최적 시그널 선택
                best_signal = self.select_best_signal(
                    signals,
                    symbol,
                    market_data['market_conditions']
                )

                if not best_signal:
                    continue

                print(f"  최적 시그널: {best_signal['signal_type']} "
                      f"(신뢰도: {best_signal['confidence']:.2%}, "
                      f"강도: {best_signal['strength']:.0f})")

                # 7. 리스크 검증
                account_balance = self.order_executor.get_account_balance()
                is_valid, reason = self.risk_manager.validate_signal_risk(
                    best_signal,
                    account_balance.get('available_krw', 0)
                )

                if not is_valid:
                    print(f"  리스크 검증 실패: {reason}")
                    continue

                # 8. 포지션 크기 계산
                position_size = self.risk_manager.calculate_position_size(
                    best_signal,
                    account_balance.get('available_krw', 0)
                )

                print(f"  포지션 크기: {position_size:,.0f}원")

                # 9. 시그널 DB 저장
                signal_record = self.save_signal(best_signal, symbol)

                # 10. 주문 실행
                if best_signal['signal_type'] == 'BUY':
                    position = self.order_executor.execute_signal(signal_record, position_size)

                    if position:
                        print(f"  ✓ 포지션 오픈 성공: {position.id}")

            except Exception as e:
                print(f"[{symbol}] 트레이딩 사이클 에러: {str(e)}")

    def manage_positions(self, symbol: str, current_price: float):
        """기존 포지션 관리"""
        open_positions = self.db.query(Position).filter(
            Position.symbol == symbol,
            Position.status == 'OPEN'
        ).all()

        for position in open_positions:
            # 포지션 지표 업데이트
            self.risk_manager.update_position_metrics(position, current_price)

            # 청산 여부 확인
            should_close, reason = self.risk_manager.should_close_position(position, current_price)

            if should_close:
                success = self.order_executor.close_position(position, current_price, reason)
                if success:
                    print(f"  포지션 청산: {position.symbol} (이유: {reason})")

    def save_signal(self, signal: Dict, symbol: str) -> TradingSignal:
        """시그널 DB 저장"""
        from decimal import Decimal

        # 전략 ID 조회
        strategy = self.db.query(Strategy).filter(
            Strategy.name == signal.get('strategy_name', '')
        ).first()

        signal_record = TradingSignal(
            strategy_id=strategy.id if strategy else None,
            symbol=symbol,
            timestamp=datetime.now(),
            signal_type=signal['signal_type'],
            strength=Decimal(str(signal['strength'])),
            entry_price=Decimal(str(signal['entry_price'])),
            stop_loss=Decimal(str(signal['stop_loss'])),
            take_profit=Decimal(str(signal['take_profit'])),
            confidence=Decimal(str(signal['confidence'])),
            reasoning=signal.get('reasoning', ''),
            metadata=signal.get('metadata', {})
        )

        self.db.add(signal_record)
        self.db.commit()
        self.db.refresh(signal_record)

        return signal_record

    def run(self, interval: int = 60):
        """
        트레이딩 봇 실행
        Args:
            interval: 사이클 간격 (초)
        """
        self.is_running = True

        print("=" * 70)
        print("Auto Coin Trading 시작")
        print(f"모드: {'실전' if config.TRADE_MODE == 'live' else '페이퍼'}")
        print(f"대상: {', '.join(self.symbols)}")
        print(f"주기: {interval}초")
        print("=" * 70)

        # 전략 가중치 계산
        self.strategy_selector.calculate_strategy_weights()

        while self.is_running:
            try:
                cycle_start = time.time()

                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 트레이딩 사이클 시작")

                # 트레이딩 사이클 실행
                self.execute_trading_cycle()

                # 계좌 잔고 업데이트
                self.order_executor.update_account_balance()

                # 일일 성과 업데이트
                self.risk_manager.update_daily_performance()

                # 다음 사이클까지 대기
                elapsed = time.time() - cycle_start
                sleep_time = max(interval - elapsed, 1)

                print(f"다음 사이클까지 {sleep_time:.0f}초 대기...")
                time.sleep(sleep_time)

            except KeyboardInterrupt:
                print("\n트레이딩 봇 중단")
                self.is_running = False
                break

            except Exception as e:
                print(f"메인 루프 에러: {str(e)}")
                time.sleep(interval)

    def stop(self):
        """트레이딩 봇 중단"""
        self.is_running = False

    def __del__(self):
        """소멸자"""
        self.db.close()


if __name__ == "__main__":
    engine = TradingEngine()
    engine.run(interval=60)  # 60초 주기
