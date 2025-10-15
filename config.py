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
MAX_OPEN_POSITIONS = int(os.getenv('MAX_OPEN_POSITIONS', 5))  # 보수적: 5개로 제한

# Target Trading Pairs - 빗썸 전체 코인 탐색 (최대 범위)
TARGET_PAIRS = [
    # 초저가 고변동성 (10-100원대) - 급등 가능성
    'SOPH', 'F', 'H', 'STAT', 'BABY', 'TOSHI', 'TAVA', 'AL', 'ATH', 'CHZ',
    'AMO', 'RSR', 'PEAQ', 'W', 'CUDIS', 'SPK', 'ELX', 'XCN', 'BLUE', 'BRETT',
    # 추가 고변동성 코인
    'ZIL', 'WAXP', 'SNT', 'GLM', 'CVC', 'ANKR', 'MBL', 'EGG', 'ARPA', 'OBSR',
    'POLA', 'ADP', 'BLY', 'BIOT', 'GRT', 'IOST', 'COS', 'XPR', 'SOFI', 'WIKEN',
    # 중저가 코인 추가 (100-1000원대)
    'STRAX', 'JST', 'SXP', 'BAT', 'ENJ', 'MTL', 'STORJ', 'SAND', 'MANA', 'AXS',
    'BORA', 'MEV', 'SSX', 'META', 'FCT2', 'MIX', 'TEMCO', 'VET', 'CHR', 'STPT',
    # 메이저 알트 (변동성)
    'XRP', 'ADA', 'DOGE', 'DOT', 'MATIC', 'LINK', 'UNI', 'ATOM', 'ETC', 'BCH',
    'LTC', 'EOS', 'TRX', 'XLM', 'ALGO', 'AVAX', 'NEAR', 'FTM', 'HBAR', 'VET',
    # 추가 잠재력 코인
    'RNDR', 'IMX', 'APT', 'OP', 'ARB', 'SUI', 'SEI', 'TIA', 'STRK', 'PYTH',
    'WLD', 'JUP', 'DYM', 'ALT', 'MANTA', 'AEVO', 'PORTAL', 'PIXEL', 'RONIN', 'OMNI',
    # 신규 상장 & 추가
    'DOGS', 'TON', 'NOT', 'HMSTR', 'CATI', 'EIGEN', 'NEIRO', 'GOAT', 'PNUT', 'ACT',
    'BANANA', 'DRIFT', 'GRASS', 'MOVE', 'USUAL', 'PENGU', 'HYPE', 'VIRTUAL', 'AIXBT', 'ZEREBRO',
]

# Data Collection Intervals (seconds)
ORDERBOOK_INTERVAL = 1  # 호가창 수집 주기
PRICE_INTERVAL = 5  # 가격 데이터 수집 주기
INDICATOR_INTERVAL = 60  # 지표 계산 주기
