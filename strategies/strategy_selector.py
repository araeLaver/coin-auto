"""
AI 기반 전략 선택기
각 전략의 성과를 학습하고 최적의 전략을 선택
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sklearn.linear_model import LogisticRegression
from database import SessionLocal, Strategy, StrategyPerformance, Trade
import pickle
import os


class StrategySelector:
    """AI 기반 전략 선택 및 가중치 관리"""

    def __init__(self):
        self.db = SessionLocal()
        self.strategies_weights = {}  # {strategy_id: weight}
        self.model = None
        self.model_path = 'models/strategy_selector.pkl'

    def calculate_strategy_weights(self) -> Dict[int, float]:
        """
        각 전략의 가중치 계산
        최근 성과 기반
        """
        # 최근 30일 성과 조회
        cutoff_date = datetime.now() - timedelta(days=30)

        strategies = self.db.query(Strategy).filter(Strategy.is_active == True).all()

        weights = {}
        total_score = 0

        for strategy in strategies:
            # 최근 거래 성과 조회
            trades = self.db.query(Trade).filter(
                Trade.strategy_id == strategy.id,
                Trade.closed_at >= cutoff_date
            ).all()

            if not trades:
                weights[strategy.id] = 0.2  # 기본 가중치
                total_score += 0.2
                continue

            # 성과 지표 계산
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if float(t.pnl) > 0)
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            avg_pnl = sum(float(t.pnl) for t in trades) / total_trades if total_trades > 0 else 0

            # 샤프 비율 근사
            pnl_std = np.std([float(t.pnl) for t in trades]) if len(trades) > 1 else 1
            sharpe = (avg_pnl / pnl_std) if pnl_std > 0 else 0

            # 종합 점수 계산
            score = (
                win_rate * 0.4 +  # 승률 40%
                min(sharpe / 2, 0.5) * 0.3 +  # 샤프 비율 30%
                min(avg_pnl / 100000, 0.5) * 0.3  # 평균 수익 30%
            )

            weights[strategy.id] = max(score, 0.1)  # 최소 0.1
            total_score += weights[strategy.id]

        # 정규화 (합계 1.0)
        if total_score > 0:
            for strategy_id in weights:
                weights[strategy_id] /= total_score

        self.strategies_weights = weights
        return weights

    def select_best_strategy(self, symbol: str, market_conditions: Dict) -> Tuple[int, float]:
        """
        현재 시장 상황에 가장 적합한 전략 선택
        Args:
            symbol: 코인 심볼
            market_conditions: 시장 상황 데이터
        Returns:
            (strategy_id, confidence)
        """
        if not self.strategies_weights:
            self.calculate_strategy_weights()

        # 시장 상황 분석
        trend_strength = market_conditions.get('trend_strength', 0)  # ADX
        volatility = market_conditions.get('volatility', 0)
        volume_ratio = market_conditions.get('volume_ratio', 1.0)
        orderbook_imbalance = market_conditions.get('orderbook_imbalance', 1.0)

        strategies = self.db.query(Strategy).filter(Strategy.is_active == True).all()

        # 각 전략 적합도 계산
        scores = {}

        for strategy in strategies:
            base_weight = self.strategies_weights.get(strategy.id, 0.25)

            # 전략 타입별 시장 적합도
            if strategy.strategy_type == 'trend_following':
                # 추세 전략: 강한 추세, 낮은 변동성
                market_fit = min(trend_strength / 30, 1.0) * 0.7 + (1 - min(volatility * 10, 1.0)) * 0.3

            elif strategy.strategy_type == 'mean_reversion':
                # 평균 회귀: 약한 추세, 높은 변동성
                market_fit = (1 - min(trend_strength / 30, 1.0)) * 0.6 + min(volatility * 10, 1.0) * 0.4

            elif strategy.strategy_type == 'momentum':
                # 모멘텀: 높은 거래량, 중간 변동성
                market_fit = min(volume_ratio / 2, 1.0) * 0.6 + min(volatility * 5, 1.0) * 0.4

            elif strategy.strategy_type == 'microstructure':
                # 호가창: 높은 불균형, 높은 유동성
                imbalance_score = abs(orderbook_imbalance - 1.0)
                market_fit = min(imbalance_score, 1.0) * 0.7 + min(volume_ratio / 1.5, 1.0) * 0.3

            else:
                market_fit = 0.5

            # 최종 점수 = 과거 성과 * 시장 적합도
            scores[strategy.id] = base_weight * market_fit

        # 최고 점수 전략 선택
        if scores:
            best_strategy_id = max(scores, key=scores.get)
            confidence = scores[best_strategy_id]
            return best_strategy_id, confidence

        return None, 0

    def train_model(self):
        """
        머신러닝 모델 학습
        과거 시장 상황과 전략 성과 데이터 활용
        """
        # 최근 90일 데이터
        cutoff_date = datetime.now() - timedelta(days=90)

        trades = self.db.query(Trade).filter(Trade.closed_at >= cutoff_date).all()

        if len(trades) < 50:
            print("학습 데이터 부족 (최소 50개 거래 필요)")
            return

        # 특징 벡터 생성
        X = []  # [trend_strength, volatility, volume_ratio, ...]
        y = []  # 수익 여부 (1: 수익, 0: 손실)

        for trade in trades:
            # TODO: 거래 당시의 시장 상황 데이터 필요
            # 현재는 간단한 버전
            features = [
                float(trade.holding_time_minutes) / 60,  # 보유 시간
                1 if trade.pnl > 0 else 0,  # 수익 여부
            ]
            X.append(features)
            y.append(1 if float(trade.pnl) > 0 else 0)

        if len(X) < 50:
            return

        # 로지스틱 회귀 모델 학습
        self.model = LogisticRegression()
        self.model.fit(X, y)

        # 모델 저장
        os.makedirs('models', exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)

        print(f"모델 학습 완료: {len(X)}개 샘플")

    def load_model(self):
        """저장된 모델 로드"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print("모델 로드 완료")
        else:
            print("저장된 모델 없음")

    def update_strategy_performance(self, strategy_id: int, symbol: str):
        """전략 성과 업데이트"""
        cutoff_date = datetime.now() - timedelta(days=30)

        trades = self.db.query(Trade).filter(
            Trade.strategy_id == strategy_id,
            Trade.symbol == symbol,
            Trade.closed_at >= cutoff_date
        ).all()

        if not trades:
            return

        total_trades = len(trades)
        profitable_trades = sum(1 for t in trades if float(t.pnl) > 0)
        total_pnl = sum(float(t.pnl) for t in trades)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0

        # 샤프 비율 계산
        pnls = [float(t.pnl) for t in trades]
        avg_pnl = np.mean(pnls)
        std_pnl = np.std(pnls)
        sharpe_ratio = (avg_pnl / std_pnl) if std_pnl > 0 else 0

        # MDD 계산
        cumulative = np.cumsum(pnls)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0

        # DB 저장
        perf = StrategyPerformance(
            strategy_id=strategy_id,
            symbol=symbol,
            timestamp=datetime.now(),
            win_rate=win_rate,
            total_trades=total_trades,
            profitable_trades=profitable_trades,
            total_pnl=total_pnl,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=abs(max_drawdown),
            current_weight=self.strategies_weights.get(strategy_id, 0.25)
        )

        self.db.add(perf)
        self.db.commit()

    def __del__(self):
        """소멸자"""
        self.db.close()


if __name__ == "__main__":
    selector = StrategySelector()
    weights = selector.calculate_strategy_weights()
    print("전략 가중치:", weights)
