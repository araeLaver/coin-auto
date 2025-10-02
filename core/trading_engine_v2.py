"""
완전히 작동하는 트레이딩 엔진 V2
모든 모듈을 통합하여 실제 자동매매 실행
"""

import time
import threading
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

from database import SessionLocal, TradingSignal, Position, Strategy, SystemLog, OHLCVData
from strategies import (
    OrderbookScalpingStrategy
)
from strategies.strategy_selector import StrategySelector
from core.risk_manager import RiskManager
from core.order_executor import OrderExecutor
from analysis.indicators import IndicatorEngine
from api import BithumbAPI
from utils.telegram_notifier import TelegramNotifier
import config


class TradingEngineV2:
    """완전히 작동하는 메인 트레이딩 엔진"""

    def __init__(self):
        self.db = SessionLocal()
        self.api = BithumbAPI()
        self.notifier = TelegramNotifier()

        # 전략 초기화
        self.strategies = self._initialize_strategies()

        # 핵심 모듈
        self.strategy_selector = StrategySelector()
        self.risk_manager = RiskManager()
        self.order_executor = OrderExecutor()
        self.indicator_engine = IndicatorEngine()

        # 캐시 (최근 데이터 저장)
        self.market_data_cache = {}
        self.indicators_cache = {}
        self.orderbook_cache = {}

        # 상태
        self.is_running = False
        self.symbols = config.TARGET_PAIRS

        # 데이터 수집 스레드
        self.data_threads = []

    def _initialize_strategies(self) -> Dict:
        """전략 초기화 - 초고속 실시간 스캘핑"""
        strategies = {}

        # 초고속 실시간 수익률 스캘핑 전략
        from strategies.hyper_scalping_strategy import HyperScalpingStrategy
        hyper_strategy = HyperScalpingStrategy()

        strategies[1] = {
            'instance': hyper_strategy,
            'name': 'Hyper Scalping',
            'type': 'ultra_fast'
        }

        return strategies

    def start_data_collection(self):
        """백그라운드에서 데이터 수집 시작"""
        self.is_running = True

        def collect_prices():
            """가격 데이터 지속 수집 (캐시 + DB 저장)"""
            from decimal import Decimal

            # 스레드 전용 DB 세션
            thread_db = SessionLocal()

            last_save_minute = None

            while self.is_running:
                try:
                    current_time = datetime.now()
                    current_minute = current_time.replace(second=0, microsecond=0)

                    for symbol in self.symbols:
                        ticker = self.api.get_ticker(symbol)
                        if ticker.get('status') == '0000':
                            data = ticker['data']
                            price = float(data.get('closing_price', 0))
                            volume = float(data.get('units_traded_24H', 0))

                            # 캐시 업데이트
                            self.market_data_cache[symbol] = {
                                'price': price,
                                'volume': volume,
                                'timestamp': current_time
                            }

                            # 1분마다 DB에 저장 (1분봉)
                            if last_save_minute != current_minute:
                                try:
                                    # 중복 체크
                                    exists = thread_db.query(OHLCVData).filter(
                                        OHLCVData.symbol == symbol,
                                        OHLCVData.timeframe == '1m',
                                        OHLCVData.timestamp == current_minute
                                    ).first()

                                    if not exists:
                                        ohlcv = OHLCVData(
                                            symbol=symbol,
                                            timeframe='1m',
                                            timestamp=current_minute,
                                            open=Decimal(str(price)),
                                            high=Decimal(str(price)),
                                            low=Decimal(str(price)),
                                            close=Decimal(str(price)),
                                            volume=Decimal(str(volume))
                                        )
                                        thread_db.add(ohlcv)
                                except Exception as e:
                                    print(f"  [DB 저장 에러] {symbol}: {str(e)}")

                    # 1분마다 커밋
                    if last_save_minute != current_minute:
                        try:
                            thread_db.commit()
                            print(f"  [DB 저장] 1분봉 {len(self.symbols)}개 코인 저장 완료")
                            last_save_minute = current_minute
                        except Exception as e:
                            print(f"  [DB 커밋 에러] {str(e)}")
                            thread_db.rollback()

                    time.sleep(5)  # 5초마다
                except Exception as e:
                    self._log_error(f"가격 수집 에러: {str(e)}")
                    time.sleep(5)

            # 스레드 종료 시 세션 닫기
            thread_db.close()

        def collect_orderbooks():
            """호가창 데이터 지속 수집"""
            while self.is_running:
                try:
                    for symbol in self.symbols:
                        orderbook = self.api.get_orderbook(symbol)
                        if orderbook.get('status') == '0000':
                            data = orderbook['data']
                            bids = data.get('bids', [])
                            asks = data.get('asks', [])

                            bid_total = sum(float(b['quantity']) for b in bids)
                            ask_total = sum(float(a['quantity']) for a in asks)

                            self.orderbook_cache[symbol] = {
                                'bids': bids,
                                'asks': asks,
                                'bid_total_volume': bid_total,
                                'ask_total_volume': ask_total,
                                'imbalance_ratio': bid_total / ask_total if ask_total > 0 else 1.0,
                                'best_bid': float(bids[0]['price']) if bids else 0,
                                'best_ask': float(asks[0]['price']) if asks else 0,
                                'spread': float(asks[0]['price']) - float(bids[0]['price']) if (bids and asks) else 0,
                                'timestamp': datetime.now()
                            }
                    time.sleep(1)  # 1초마다
                except Exception as e:
                    self._log_error(f"호가창 수집 에러: {str(e)}")
                    time.sleep(1)

        def calculate_indicators():
            """기술적 지표 지속 계산"""
            while self.is_running:
                try:
                    for symbol in self.symbols:
                        indicators = self.indicator_engine.calculate_all_indicators(symbol, '15m')
                        if indicators:
                            self.indicators_cache[symbol] = indicators
                    time.sleep(60)  # 60초마다
                except Exception as e:
                    self._log_error(f"지표 계산 에러: {str(e)}")
                    time.sleep(60)

        # 스레드 시작
        threads = [
            threading.Thread(target=collect_prices, daemon=True),
            threading.Thread(target=collect_orderbooks, daemon=True),
            threading.Thread(target=calculate_indicators, daemon=True)
        ]

        for thread in threads:
            thread.start()
            self.data_threads.append(thread)

        self._log_info("데이터 수집 백그라운드 스레드 시작")

    def generate_signal(self, symbol: str, strategy_id: int) -> Optional[Dict]:
        """특정 전략으로 시그널 생성"""

        if strategy_id not in self.strategies:
            return None

        strategy_info = self.strategies[strategy_id]
        strategy = strategy_info['instance']

        # 캐시에서 데이터 가져오기
        market_data_entry = self.market_data_cache.get(symbol)
        indicators = self.indicators_cache.get(symbol)
        orderbook = self.orderbook_cache.get(symbol)

        if not market_data_entry or not indicators:
            return None

        # 시장 데이터 준비
        market_data = {
            'current_price': market_data_entry['price'],
            'current_volume': market_data_entry['volume'],
            'orderbook': orderbook
        }

        try:
            # 전략 실행
            signal = strategy.generate_signal(symbol, market_data, indicators)

            if signal:
                # 시장 상황 계산
                market_conditions = {
                    'trend_strength': indicators.get('adx_14', 0),
                    'volatility': 0.05,  # 임시값
                    'volume_ratio': 1.0,
                    'orderbook_imbalance': orderbook.get('imbalance_ratio', 1.0) if orderbook else 1.0
                }

                # 유효성 검증
                if strategy.validate_signal(signal, market_conditions):
                    signal['strategy_id'] = strategy_id
                    signal['strategy_name'] = strategy_info['name']
                    return signal

        except Exception as e:
            self._log_error(f"시그널 생성 에러 ({strategy_info['name']}): {str(e)}")

        return None

    def execute_trading_cycle(self):
        """트레이딩 사이클 실행"""

        print(f"\n대상 코인: {len(self.symbols)}개")

        for symbol in self.symbols:
            try:
                # 1. 현재가 확인
                if symbol not in self.market_data_cache:
                    continue

                current_price = self.market_data_cache[symbol]['price']

                if current_price <= 0:
                    continue

                print(f"\n[{symbol}] 현재가: {current_price:,.0f}원")

                # 2. 기존 포지션 관리
                self._manage_positions(symbol, current_price)

                # 3. 리스크 체크
                if not self.risk_manager.check_daily_loss_limit():
                    print("  일일 손실 한도 초과 - 거래 중단")
                    continue

                if not self.risk_manager.check_max_open_positions():
                    print("  최대 포지션 수 도달")
                    continue

                # 4. 모든 전략에서 시그널 생성
                signals = []
                for strategy_id in self.strategies.keys():
                    signal = self.generate_signal(symbol, strategy_id)
                    if signal:
                        signals.append(signal)

                if not signals:
                    continue

                print(f"  시그널 {len(signals)}개 생성")

                # 5. 최적 시그널 선택
                best_signal = self._select_best_signal(signals)

                if not best_signal:
                    continue

                print(f"  최적 시그널: {best_signal['signal_type']} "
                      f"(전략: {best_signal['strategy_name']}, "
                      f"신뢰도: {best_signal['confidence']:.1%})")

                # 6. BUY 시그널만 처리 (SELL은 포지션 관리에서 처리)
                if best_signal['signal_type'] != 'BUY':
                    continue

                # 7. 계좌 잔고 확인
                balance = self.order_executor.get_account_balance()
                available_krw = balance.get('available_krw', 0)

                if available_krw < 10000:  # 최소 1만원
                    print(f"  잔고 부족: {available_krw:,.0f}원")
                    continue

                # 8. 리스크 검증
                is_valid, reason = self.risk_manager.validate_signal_risk(best_signal, available_krw)

                if not is_valid:
                    print(f"  리스크 검증 실패: {reason}")
                    continue

                # 9. 포지션 크기 계산
                position_size = self.risk_manager.calculate_position_size(best_signal, available_krw)

                print(f"  포지션 크기: {position_size:,.0f}원")

                # 10. 시그널 DB 저장
                signal_record = self._save_signal(best_signal, symbol)

                # 11. 주문 실행
                position = self.order_executor.execute_signal(signal_record, position_size)

                if position:
                    print(f"  ✓ 포지션 오픈 성공: {position.id}")

                    # 텔레그램 알림
                    self.notifier.notify_trade_open({
                        'symbol': symbol,
                        'position_type': position.position_type,
                        'entry_price': float(position.entry_price),
                        'quantity': float(position.quantity),
                        'investment': position_size,
                        'take_profit': float(position.take_profit),
                        'stop_loss': float(position.stop_loss),
                        'strategy_name': best_signal['strategy_name'],
                        'confidence': best_signal['confidence']
                    })

            except Exception as e:
                self._log_error(f"[{symbol}] 트레이딩 사이클 에러: {str(e)}")
                import traceback
                traceback.print_exc()

    def _manage_positions(self, symbol: str, current_price: float):
        """포지션 관리 및 자동 청산"""

        open_positions = self.db.query(Position).filter(
            Position.symbol == symbol,
            Position.status == 'OPEN'
        ).all()

        for position in open_positions:
            try:
                # 현재 손익 업데이트
                self.risk_manager.update_position_metrics(position, current_price)

                # 청산 여부 확인
                should_close, reason = self.risk_manager.should_close_position(position, current_price)

                if should_close:
                    success = self.order_executor.close_position(position, current_price, reason)

                    if success:
                        print(f"  ✓ 포지션 청산: {position.symbol} (이유: {reason})")

                        # 손익 계산
                        entry_price = float(position.entry_price)
                        quantity = float(position.quantity)

                        if position.position_type == 'LONG':
                            pnl = (current_price - entry_price) * quantity
                        else:
                            pnl = (entry_price - current_price) * quantity

                        pnl_percent = (pnl / (entry_price * quantity)) * 100

                        # 보유 시간
                        holding_time = (datetime.now() - position.opened_at).total_seconds() / 60
                        holding_time_str = f"{int(holding_time)}분" if holding_time < 60 else f"{holding_time/60:.1f}시간"

                        # 텔레그램 알림
                        self.notifier.notify_trade_close({
                            'symbol': symbol,
                            'position_type': position.position_type,
                            'entry_price': entry_price,
                            'exit_price': current_price,
                            'pnl': pnl,
                            'pnl_percent': pnl_percent,
                            'holding_time': holding_time_str,
                            'exit_reason': reason
                        })

            except Exception as e:
                self._log_error(f"포지션 관리 에러: {str(e)}")

    def _select_best_signal(self, signals: List[Dict]) -> Optional[Dict]:
        """최적 시그널 선택"""

        if not signals:
            return None

        # 신뢰도 * 강도로 점수 계산
        scored_signals = []

        for signal in signals:
            score = signal['confidence'] * (signal['strength'] / 100)
            scored_signals.append((score, signal))

        # 최고 점수 시그널
        scored_signals.sort(key=lambda x: x[0], reverse=True)
        return scored_signals[0][1]

    def _save_signal(self, signal: Dict, symbol: str) -> TradingSignal:
        """시그널 DB 저장"""

        signal_record = TradingSignal(
            strategy_id=signal.get('strategy_id'),
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
        """트레이딩 봇 실행"""

        self.is_running = True

        print("=" * 70)
        print("Auto Coin Trading V2 시작")
        print(f"모드: {'실전' if config.TRADE_MODE == 'live' else '페이퍼'}")
        print(f"대상: {', '.join(self.symbols)}")
        print(f"주기: {interval}초")
        print("=" * 70)

        # 텔레그램 알림
        self.notifier.notify_system_start()

        # 데이터 수집 시작
        self.start_data_collection()

        # 초기 데이터 로딩 대기
        print("\n초기 데이터 수집 중... (30초)")
        time.sleep(30)

        # 전략 가중치 계산
        self.strategy_selector.calculate_strategy_weights()

        cycle_count = 0

        while self.is_running:
            try:
                cycle_start = time.time()
                cycle_count += 1

                print(f"\n{'='*70}")
                print(f"[사이클 #{cycle_count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*70}")

                # 트레이딩 사이클 실행
                self.execute_trading_cycle()

                # 계좌 잔고 업데이트
                self.order_executor.update_account_balance()

                # 일일 성과 업데이트
                self.risk_manager.update_daily_performance()

                # 다음 사이클까지 대기
                elapsed = time.time() - cycle_start
                sleep_time = max(interval - elapsed, 1)

                print(f"\n다음 사이클까지 {sleep_time:.0f}초 대기...")
                time.sleep(sleep_time)

            except KeyboardInterrupt:
                print("\n\n트레이딩 봇 중단")
                self.is_running = False
                self.notifier.notify_system_stop()
                break

            except Exception as e:
                self._log_error(f"메인 루프 에러: {str(e)}")
                import traceback
                traceback.print_exc()
                time.sleep(interval)

    def stop(self):
        """트레이딩 봇 중단"""
        self.is_running = False

    def _log_info(self, message: str):
        """정보 로그"""
        print(f"[INFO] {message}")
        try:
            log = SystemLog(log_level='INFO', module='TradingEngineV2', message=message)
            self.db.add(log)
            self.db.commit()
        except:
            pass

    def _log_error(self, message: str):
        """에러 로그"""
        print(f"[ERROR] {message}")
        try:
            log = SystemLog(log_level='ERROR', module='TradingEngineV2', message=message)
            self.db.add(log)
            self.db.commit()
        except:
            pass

    def __del__(self):
        """소멸자"""
        self.is_running = False
        self.db.close()


if __name__ == "__main__":
    engine = TradingEngineV2()
    engine.run(interval=60)
