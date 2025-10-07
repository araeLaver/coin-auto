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

# Target Trading Pairs - 초고변동성 잡코인 집중 (40개)
TARGET_PAIRS = [
    # 초저가 고변동성 (10-100원대) - 급등 가능성
    'SOPH', 'F', 'H', 'STAT', 'BABY', 'TOSHI', 'TAVA', 'AL', 'ATH', 'CHZ',
    'AMO', 'RSR', 'PEAQ', 'W', 'CUDIS', 'SPK', 'ELX', 'XCN', 'BLUE', 'BRETT',
    # 추가 고변동성 코인 (불장 대응)
    'ZIL', 'WAXP', 'SNT', 'GLM', 'CVC', 'ANKR', 'MBL', 'EGG', 'ARPA', 'OBSR',
    'POLA', 'ADP', 'BLY', 'BIOT', 'GRT', 'IOST', 'COS', 'XPR', 'SOFI', 'WIKEN',
]

# Data Collection Intervals (seconds)
ORDERBOOK_INTERVAL = 1  # 호가창 수집 주기
PRICE_INTERVAL = 5  # 가격 데이터 수집 주기
INDICATOR_INTERVAL = 60  # 지표 계산 주기
