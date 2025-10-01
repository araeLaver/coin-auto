-- Auto Coin Trading Schema
-- 전용 스키마 생성
CREATE SCHEMA IF NOT EXISTS auto_coin_trading;

-- 스키마 설정
SET search_path TO auto_coin_trading;

-- ===========================
-- 1. 시세 데이터 테이블
-- ===========================

-- OHLCV 캔들 데이터
CREATE TABLE IF NOT EXISTS ohlcv_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,  -- 1m, 5m, 15m, 1h, 4h, 1d
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timeframe, timestamp)
);

CREATE INDEX idx_ohlcv_symbol_timeframe ON ohlcv_data(symbol, timeframe, timestamp DESC);

-- 호가창 스냅샷 (핵심 차별화 데이터)
CREATE TABLE IF NOT EXISTS orderbook_snapshots (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    bids JSONB NOT NULL,  -- [{price, quantity}, ...]
    asks JSONB NOT NULL,
    bid_total_volume DECIMAL(20, 8),
    ask_total_volume DECIMAL(20, 8),
    imbalance_ratio DECIMAL(10, 4),  -- 매수/매도 불균형 비율
    spread DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orderbook_symbol_time ON orderbook_snapshots(symbol, timestamp DESC);

-- 호가창 이상 패턴 감지
CREATE TABLE IF NOT EXISTS orderbook_anomalies (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL,  -- 'whale_wall', 'spread_spike', 'volume_surge'
    severity DECIMAL(5, 2),  -- 0-100
    details JSONB,
    price_before DECIMAL(20, 8),
    price_after DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_anomaly_symbol_type ON orderbook_anomalies(symbol, anomaly_type, timestamp DESC);

-- ===========================
-- 2. 기술적 지표 테이블
-- ===========================

CREATE TABLE IF NOT EXISTS technical_indicators (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    rsi_14 DECIMAL(10, 4),
    macd DECIMAL(20, 8),
    macd_signal DECIMAL(20, 8),
    macd_histogram DECIMAL(20, 8),
    bb_upper DECIMAL(20, 8),
    bb_middle DECIMAL(20, 8),
    bb_lower DECIMAL(20, 8),
    ema_9 DECIMAL(20, 8),
    ema_21 DECIMAL(20, 8),
    ema_50 DECIMAL(20, 8),
    ema_200 DECIMAL(20, 8),
    volume_sma_20 DECIMAL(20, 8),
    atr_14 DECIMAL(20, 8),
    adx_14 DECIMAL(10, 4),
    stoch_k DECIMAL(10, 4),
    stoch_d DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timeframe, timestamp)
);

CREATE INDEX idx_indicators_symbol_time ON technical_indicators(symbol, timeframe, timestamp DESC);

-- ===========================
-- 3. 온체인 데이터 테이블
-- ===========================

-- 대량 거래 추적 (Whale Transactions)
CREATE TABLE IF NOT EXISTS whale_transactions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    amount DECIMAL(30, 8) NOT NULL,
    amount_usd DECIMAL(20, 2),
    from_address VARCHAR(100),
    to_address VARCHAR(100),
    tx_hash VARCHAR(100) UNIQUE,
    transaction_type VARCHAR(50),  -- 'exchange_inflow', 'exchange_outflow', 'whale_transfer'
    exchange_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_whale_symbol_time ON whale_transactions(symbol, timestamp DESC);

-- ===========================
-- 4. 전략 및 시그널 테이블
-- ===========================

-- 전략 정의
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,  -- 'trend_following', 'mean_reversion', 'momentum'
    description TEXT,
    parameters JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 전략 성과 추적
CREATE TABLE IF NOT EXISTS strategy_performance (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    win_rate DECIMAL(10, 4),
    total_trades INTEGER DEFAULT 0,
    profitable_trades INTEGER DEFAULT 0,
    total_pnl DECIMAL(20, 8) DEFAULT 0,
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    current_weight DECIMAL(5, 4),  -- AI 가중치 (0-1)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_strategy_perf ON strategy_performance(strategy_id, timestamp DESC);

-- 트레이딩 시그널
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    signal_type VARCHAR(20) NOT NULL,  -- 'BUY', 'SELL', 'HOLD'
    strength DECIMAL(5, 2),  -- 0-100
    entry_price DECIMAL(20, 8),
    stop_loss DECIMAL(20, 8),
    take_profit DECIMAL(20, 8),
    position_size DECIMAL(20, 8),
    confidence DECIMAL(5, 4),  -- 0-1
    reasoning TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signals_symbol_time ON trading_signals(symbol, timestamp DESC);

-- ===========================
-- 5. 거래 실행 테이블
-- ===========================

-- 포지션 (현재 보유)
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    strategy_id INTEGER REFERENCES strategies(id),
    signal_id INTEGER REFERENCES trading_signals(id),
    position_type VARCHAR(10) NOT NULL,  -- 'LONG', 'SHORT'
    entry_price DECIMAL(20, 8) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    current_price DECIMAL(20, 8),
    unrealized_pnl DECIMAL(20, 8),
    stop_loss DECIMAL(20, 8),
    take_profit DECIMAL(20, 8),
    status VARCHAR(20) DEFAULT 'OPEN',  -- 'OPEN', 'CLOSED'
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_status ON positions(status, symbol);

-- 주문 내역
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    order_id VARCHAR(100) UNIQUE,  -- Bithumb order ID
    symbol VARCHAR(20) NOT NULL,
    order_type VARCHAR(20) NOT NULL,  -- 'MARKET', 'LIMIT'
    side VARCHAR(10) NOT NULL,  -- 'BUY', 'SELL'
    price DECIMAL(20, 8),
    quantity DECIMAL(20, 8) NOT NULL,
    filled_quantity DECIMAL(20, 8) DEFAULT 0,
    status VARCHAR(20) NOT NULL,  -- 'PENDING', 'FILLED', 'PARTIAL', 'CANCELLED'
    fee DECIMAL(20, 8) DEFAULT 0,
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_status ON orders(status, created_at DESC);

-- 거래 내역 (청산된 포지션)
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    strategy_id INTEGER REFERENCES strategies(id),
    symbol VARCHAR(20) NOT NULL,
    entry_price DECIMAL(20, 8) NOT NULL,
    exit_price DECIMAL(20, 8) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    pnl DECIMAL(20, 8) NOT NULL,
    pnl_percent DECIMAL(10, 4) NOT NULL,
    fees DECIMAL(20, 8) DEFAULT 0,
    holding_time_minutes INTEGER,
    exit_reason VARCHAR(50),  -- 'TAKE_PROFIT', 'STOP_LOSS', 'SIGNAL', 'MANUAL'
    opened_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trades_symbol_time ON trades(symbol, closed_at DESC);

-- ===========================
-- 6. 리스크 관리 테이블
-- ===========================

-- 일일 손익 추적
CREATE TABLE IF NOT EXISTS daily_performance (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    starting_balance DECIMAL(20, 8) NOT NULL,
    ending_balance DECIMAL(20, 8) NOT NULL,
    total_pnl DECIMAL(20, 8) NOT NULL,
    pnl_percent DECIMAL(10, 4) NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    max_drawdown DECIMAL(10, 4),
    is_trading_paused BOOLEAN DEFAULT false,  -- 손실 한도 초과시
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 계좌 잔고 스냅샷
CREATE TABLE IF NOT EXISTS account_balance (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    total_krw DECIMAL(20, 2) NOT NULL,
    total_crypto_value DECIMAL(20, 2) NOT NULL,
    total_value DECIMAL(20, 2) NOT NULL,
    available_krw DECIMAL(20, 2) NOT NULL,
    positions_value DECIMAL(20, 2) NOT NULL,
    unrealized_pnl DECIMAL(20, 2) DEFAULT 0,
    details JSONB,  -- 각 코인별 잔고
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_balance_time ON account_balance(timestamp DESC);

-- ===========================
-- 7. 시스템 로그 테이블
-- ===========================

CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    log_level VARCHAR(20) NOT NULL,  -- 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    module VARCHAR(100),
    message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_level_time ON system_logs(log_level, timestamp DESC);

-- 알림 내역
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notification_type VARCHAR(50) NOT NULL,  -- 'TRADE', 'SIGNAL', 'ERROR', 'RISK_ALERT'
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'NORMAL',  -- 'LOW', 'NORMAL', 'HIGH', 'CRITICAL'
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_sent ON notifications(is_sent, priority, created_at DESC);

-- ===========================
-- 8. 백테스팅 테이블
-- ===========================

CREATE TABLE IF NOT EXISTS backtest_runs (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    initial_capital DECIMAL(20, 8) NOT NULL,
    final_capital DECIMAL(20, 8) NOT NULL,
    total_pnl DECIMAL(20, 8) NOT NULL,
    total_trades INTEGER,
    win_rate DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    parameters JSONB,
    results JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_backtest_strategy ON backtest_runs(strategy_id, created_at DESC);

-- ===========================
-- 뷰 생성
-- ===========================

-- 현재 활성 포지션 요약
CREATE OR REPLACE VIEW v_active_positions AS
SELECT
    p.id,
    p.symbol,
    s.name as strategy_name,
    p.position_type,
    p.entry_price,
    p.quantity,
    p.current_price,
    p.unrealized_pnl,
    (p.unrealized_pnl / (p.entry_price * p.quantity) * 100) as pnl_percent,
    p.stop_loss,
    p.take_profit,
    p.opened_at,
    EXTRACT(EPOCH FROM (NOW() - p.opened_at))/60 as holding_minutes
FROM positions p
LEFT JOIN strategies s ON p.strategy_id = s.id
WHERE p.status = 'OPEN'
ORDER BY p.opened_at DESC;

-- 전략별 성과 요약
CREATE OR REPLACE VIEW v_strategy_summary AS
SELECT
    s.id,
    s.name,
    s.strategy_type,
    COUNT(t.id) as total_trades,
    SUM(CASE WHEN t.pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    ROUND(AVG(CASE WHEN t.pnl > 0 THEN 1.0 ELSE 0.0 END) * 100, 2) as win_rate,
    SUM(t.pnl) as total_pnl,
    AVG(t.pnl) as avg_pnl,
    MAX(t.pnl) as max_win,
    MIN(t.pnl) as max_loss
FROM strategies s
LEFT JOIN trades t ON s.id = t.strategy_id
WHERE s.is_active = true
GROUP BY s.id, s.name, s.strategy_type
ORDER BY total_pnl DESC;

-- 최근 시그널 요약
CREATE OR REPLACE VIEW v_recent_signals AS
SELECT
    ts.id,
    ts.symbol,
    s.name as strategy_name,
    ts.signal_type,
    ts.strength,
    ts.entry_price,
    ts.confidence,
    ts.timestamp,
    CASE
        WHEN p.id IS NOT NULL THEN 'EXECUTED'
        ELSE 'PENDING'
    END as execution_status
FROM trading_signals ts
LEFT JOIN strategies s ON ts.strategy_id = s.id
LEFT JOIN positions p ON ts.id = p.signal_id
WHERE ts.timestamp > NOW() - INTERVAL '24 hours'
ORDER BY ts.timestamp DESC;
