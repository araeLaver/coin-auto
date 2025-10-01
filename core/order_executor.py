"""
자동 주문 실행 모듈
시그널 -> 실제 거래소 주문 변환 및 실행
"""

import time
from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime
from api import BithumbAPI
from database import SessionLocal, Position, Order, TradingSignal, SystemLog
import config


class OrderExecutor:
    """주문 실행 시스템"""

    def __init__(self):
        self.api = BithumbAPI()
        self.db = SessionLocal()
        self.is_live_mode = (config.TRADE_MODE == 'live')

    def execute_signal(self, signal: TradingSignal, position_size_krw: float) -> Optional[Position]:
        """
        시그널 실행
        Args:
            signal: 트레이딩 시그널
            position_size_krw: 포지션 크기 (KRW)
        Returns:
            생성된 포지션 또는 None
        """
        try:
            symbol = signal.symbol
            signal_type = signal.signal_type
            entry_price = float(signal.entry_price)

            # 수량 계산
            quantity = position_size_krw / entry_price

            # 최소 주문 수량 체크 (빗썸 기준)
            min_order_amount = 1000  # 최소 1,000원
            if position_size_krw < min_order_amount:
                self._log_error(f"주문 금액 부족: {position_size_krw:.0f}원 < {min_order_amount}원")
                return None

            # 주문 실행
            if self.is_live_mode:
                order_result = self._execute_live_order(symbol, signal_type, quantity, entry_price)
            else:
                order_result = self._execute_paper_order(symbol, signal_type, quantity, entry_price)

            if not order_result:
                return None

            # 포지션 생성
            position = Position(
                symbol=symbol,
                strategy_id=signal.strategy_id,
                signal_id=signal.id,
                position_type='LONG' if signal_type == 'BUY' else 'SHORT',
                entry_price=signal.entry_price,
                quantity=Decimal(str(quantity)),
                current_price=signal.entry_price,
                unrealized_pnl=Decimal('0'),
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                status='OPEN',
                opened_at=datetime.now()
            )

            self.db.add(position)
            self.db.commit()
            self.db.refresh(position)

            # 주문 기록
            order = Order(
                position_id=position.id,
                order_id=order_result.get('order_id', f"paper_{int(time.time())}"),
                symbol=symbol,
                order_type='MARKET',
                side='BUY' if signal_type == 'BUY' else 'SELL',
                price=signal.entry_price,
                quantity=Decimal(str(quantity)),
                filled_quantity=Decimal(str(quantity)),
                status='FILLED',
                executed_at=datetime.now()
            )

            self.db.add(order)
            self.db.commit()

            self._log_info(f"포지션 오픈: {symbol} {signal_type} {quantity:.8f} @ {entry_price:.0f}원")

            return position

        except Exception as e:
            self._log_error(f"시그널 실행 실패: {str(e)}")
            return None

    def _execute_live_order(self, symbol: str, side: str, quantity: float, price: float) -> Optional[Dict]:
        """실제 거래소 주문"""
        try:
            order_type = 'bid' if side == 'BUY' else 'ask'

            # 시장가 주문 (빗썸은 price=None이면 시장가)
            result = self.api.place_order(
                symbol=symbol,
                order_type=order_type,
                quantity=quantity,
                price=None  # 시장가
            )

            if result.get('status') == '0000':
                return {
                    'order_id': result.get('order_id'),
                    'filled_price': price,
                    'filled_quantity': quantity
                }
            else:
                self._log_error(f"주문 실패: {result.get('message')}")
                return None

        except Exception as e:
            self._log_error(f"거래소 주문 에러: {str(e)}")
            return None

    def _execute_paper_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict:
        """페이퍼 트레이딩 (모의 주문)"""
        return {
            'order_id': f"paper_{symbol}_{int(time.time())}",
            'filled_price': price,
            'filled_quantity': quantity
        }

    def close_position(self, position: Position, current_price: float, reason: str) -> bool:
        """
        포지션 청산
        Args:
            position: 청산할 포지션
            current_price: 현재 가격
            reason: 청산 이유
        Returns:
            성공 여부
        """
        try:
            symbol = position.symbol
            quantity = float(position.quantity)
            entry_price = float(position.entry_price)

            # 청산 주문 (포지션과 반대 방향)
            side = 'SELL' if position.position_type == 'LONG' else 'BUY'

            if self.is_live_mode:
                order_result = self._execute_live_order(symbol, side, quantity, current_price)
            else:
                order_result = self._execute_paper_order(symbol, side, quantity, current_price)

            if not order_result:
                return False

            # 손익 계산
            if position.position_type == 'LONG':
                pnl = (current_price - entry_price) * quantity
            else:
                pnl = (entry_price - current_price) * quantity

            pnl_percent = (pnl / (entry_price * quantity)) * 100 if (entry_price * quantity) > 0 else 0

            # 보유 시간 계산
            holding_time = (datetime.now() - position.opened_at).total_seconds() / 60  # 분

            # 포지션 업데이트
            position.status = 'CLOSED'
            position.closed_at = datetime.now()
            position.current_price = Decimal(str(current_price))
            position.unrealized_pnl = Decimal(str(pnl))

            # 거래 내역 생성
            from database import Trade

            trade = Trade(
                position_id=position.id,
                strategy_id=position.strategy_id,
                symbol=symbol,
                entry_price=position.entry_price,
                exit_price=Decimal(str(current_price)),
                quantity=position.quantity,
                pnl=Decimal(str(pnl)),
                pnl_percent=Decimal(str(pnl_percent)),
                holding_time_minutes=int(holding_time),
                exit_reason=reason,
                opened_at=position.opened_at,
                closed_at=datetime.now()
            )

            self.db.add(trade)

            # 청산 주문 기록
            order = Order(
                position_id=position.id,
                order_id=order_result.get('order_id'),
                symbol=symbol,
                order_type='MARKET',
                side=side,
                price=Decimal(str(current_price)),
                quantity=Decimal(str(quantity)),
                filled_quantity=Decimal(str(quantity)),
                status='FILLED',
                executed_at=datetime.now()
            )

            self.db.add(order)
            self.db.commit()

            self._log_info(f"포지션 청산: {symbol} {side} {quantity:.8f} @ {current_price:.0f}원 | "
                          f"손익: {pnl:,.0f}원 ({pnl_percent:+.2f}%) | 이유: {reason}")

            return True

        except Exception as e:
            self._log_error(f"포지션 청산 실패: {str(e)}")
            return False

    def get_account_balance(self) -> Dict:
        """계좌 잔고 조회"""
        try:
            if self.is_live_mode:
                result = self.api.get_balance('ALL')

                if result.get('status') == '0000':
                    data = result.get('data', {})
                    total_krw = float(data.get('total_krw', 0))
                    available_krw = float(data.get('available_krw', 0))

                    return {
                        'total_krw': total_krw,
                        'available_krw': available_krw,
                        'total_crypto_value': 0,  # TODO: 암호화폐 평가
                        'total_value': total_krw
                    }

            # 페이퍼 트레이딩: DB에서 조회
            from database import AccountBalance

            latest = self.db.query(AccountBalance).order_by(
                AccountBalance.timestamp.desc()
            ).first()

            if latest:
                return {
                    'total_krw': float(latest.total_krw),
                    'available_krw': float(latest.available_krw),
                    'total_crypto_value': float(latest.total_crypto_value),
                    'total_value': float(latest.total_value)
                }

            # 초기 자본
            return {
                'total_krw': config.INITIAL_CAPITAL,
                'available_krw': config.INITIAL_CAPITAL,
                'total_crypto_value': 0,
                'total_value': config.INITIAL_CAPITAL
            }

        except Exception as e:
            self._log_error(f"잔고 조회 실패: {str(e)}")
            return {}

    def update_account_balance(self):
        """계좌 잔고 업데이트"""
        try:
            balance = self.get_account_balance()

            if not balance:
                return

            # 오픈 포지션 평가
            open_positions = self.db.query(Position).filter(Position.status == 'OPEN').all()

            positions_value = 0
            unrealized_pnl = 0

            for pos in open_positions:
                current_price = float(pos.current_price) if pos.current_price else float(pos.entry_price)
                quantity = float(pos.quantity)
                positions_value += current_price * quantity

                if pos.unrealized_pnl:
                    unrealized_pnl += float(pos.unrealized_pnl)

            from database import AccountBalance

            balance_record = AccountBalance(
                timestamp=datetime.now(),
                total_krw=Decimal(str(balance.get('total_krw', 0))),
                total_crypto_value=Decimal(str(positions_value)),
                total_value=Decimal(str(balance.get('total_value', 0) + positions_value)),
                available_krw=Decimal(str(balance.get('available_krw', 0))),
                positions_value=Decimal(str(positions_value)),
                unrealized_pnl=Decimal(str(unrealized_pnl))
            )

            self.db.add(balance_record)
            self.db.commit()

        except Exception as e:
            self._log_error(f"잔고 업데이트 실패: {str(e)}")

    def _log_info(self, message: str):
        """정보 로그"""
        print(f"[OrderExecutor] {message}")
        log = SystemLog(log_level='INFO', module='OrderExecutor', message=message)
        self.db.add(log)
        self.db.commit()

    def _log_error(self, message: str):
        """에러 로그"""
        print(f"[OrderExecutor ERROR] {message}")
        log = SystemLog(log_level='ERROR', module='OrderExecutor', message=message)
        self.db.add(log)
        self.db.commit()

    def __del__(self):
        """소멸자"""
        self.db.close()
