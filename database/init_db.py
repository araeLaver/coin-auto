"""
데이터베이스 초기화 스크립트
전용 스키마 생성 및 기본 전략 데이터 삽입
"""

import sys
import os

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from database.models import init_db, SessionLocal, Strategy
from datetime import datetime

def create_default_strategies():
    """기본 전략 데이터 생성"""
    db = SessionLocal()

    try:
        default_strategies = [
            {
                'name': 'Trend Following',
                'strategy_type': 'trend_following',
                'description': '추세 추종 전략 - EMA 크로스오버와 MACD를 활용',
                'parameters': {
                    'ema_short': 9,
                    'ema_long': 21,
                    'use_macd': True,
                    'min_trend_strength': 0.6
                },
                'is_active': True
            },
            {
                'name': 'Mean Reversion',
                'strategy_type': 'mean_reversion',
                'description': '평균 회귀 전략 - 볼린저밴드와 RSI 활용',
                'parameters': {
                    'bb_period': 20,
                    'bb_std': 2,
                    'rsi_oversold': 30,
                    'rsi_overbought': 70
                },
                'is_active': True
            },
            {
                'name': 'Momentum Breakout',
                'strategy_type': 'momentum',
                'description': '모멘텀 돌파 전략 - 거래량과 변동성 기반',
                'parameters': {
                    'volume_threshold': 1.5,
                    'atr_multiplier': 2.0,
                    'confirmation_candles': 2
                },
                'is_active': True
            },
            {
                'name': 'Orderbook Imbalance',
                'strategy_type': 'microstructure',
                'description': '호가창 불균형 전략 - 매수/매도 벽 분석',
                'parameters': {
                    'imbalance_threshold': 1.5,
                    'min_wall_size': 10000000,  # 1천만원
                    'reaction_time_seconds': 5
                },
                'is_active': True
            },
            {
                'name': 'Whale Alert Strategy',
                'strategy_type': 'onchain',
                'description': '온체인 대량 거래 추적 전략',
                'parameters': {
                    'min_whale_amount': 100,  # BTC 기준
                    'exchange_flow_weight': 0.7,
                    'reaction_delay_minutes': 15
                },
                'is_active': True
            }
        ]

        for strat_data in default_strategies:
            # 이미 존재하는지 확인
            existing = db.query(Strategy).filter(Strategy.name == strat_data['name']).first()
            if not existing:
                strategy = Strategy(**strat_data)
                db.add(strategy)
                print(f"✓ 전략 생성: {strat_data['name']}")
            else:
                print(f"○ 전략 이미 존재: {strat_data['name']}")

        db.commit()
        print(f"\n기본 전략 {len(default_strategies)}개 초기화 완료!")

    except Exception as e:
        print(f"❌ 전략 초기화 실패: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def main():
    """메인 초기화 프로세스"""
    print("=" * 60)
    print("Auto Coin Trading 데이터베이스 초기화")
    print("=" * 60)

    try:
        # 1. 스키마 및 테이블 생성
        print("\n[1/2] 스키마 및 테이블 생성 중...")
        init_db()
        print("✓ 스키마 및 테이블 생성 완료!")

        # 2. 기본 전략 데이터 삽입
        print("\n[2/2] 기본 전략 데이터 삽입 중...")
        create_default_strategies()

        print("\n" + "=" * 60)
        print("데이터베이스 초기화 성공!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 초기화 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
