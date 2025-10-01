"""
리스크 관리 시스템
손절/익절, 포지션 사이징, 일일 손실 한도 관리
"""

from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal
from database import SessionLocal, Position, DailyPerformance, AccountBalance, SystemLog
import config


class RiskManager:
    """리스크 관리 시스템"""

    def __init__(self):
        self.db = SessionLocal()
        self.daily_pnl = 0
        self.starting_balance = 0
        self.is_trading_paused = False

    def check_daily_loss_limit(self) -> bool:
        """
        일일 손실 한도 체크
        Returns:
            거래 가능 여부
        """
        today = date.today()

        daily_perf = self.db.query(DailyPerformance).filter(
            DailyPerformance.date == today
        ).first()

        if daily_perf:
            loss_percent = abs(float(daily_perf.pnl_percent))
            if loss_percent >= config.MAX_DAILY_LOSS * 100:
                self.is_trading_paused = True
                self._log_warning(f"일일 손실 한도 초과: {loss_percent:.2f}%")
                return False

        return True

    def calculate_position_size(self,
                               signal: Dict,
                               account_balance: float,
                               risk_per_trade: float = None) -> float:
        """
        포지션 사이즈 계산 (Kelly Criterion 기반)
        Args:
            signal: 트레이딩 시그널
            account_balance: 계좌 잔고
            risk_per_trade: 거래당 리스크 (기본값: config)
        Returns:
            투자 금액 (KRW)
        """
        risk_per_trade = risk_per_trade or config.MAX_POSITION_SIZE

        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)

        if entry_price <= 0 or stop_loss <= 0:
            return 0

        # 손실 거리 계산
        if signal['signal_type'] == 'BUY':
            loss_distance = abs(entry_price - stop_loss) / entry_price
        else:
            loss_distance = abs(stop_loss - entry_price) / entry_price

        if loss_distance <= 0:
            return 0

        # 기본 포지션 사이즈
        base_position = account_balance * risk_per_trade

        # 신뢰도 기반 조정
        confidence = signal.get('confidence', 0.5)
        adjusted_position = base_position * confidence

        # 손실 거리 기반 조정 (리스크가 크면 포지션 축소)
        risk_adjusted = adjusted_position * (1 / (1 + loss_distance * 10))

        # 최대/최소 제한
        max_position = account_balance * 0.3  # 최대 30%
        min_position = account_balance * 0.01  # 최소 1%

        final_position = max(min(risk_adjusted, max_position), min_position)

        return final_position

    def check_max_open_positions(self) -> bool:
        """
        최대 동시 보유 포지션 수 체크
        Returns:
            추가 포지션 가능 여부
        """
        open_positions = self.db.query(Position).filter(
            Position.status == 'OPEN'
        ).count()

        if open_positions >= config.MAX_OPEN_POSITIONS:
            self._log_info(f"최대 포지션 수 도달: {open_positions}/{config.MAX_OPEN_POSITIONS}")
            return False

        return True

    def should_close_position(self, position: Position, current_price: float) -> tuple[bool, str]:
        """
        포지션 청산 여부 결정
        Args:
            position: 포지션
            current_price: 현재 가격
        Returns:
            (청산 여부, 이유)
        """
        entry_price = float(position.entry_price)
        stop_loss = float(position.stop_loss) if position.stop_loss else None
        take_profit = float(position.take_profit) if position.take_profit else None

        # 손절가 체크
        if stop_loss:
            if position.position_type == 'LONG':
                if current_price <= stop_loss:
                    return True, 'STOP_LOSS'
            else:  # SHORT
                if current_price >= stop_loss:
                    return True, 'STOP_LOSS'

        # 익절가 체크
        if take_profit:
            if position.position_type == 'LONG':
                if current_price >= take_profit:
                    return True, 'TAKE_PROFIT'
            else:  # SHORT
                if current_price <= take_profit:
                    return True, 'TAKE_PROFIT'

        # 트레일링 스톱 (수익이 5% 이상이면 손절가 조정)
        pnl_percent = self.calculate_pnl_percent(position, current_price)

        if pnl_percent > 5:  # 5% 이상 수익
            # 손절가를 진입가로 이동 (손실 방지)
            new_stop_loss = entry_price * 1.01  # 진입가 + 1%

            if position.position_type == 'LONG':
                if stop_loss and new_stop_loss > stop_loss:
                    position.stop_loss = Decimal(str(new_stop_loss))
                    self.db.commit()
                    self._log_info(f"트레일링 스톱 조정: {position.symbol} {new_stop_loss:.2f}")

        # 장기 보유 체크 (24시간 이상)
        holding_hours = (datetime.now() - position.opened_at).total_seconds() / 3600

        if holding_hours > 24:
            # 24시간 보유했는데 손실이면 청산
            if pnl_percent < -1:
                return True, 'TIMEOUT_LOSS'

        return False, ''

    def calculate_pnl_percent(self, position: Position, current_price: float) -> float:
        """손익률 계산"""
        entry_price = float(position.entry_price)
        quantity = float(position.quantity)

        if position.position_type == 'LONG':
            pnl = (current_price - entry_price) * quantity
        else:  # SHORT
            pnl = (entry_price - current_price) * quantity

        investment = entry_price * quantity
        pnl_percent = (pnl / investment * 100) if investment > 0 else 0

        return pnl_percent

    def update_position_metrics(self, position: Position, current_price: float):
        """포지션 지표 업데이트"""
        entry_price = float(position.entry_price)
        quantity = float(position.quantity)

        if position.position_type == 'LONG':
            pnl = (current_price - entry_price) * quantity
        else:
            pnl = (entry_price - current_price) * quantity

        position.current_price = Decimal(str(current_price))
        position.unrealized_pnl = Decimal(str(pnl))
        position.updated_at = datetime.now()

        self.db.commit()

    def validate_signal_risk(self, signal: Dict, account_balance: float) -> tuple[bool, str]:
        """
        시그널 리스크 검증
        Args:
            signal: 트레이딩 시그널
            account_balance: 계좌 잔고
        Returns:
            (유효 여부, 거부 이유)
        """
        # 1. 일일 손실 한도 체크
        if not self.check_daily_loss_limit():
            return False, "일일 손실 한도 초과"

        # 2. 최대 포지션 수 체크
        if not self.check_max_open_positions():
            return False, "최대 포지션 수 도달"

        # 3. 손절/익절 비율 체크 (최소 1:1.5 권장)
        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)
        take_profit = signal.get('take_profit', 0)

        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            return False, "손절/익절 가격 오류"

        if signal['signal_type'] == 'BUY':
            loss_distance = abs(entry_price - stop_loss)
            profit_distance = abs(take_profit - entry_price)
        else:
            loss_distance = abs(stop_loss - entry_price)
            profit_distance = abs(entry_price - take_profit)

        risk_reward_ratio = profit_distance / loss_distance if loss_distance > 0 else 0

        if risk_reward_ratio < 1.2:  # 최소 1:1.2
            return False, f"리스크/보상 비율 부족: {risk_reward_ratio:.2f}"

        # 4. 포지션 크기 체크
        position_size = self.calculate_position_size(signal, account_balance)

        if position_size < account_balance * 0.01:
            return False, "포지션 크기 너무 작음"

        if position_size > account_balance * 0.3:
            return False, "포지션 크기 너무 큼"

        # 5. 신뢰도 체크
        confidence = signal.get('confidence', 0)
        if confidence < 0.6:
            return False, f"신뢰도 부족: {confidence:.2f}"

        return True, ""

    def update_daily_performance(self):
        """일일 성과 업데이트"""
        today = date.today()

        # 오늘의 모든 거래 조회
        from database import Trade

        today_start = datetime.combine(today, datetime.min.time())
        today_trades = self.db.query(Trade).filter(
            Trade.closed_at >= today_start
        ).all()

        total_trades = len(today_trades)
        winning_trades = sum(1 for t in today_trades if float(t.pnl) > 0)
        losing_trades = total_trades - winning_trades
        total_pnl = sum(float(t.pnl) for t in today_trades)

        # 계좌 잔고 조회
        latest_balance = self.db.query(AccountBalance).order_by(
            AccountBalance.timestamp.desc()
        ).first()

        if latest_balance:
            starting_balance = float(latest_balance.total_value) - total_pnl
            ending_balance = float(latest_balance.total_value)
            pnl_percent = (total_pnl / starting_balance * 100) if starting_balance > 0 else 0
        else:
            starting_balance = config.INITIAL_CAPITAL
            ending_balance = starting_balance + total_pnl
            pnl_percent = (total_pnl / starting_balance * 100) if starting_balance > 0 else 0

        # DB 업데이트
        daily_perf = self.db.query(DailyPerformance).filter(
            DailyPerformance.date == today
        ).first()

        if daily_perf:
            daily_perf.ending_balance = Decimal(str(ending_balance))
            daily_perf.total_pnl = Decimal(str(total_pnl))
            daily_perf.pnl_percent = Decimal(str(pnl_percent))
            daily_perf.total_trades = total_trades
            daily_perf.winning_trades = winning_trades
            daily_perf.losing_trades = losing_trades
            daily_perf.is_trading_paused = self.is_trading_paused
        else:
            daily_perf = DailyPerformance(
                date=today,
                starting_balance=Decimal(str(starting_balance)),
                ending_balance=Decimal(str(ending_balance)),
                total_pnl=Decimal(str(total_pnl)),
                pnl_percent=Decimal(str(pnl_percent)),
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                is_trading_paused=self.is_trading_paused
            )
            self.db.add(daily_perf)

        self.db.commit()

    def _log_info(self, message: str):
        """정보 로그"""
        log = SystemLog(log_level='INFO', module='RiskManager', message=message)
        self.db.add(log)
        self.db.commit()

    def _log_warning(self, message: str):
        """경고 로그"""
        log = SystemLog(log_level='WARNING', module='RiskManager', message=message)
        self.db.add(log)
        self.db.commit()

    def __del__(self):
        """소멸자"""
        self.db.close()
