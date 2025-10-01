"""
전략 베이스 클래스
모든 전략은 이 클래스를 상속받아 구현
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
import pandas as pd


class BaseStrategy(ABC):
    """전략 추상 베이스 클래스"""

    def __init__(self, name: str, strategy_type: str, parameters: Dict = None):
        self.name = name
        self.strategy_type = strategy_type
        self.parameters = parameters or {}
        self.signals = []
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0,
            'win_rate': 0
        }

    @abstractmethod
    def generate_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """
        매매 시그널 생성
        Args:
            symbol: 코인 심볼
            market_data: 시장 데이터 (가격, 거래량 등)
            indicators: 기술적 지표
        Returns:
            시그널 딕셔너리 또는 None
            {
                'signal_type': 'BUY' | 'SELL' | 'HOLD',
                'strength': 0-100,
                'confidence': 0-1,
                'entry_price': float,
                'stop_loss': float,
                'take_profit': float,
                'position_size': float,
                'reasoning': str
            }
        """
        pass

    @abstractmethod
    def validate_signal(self, signal: Dict, market_conditions: Dict) -> bool:
        """
        시그널 유효성 검증
        Args:
            signal: 생성된 시그널
            market_conditions: 시장 상황
        Returns:
            유효 여부
        """
        pass

    def calculate_position_size(self, capital: float, risk_percent: float, stop_loss_distance: float) -> float:
        """
        포지션 사이즈 계산
        Args:
            capital: 가용 자본
            risk_percent: 리스크 비율 (0-1)
            stop_loss_distance: 손절가까지 거리 (%)
        Returns:
            투자 금액
        """
        if stop_loss_distance <= 0:
            return capital * 0.1  # 기본 10%

        risk_amount = capital * risk_percent
        position_size = risk_amount / stop_loss_distance

        # 최대 포지션 제한
        max_position = capital * 0.3  # 최대 30%
        return min(position_size, max_position)

    def update_performance(self, trade_result: Dict):
        """성과 업데이트"""
        self.performance['total_trades'] += 1

        pnl = trade_result.get('pnl', 0)
        self.performance['total_pnl'] += pnl

        if pnl > 0:
            self.performance['winning_trades'] += 1
        else:
            self.performance['losing_trades'] += 1

        if self.performance['total_trades'] > 0:
            self.performance['win_rate'] = (
                self.performance['winning_trades'] / self.performance['total_trades']
            )

    def get_performance_summary(self) -> Dict:
        """성과 요약 반환"""
        return {
            'strategy_name': self.name,
            'strategy_type': self.strategy_type,
            **self.performance
        }
