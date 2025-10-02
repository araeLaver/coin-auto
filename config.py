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

# Target Trading Pairs - 단타 전용 (저가 고변동성 코인만)
# 가격: 10원~5000원, 변동성 높음, 최소 주문량 충족 가능
TARGET_PAIRS = [
    # 초저가 고변동성 (10원~100원) - 단타 최적
    'PUMPBTC', 'PENGU', 'H', 'F', 'SOPH', 'ATH', 'SPK', 'CHZ', 'BABY', 'BRETT',
    'AL', 'CUDIS', 'TOSHI', 'TAVA', 'XCN', 'LBL', 'AMO', 'RSR', 'IQ', 'BTR',

    # 저가 변동성 (100원~500원)
    'STAT', 'FF', 'BLUE', 'AVL', 'MOODENG', 'HEMI', 'AWE', 'ELX', 'PEAQ', 'BIO',
    'STRK', 'W', 'KAIA', 'WLFI', 'UXLINK', 'MERL', 'DOGE', 'POPCAT', 'TRX', 'SAND',

    # 중저가 활발 (500원~2000원)
    'SOMI', 'ORDER', 'SOON', 'XLM', 'LA', 'MIRA', 'SNX', 'BARD', 'ADA', 'ONDO',
    'XPL', 'ENA', 'ME', 'DRIFT', 'USDT', 'USDC', 'VIRTUAL', 'AVNT', 'CELO', 'ARB',

    # 중가 변동성 (2000원~5000원)
    'KAITO', 'ETHFI', 'EIGEN', '0G', 'SEI', 'SUI', 'BERA', 'OMNI', 'NEAR', 'MNT'
]

# 우선순위 그룹 (초단타 - 초저가 초고변동성만)
PRIORITY_PAIRS = [
    'PUMPBTC', 'PENGU', 'SOPH', 'F', 'H',      # 초저가 폭발형
    'STAT', 'SOMI', 'MOODENG', 'FF', 'BLUE',   # 저가 변동성
    'KAITO', 'EIGEN', '0G'                      # 중가 변동성
]

# Data Collection Intervals (seconds)
ORDERBOOK_INTERVAL = 1  # 호가창 수집 주기
PRICE_INTERVAL = 5  # 가격 데이터 수집 주기
INDICATOR_INTERVAL = 60  # 지표 계산 주기
