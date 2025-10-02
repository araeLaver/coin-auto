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

# Target Trading Pairs - 공격적 스캘핑 (300개 이상 코인)
TARGET_PAIRS = [
    # Top 50 - 초고거래량
    'USDT', 'XRP', 'BTC', 'ETH', 'SOMI', 'SOL', 'DOGE', 'WLD', 'PENGU', 'FF',
    'XPL', 'PUMPBTC', 'ENA', 'AVL', '0G', 'KAITO', 'STAT', 'ADA', 'SUI', 'ONDO',
    'MIRA', 'XLM', 'MOODENG', 'PEPE', 'PUMP', 'AVNT', 'ORDER', 'KAIA', 'H', 'SNX',
    'LBL', 'WLFI', 'VIRTUAL', 'BLUE', 'IQ', 'BONK', 'LINK', 'BARD', 'TRUMP', 'SOON',
    'BTR', 'F', 'EIGEN', 'SHIB', 'ETC', 'IP', 'FLUID', 'HBAR', 'AVAX', 'ETHFI',

    # 51-100 - 고거래량
    'TRX', 'BCH', 'BIO', 'IMX', 'W', 'ENS', 'ME', 'BRETT', 'DRIFT', 'RSR',
    'PEAQ', 'OMNI', 'SEI', 'AL', 'ATH', 'USDC', 'SOPH', 'BABY', 'TOSHI', 'TAVA',
    'NEAR', 'MNT', 'LA', 'STRK', 'UXLINK', 'HEMI', 'DOT', 'NMR', 'AWE', 'MIX',
    'BERA', 'ELX', 'MERL', 'SPK', 'CHZ', 'AMO', 'UNI', 'BSV', 'SAND', 'OPEN',
    'PROVE', 'APT', 'CUDIS', 'AAVE', 'CELO', 'POPCAT', 'XCN', 'ARB', 'STX', 'THE',

    # 101-150 - 중거래량
    'LTC', 'MATIC', 'ATOM', 'FIL', 'VET', 'ALGO', 'MANA', 'AXS', 'THETA', 'EGLD',
    'FTM', 'KLAY', 'WAVES', 'QTUM', 'ZIL', 'ICX', 'ONT', 'ZRX', 'BAT', 'ENJ',
    'STORJ', 'CVC', 'GRT', 'COMP', 'MKR', 'SNT', 'KNC', 'BAL', 'UMA', 'BAND',
    'ANKR', 'CRV', 'SUSHI', 'YFI', 'REN', 'LRC', 'NU', 'KEEP', 'OXT', 'NMR',
    'SKL', 'MLN', 'GNO', 'OCEAN', 'PUNDIX', 'T', 'PAXG', 'CHR', 'SXP', 'AMP',

    # 151-200 - 활발한 거래
    'AERGO', 'ANT', 'ARDR', 'AST', 'AUDIO', 'AXL', 'BOBA', 'BLUR', 'CTXC', 'CYBER',
    'DYDX', 'FIDA', 'FLM', 'FLOW', 'FX', 'GALA', 'GLM', 'GMT', 'GMX', 'HIFI',
    'HNT', 'ICP', 'JASMY', 'JST', 'JUP', 'KAVA', 'LDO', 'LOOM', 'LSK', 'MAGIC',
    'MANA', 'MASK', 'MATIC', 'MINA', 'MTL', 'NEST', 'OMG', 'ONE', 'OP', 'ORBS',
    'PENDLE', 'PLA', 'POLYX', 'POWR', 'PYTH', 'QKC', 'RAD', 'RDNT', 'REQ', 'RLC',

    # 201-250 - 기회 코인
    'RNDR', 'RSS3', 'SC', 'SFP', 'SLICE', 'SNT', 'SOL', 'SPELL', 'SSV', 'STEEM',
    'STMX', 'STORJ', 'STPT', 'STX', 'SUN', 'SUPER', 'SUSHI', 'SYN', 'T', 'TIA',
    'TLM', 'TON', 'TORN', 'TRB', 'TRU', 'TWT', 'UMA', 'UNI', 'USTC', 'VET',
    'VOXEL', 'WAXP', 'WBTC', 'WOO', 'XEC', 'XEM', 'XLM', 'XRP', 'XTZ', 'XVS',
    'YFI', 'YGG', 'ZEC', 'ZEN', 'ZIL', 'ZRX', 'RUNE', 'INJ', 'DYDX', 'BLUR'
]

# 우선순위 그룹 (변동성 돌파 - 급등 가능성)
PRIORITY_PAIRS = [
    # 초저가 고변동성 (10-100원대)
    'SOPH', 'F', 'H', 'STAT', 'BABY', 'TOSHI', 'TAVA', 'AL', 'ATH', 'CHZ', 'AMO', 'RSR', 'PEAQ', 'W',
    'CUDIS', 'SPK', 'ELX', 'XCN', 'VET', 'ZIL', 'ICX', 'ONT', 'BLUE', 'BRETT',

    # 저가 변동성 (100-500원대)
    'PENGU', 'MOODENG', 'BIO', 'KAIA', 'FF', 'ENJ', 'BAT', 'ZRX', 'POPCAT', 'LA', 'CELO', 'SAND',
    'MANA', 'UXLINK', 'HEMI', 'STRK', 'SEI', 'ALGO', 'TRX',

    # 중가 변동성 (500-3000원대)
    'SOMI', 'ENA', 'IMX', 'ETHFI', 'ME', 'DRIFT', 'OPEN', 'ARB', 'THE', 'STX', 'THETA', 'BARD',
    'WAVES', 'SOON', 'MIRA', 'XLM', 'ADA', 'EIGEN', 'SNX', 'KAITO', '0G'
]

# Data Collection Intervals (seconds)
ORDERBOOK_INTERVAL = 1  # 호가창 수집 주기
PRICE_INTERVAL = 5  # 가격 데이터 수집 주기
INDICATOR_INTERVAL = 60  # 지표 계산 주기
