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

# Target Trading Pairs (거래대금 상위 100개 - 최대 수익 기회)
# 거래량 1억원 이상 + 변동률 0.5% 이상 코인 전체
TARGET_PAIRS = [
    # Top 20 (거래량 최상위)
    'USDT', 'XRP', 'BTC', 'ETH', 'SOMI', 'SOL', 'DOGE', 'WLD', 'PENGU', 'FF',
    'XPL', 'PUMPBTC', 'ENA', 'AVL', '0G', 'KAITO', 'STAT', 'ADA', 'SUI', 'ONDO',

    # 21-40 (고거래량)
    'MIRA', 'XLM', 'MOODENG', 'PEPE', 'PUMP', 'AVNT', 'ORDER', 'KAIA', 'H', 'SNX',
    'LBL', 'WLFI', 'VIRTUAL', 'BLUE', 'IQ', 'BONK', 'LINK', 'BARD', 'TRUMP', 'SOON',

    # 41-60 (중거래량)
    'BTR', 'F', 'EIGEN', 'SHIB', 'ETC', 'IP', 'FLUID', 'HBAR', 'AVAX', 'ETHFI',
    'TRX', 'BCH', 'BIO', 'IMX', 'W', 'ENS', 'ME', 'BRETT', 'DRIFT', 'RSR',

    # 61-80 (활발한 거래)
    'PEAQ', 'OMNI', 'SEI', 'AL', 'ATH', 'USDC', 'SOPH', 'BABY', 'TOSHI', 'TAVA',
    'NEAR', 'MNT', 'LA', 'STRK', 'UXLINK', 'HEMI', 'DOT', 'NMR', 'AWE', 'MIX',

    # 81-100 (기회 코인)
    'BERA', 'ELX', 'MERL', 'SPK', 'CHZ', 'AMO', 'UNI', 'BSV', 'SAND', 'OPEN',
    'PROVE', 'APT', 'CUDIS', 'AAVE', 'CELO', 'POPCAT', 'XCN', 'ARB', 'STX', 'THE'
]

# 우선순위 그룹 (초고속 스캔 - 변동성 최고)
PRIORITY_PAIRS = [
    'SOMI', 'STAT', 'SNX', 'FLUID', 'EIGEN',  # 고변동성
    'BTC', 'ETH', 'XRP', 'SOL', 'DOGE',       # 메이저
    'PENGU', 'MOODENG', 'TRUMP', 'PEPE'       # 밈코인
]

# Data Collection Intervals (seconds)
ORDERBOOK_INTERVAL = 1  # 호가창 수집 주기
PRICE_INTERVAL = 5  # 가격 데이터 수집 주기
INDICATOR_INTERVAL = 60  # 지표 계산 주기
