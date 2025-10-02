import os
from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()

# Database Configuration
DATABASE_URL = URL.create(
    'postgresql',
    username=os.getenv('DB_USER', 'unble'),
    password=os.getenv('DB_PASSWORD', 'npg_1kjV0mhECxqs'),
    host=os.getenv('DB_HOST', 'ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app'),
    database=os.getenv('DB_NAME', 'unble'),
)

DB_SCHEMA = os.getenv('DB_SCHEMA', 'auto_coin_trading')

# Bithumb API Configuration
BITHUMB_API_KEY = os.getenv('BITHUMB_API_KEY', '')
BITHUMB_SECRET_KEY = os.getenv('BITHUMB_SECRET_KEY', '')

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Trading Configuration
TRADE_MODE = os.getenv('TRADE_MODE', 'paper')  # 'paper' or 'live'
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 1000000))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 0.1))
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 0.02))
TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', 0.05))

# Risk Management
MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 0.05))
MAX_OPEN_POSITIONS = int(os.getenv('MAX_OPEN_POSITIONS', 3))

# Target Trading Pairs (거래대금 상위 30개 - 활발한 거래 + 안정성)
TARGET_PAIRS = [
    # Tier 1: 메이저 코인 (가장 안정적, 거래량 최고)
    'BTC', 'ETH', 'XRP', 'SOL', 'DOGE', 'ADA',

    # Tier 2: 중형 코인 (거래량 높음, 변동성 적당)
    'WLD', 'PENGU', 'FF', 'ENA', 'ONDO', 'SUI', 'XLM', 'PEPE',
    'LINK', 'BONK', 'SHIB', 'ETC', 'AVAX', 'HBAR',

    # Tier 3: 고변동성 코인 (수익 기회 많음)
    'SOMI', 'STAT', 'MOODENG', 'PUMP', 'SNX', 'VIRTUAL',
    'BLUE', 'EIGEN', 'TRUMP', 'FLUID'
]

# 우선순위 그룹 (빠른 스캔용)
PRIORITY_PAIRS = ['BTC', 'ETH', 'XRP', 'SOL', 'DOGE', 'SOMI', 'STAT', 'SNX']

# Data Collection Intervals (seconds)
ORDERBOOK_INTERVAL = 1  # 호가창 수집 주기
PRICE_INTERVAL = 5  # 가격 데이터 수집 주기
INDICATOR_INTERVAL = 60  # 지표 계산 주기
