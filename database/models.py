from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, Boolean, Text, ForeignKey, Date, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import config

Base = declarative_base()

# Database Engine
engine = create_engine(
    config.DATABASE_URL,
    connect_args={
        'options': f'-c search_path={config.DB_SCHEMA}'
    },
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===========================
# 1. 시세 데이터 모델
# ===========================

class OHLCVData(Base):
    __tablename__ = 'ohlcv_data'
    __table_args__ = (
        UniqueConstraint('symbol', 'timeframe', 'timestamp', name='uix_ohlcv'),
        {'schema': config.DB_SCHEMA}
    )

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Numeric(20, 8), nullable=False)
    high = Column(Numeric(20, 8), nullable=False)
    low = Column(Numeric(20, 8), nullable=False)
    close = Column(Numeric(20, 8), nullable=False)
    volume = Column(Numeric(20, 8), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderbookSnapshot(Base):
    __tablename__ = 'orderbook_snapshots'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    bids = Column(JSONB, nullable=False)
    asks = Column(JSONB, nullable=False)
    bid_total_volume = Column(Numeric(20, 8))
    ask_total_volume = Column(Numeric(20, 8))
    imbalance_ratio = Column(Numeric(10, 4))
    spread = Column(Numeric(20, 8))
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderbookAnomaly(Base):
    __tablename__ = 'orderbook_anomalies'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    anomaly_type = Column(String(50), nullable=False)
    severity = Column(Numeric(5, 2))
    details = Column(JSONB)
    price_before = Column(Numeric(20, 8))
    price_after = Column(Numeric(20, 8))
    created_at = Column(DateTime, default=datetime.utcnow)


# ===========================
# 2. 기술적 지표 모델
# ===========================

class TechnicalIndicator(Base):
    __tablename__ = 'technical_indicators'
    __table_args__ = (
        UniqueConstraint('symbol', 'timeframe', 'timestamp', name='uix_indicators'),
        {'schema': config.DB_SCHEMA}
    )

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    rsi_14 = Column(Numeric(10, 4))
    macd = Column(Numeric(20, 8))
    macd_signal = Column(Numeric(20, 8))
    macd_histogram = Column(Numeric(20, 8))
    bb_upper = Column(Numeric(20, 8))
    bb_middle = Column(Numeric(20, 8))
    bb_lower = Column(Numeric(20, 8))
    ema_9 = Column(Numeric(20, 8))
    ema_21 = Column(Numeric(20, 8))
    ema_50 = Column(Numeric(20, 8))
    ema_200 = Column(Numeric(20, 8))
    volume_sma_20 = Column(Numeric(20, 8))
    atr_14 = Column(Numeric(20, 8))
    adx_14 = Column(Numeric(10, 4))
    stoch_k = Column(Numeric(10, 4))
    stoch_d = Column(Numeric(10, 4))
    created_at = Column(DateTime, default=datetime.utcnow)


# ===========================
# 3. 온체인 데이터 모델
# ===========================

class WhaleTransaction(Base):
    __tablename__ = 'whale_transactions'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    amount = Column(Numeric(30, 8), nullable=False)
    amount_usd = Column(Numeric(20, 2))
    from_address = Column(String(100))
    to_address = Column(String(100))
    tx_hash = Column(String(100), unique=True)
    transaction_type = Column(String(50))
    exchange_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


# ===========================
# 4. 전략 및 시그널 모델
# ===========================

class Strategy(Base):
    __tablename__ = 'strategies'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    strategy_type = Column(String(50), nullable=False)
    description = Column(Text)
    parameters = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    signals = relationship("TradingSignal", back_populates="strategy")
    positions = relationship("Position", back_populates="strategy")
    trades = relationship("Trade", back_populates="strategy")
    performance = relationship("StrategyPerformance", back_populates="strategy")


class StrategyPerformance(Base):
    __tablename__ = 'strategy_performance'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey(f'{config.DB_SCHEMA}.strategies.id'))
    symbol = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    win_rate = Column(Numeric(10, 4))
    total_trades = Column(Integer, default=0)
    profitable_trades = Column(Integer, default=0)
    total_pnl = Column(Numeric(20, 8), default=0)
    sharpe_ratio = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 4))
    current_weight = Column(Numeric(5, 4))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    strategy = relationship("Strategy", back_populates="performance")


class TradingSignal(Base):
    __tablename__ = 'trading_signals'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey(f'{config.DB_SCHEMA}.strategies.id'))
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    signal_type = Column(String(20), nullable=False)
    strength = Column(Numeric(5, 2))
    entry_price = Column(Numeric(20, 8))
    stop_loss = Column(Numeric(20, 8))
    take_profit = Column(Numeric(20, 8))
    position_size = Column(Numeric(20, 8))
    confidence = Column(Numeric(5, 4))
    reasoning = Column(Text)
    signal_metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    strategy = relationship("Strategy", back_populates="signals")
    position = relationship("Position", back_populates="signal", uselist=False)


# ===========================
# 5. 거래 실행 모델
# ===========================

class Position(Base):
    __tablename__ = 'positions'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    strategy_id = Column(Integer, ForeignKey(f'{config.DB_SCHEMA}.strategies.id'))
    signal_id = Column(Integer, ForeignKey(f'{config.DB_SCHEMA}.trading_signals.id'))
    position_type = Column(String(10), nullable=False)
    entry_price = Column(Numeric(20, 8), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    current_price = Column(Numeric(20, 8))
    unrealized_pnl = Column(Numeric(20, 8))
    stop_loss = Column(Numeric(20, 8))
    take_profit = Column(Numeric(20, 8))
    status = Column(String(20), default='OPEN', index=True)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    strategy = relationship("Strategy", back_populates="positions")
    signal = relationship("TradingSignal", back_populates="position")
    orders = relationship("Order", back_populates="position")
    trade = relationship("Trade", back_populates="position", uselist=False)


class Order(Base):
    __tablename__ = 'orders'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(Integer, ForeignKey(f'{config.DB_SCHEMA}.positions.id'))
    order_id = Column(String(100), unique=True)
    symbol = Column(String(20), nullable=False)
    order_type = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    price = Column(Numeric(20, 8))
    quantity = Column(Numeric(20, 8), nullable=False)
    filled_quantity = Column(Numeric(20, 8), default=0)
    status = Column(String(20), nullable=False, index=True)
    fee = Column(Numeric(20, 8), default=0)
    executed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    position = relationship("Position", back_populates="orders")


class Trade(Base):
    __tablename__ = 'trades'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(Integer, ForeignKey(f'{config.DB_SCHEMA}.positions.id'))
    strategy_id = Column(Integer, ForeignKey(f'{config.DB_SCHEMA}.strategies.id'))
    symbol = Column(String(20), nullable=False, index=True)
    entry_price = Column(Numeric(20, 8), nullable=False)
    exit_price = Column(Numeric(20, 8), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    pnl = Column(Numeric(20, 8), nullable=False)
    pnl_percent = Column(Numeric(10, 4), nullable=False)
    fees = Column(Numeric(20, 8), default=0)
    holding_time_minutes = Column(Integer)
    exit_reason = Column(String(50))
    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    strategy = relationship("Strategy", back_populates="trades")
    position = relationship("Position", back_populates="trade")


# ===========================
# 6. 리스크 관리 모델
# ===========================

class DailyPerformance(Base):
    __tablename__ = 'daily_performance'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    starting_balance = Column(Numeric(20, 8), nullable=False)
    ending_balance = Column(Numeric(20, 8), nullable=False)
    total_pnl = Column(Numeric(20, 8), nullable=False)
    pnl_percent = Column(Numeric(10, 4), nullable=False)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    max_drawdown = Column(Numeric(10, 4))
    is_trading_paused = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountBalance(Base):
    __tablename__ = 'account_balance'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    total_krw = Column(Numeric(20, 2), nullable=False)
    total_crypto_value = Column(Numeric(20, 2), nullable=False)
    total_value = Column(Numeric(20, 2), nullable=False)
    available_krw = Column(Numeric(20, 2), nullable=False)
    positions_value = Column(Numeric(20, 2), nullable=False)
    unrealized_pnl = Column(Numeric(20, 2), default=0)
    details = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===========================
# 7. 시스템 로그 모델
# ===========================

class SystemLog(Base):
    __tablename__ = 'system_logs'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    log_level = Column(String(20), nullable=False, index=True)
    module = Column(String(100))
    message = Column(Text, nullable=False)
    details = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    notification_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), default='NORMAL', index=True)
    is_sent = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===========================
# 8. 백테스팅 모델
# ===========================

class BacktestRun(Base):
    __tablename__ = 'backtest_runs'
    __table_args__ = {'schema': config.DB_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey(f'{config.DB_SCHEMA}.strategies.id'))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Numeric(20, 8), nullable=False)
    final_capital = Column(Numeric(20, 8), nullable=False)
    total_pnl = Column(Numeric(20, 8), nullable=False)
    total_trades = Column(Integer)
    win_rate = Column(Numeric(10, 4))
    sharpe_ratio = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 4))
    parameters = Column(JSONB)
    results = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===========================
# 데이터베이스 초기화 함수
# ===========================

def init_db():
    """데이터베이스 스키마 및 테이블 생성"""
    from sqlalchemy import text

    # 스키마 생성
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {config.DB_SCHEMA}"))
        conn.commit()

    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    print(f"Database schema '{config.DB_SCHEMA}' and tables created successfully!")


def get_db():
    """데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
