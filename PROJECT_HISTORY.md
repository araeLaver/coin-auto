# 자동매매 시스템 개발 기록

## 📌 프로젝트 개요

**프로젝트명**: 빗썸 자동매매 시스템 (Auto Coin Trading)
**목적**: 100개 암호화폐를 대상으로 기술적 분석 기반 자동 매매
**배포**: Koyeb 클라우드
**대시보드**: https://liable-margette-untab-c8b59ae3.koyeb.app/

## 🗂️ 시스템 구조

```
auto-coin/
├── api/                    # 빗썸 API 클라이언트
│   └── bithumb_client.py
├── core/                   # 핵심 엔진
│   ├── trading_engine_v2.py    # 메인 트레이딩 엔진
│   ├── order_executor.py       # 주문 실행
│   └── risk_manager.py         # 리스크 관리
├── strategies/             # 4가지 매매 전략
│   ├── trend_following.py
│   ├── mean_reversion.py
│   ├── momentum_breakout.py
│   └── orderbook_imbalance.py
├── analysis/              # 기술적 분석
│   └── indicators.py      # RSI, MACD, 볼린저밴드 등
├── database/              # PostgreSQL 모델
│   └── models.py          # 13개 테이블
├── templates/             # 웹 대시보드
│   └── dashboard.html
├── dashboard.py           # Flask 서버
├── app.py                # Koyeb 배포용 통합 앱
├── config.py             # 설정
└── .env                  # 환경변수

데이터베이스: PostgreSQL (Koyeb)
- 스키마: auto_coin_trading
- 테이블: 13개 (OHLCV, 지표, 시그널, 포지션, 거래 등)
```

## 🔧 주요 기능

### 1. 데이터 수집
- **1분봉**: 100개 코인 실시간 수집
- **5분봉, 15분봉**: 기술적 분석용
- **호가창**: 매수/매도 압력 분석

### 2. 기술적 지표 계산
- RSI (14)
- MACD (12, 26, 9)
- 볼린저 밴드 (20, 2)
- EMA (9, 21, 50, 200)
- ATR, ADX, Stochastic

### 3. 4가지 매매 전략
1. **Trend Following**: EMA 크로스오버
2. **Mean Reversion**: 볼린저 밴드 + RSI
3. **Momentum Breakout**: 거래량 + ATR
4. **Orderbook Imbalance**: 호가창 불균형

### 4. AI 전략 선택
- 최근 30일 성과 기반 가중치 조정
- 샤프 비율, 승률, 손익 종합 평가

### 5. 리스크 관리
- 포지션 크기: Kelly Criterion
- 손절: -2%
- 익절: +5%
- 최대 포지션: 10개
- 일일 손실 한도: -5%

### 6. 텔레그램 알림
- 봇: @auto_coin_down_bot
- 매수/매도 알림
- 손익 알림

## 📊 대상 코인 (100개)

### Top 20 (거래량 최상위)
USDT, XRP, BTC, ETH, SOMI, SOL, DOGE, WLD, PENGU, FF, XPL, PUMPBTC, ENA, AVL, 0G, KAITO, STAT, ADA, SUI, ONDO

### 21-40 (고거래량)
MIRA, XLM, MOODENG, PEPE, PUMP, AVNT, ORDER, KAIA, H, SNX, LBL, WLFI, VIRTUAL, BLUE, IQ, BONK, LINK, BARD, TRUMP, SOON

### 41-60 (중거래량)
BTR, F, EIGEN, SHIB, ETC, IP, FLUID, HBAR, AVAX, ETHFI, TRX, BCH, BIO, IMX, W, ENS, ME, BRETT, DRIFT, RSR

### 61-80 (활발한 거래)
PEAQ, OMNI, SEI, AL, ATH, USDC, SOPH, BABY, TOSHI, TAVA, NEAR, MNT, LA, STRK, UXLINK, HEMI, DOT, NMR, AWE, MIX

### 81-100 (기회 코인)
BERA, ELX, MERL, SPK, CHZ, AMO, UNI, BSV, SAND, OPEN, PROVE, APT, CUDIS, AAVE, CELO, POPCAT, XCN, ARB, STX, THE

### 우선순위 코인 (14개)
SOMI, STAT, SNX, FLUID, EIGEN (고변동성)
BTC, ETH, XRP, SOL, DOGE (메이저)
PENGU, MOODENG, TRUMP, PEPE (밈코인)

## ⚙️ 설정 (.env)

```env
# Database
DB_USER=unble
DB_PASSWORD=npg_1kjV0mhECxqs
DB_HOST=ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app
DB_NAME=unble
DB_SCHEMA=auto_coin_trading

# Bithumb API
BITHUMB_API_KEY=8eda6686ef71d4635f0ba20d96d3eb6a
BITHUMB_SECRET_KEY=72510d02ef42456b319e1be1c05a3f84

# Telegram
TELEGRAM_BOT_TOKEN=8289507874:AAHvAT9KNn-D7VkLrmyBzliw69UhEhiEgkM
TELEGRAM_CHAT_ID=552300458

# Trading
TRADE_MODE=live              # live or paper
INITIAL_CAPITAL=234248
MAX_POSITION_SIZE=0.1        # 10%
STOP_LOSS_PERCENT=0.02       # -2%
TAKE_PROFIT_PERCENT=0.05     # +5%

# Risk Management
MAX_DAILY_LOSS=0.05          # -5%
MAX_OPEN_POSITIONS=10
```

## 🐛 해결한 주요 문제들

### 1. 대시보드 없음
**문제**: 백그라운드 서비스라 상태 확인 불가
**해결**: Flask 웹 대시보드 생성 (8개 API 엔드포인트)

### 2. 빗썸 API 잔고 버그
**문제**: `order_currency` 파라미터로 BTC만 표시
**해결**: `currency` 파라미터로 수정 → 모든 코인 잔고 표시

### 3. 시그널 생성 안 됨
**문제**: DB에 OHLCV 데이터 없음
**해결**: `collect_initial_data.py` 생성, app.py에 자동 수집 추가

### 4. 타임존 문제
**문제**: 대시보드에 UTC 시각 표시 (새벽 2시)
**해결**: KST 변환 로직 추가

### 5. 데이터 수집이 DB에 저장 안 됨 ⭐
**문제**:
- `is_running = False`로 스레드 작동 안 함
- 메모리 캐시만 사용, DB 미저장

**해결**:
```python
def start_data_collection(self):
    self.is_running = True  # ✅ 추가

def collect_prices():
    thread_db = SessionLocal()  # ✅ 스레드별 DB 세션
    # ... 1분봉 DB 저장 로직 추가
```

### 6. DB 세션 충돌
**문제**: "This session is in 'prepared' state" 에러
**해결**: 각 스레드가 별도 DB 세션 사용

### 7. 주문 실패 - "Invalid Parameter" ⭐⭐⭐
**문제 1**: 수량 이중 계산
```python
# ❌ 잘못된 코드
quantity = position_size_krw / entry_price  # 5500/4225 = 1.3
units = quantity / order_price              # 1.3/4246 = 0.0003

# ✅ 수정
units = round(position_size_krw / order_price, 8)  # 5500/4246 = 1.29533679
```

**문제 2**: 빗썸은 시장가 주문 미지원
```python
# ❌ 잘못된 코드
order_type = 'market_bid'

# ✅ 수정 (지정가 주문, 즉시 체결)
order_type = 'bid'
order_price = round(price * 1.005, 0)  # 0.5% 높게
units = round(position_size_krw / order_price, 8)
```

**문제 3**: 소수점 자리수
```python
# ❌ 9자리
units = 1.295336789

# ✅ 8자리
units = round(units, 8)  # 1.29533679
```

**문제 4**: 최소 주문 금액
```python
# ❌ 1,000원
min_order_amount = 1000

# ✅ 5,000원 (빗썸 규정)
min_order_amount = 5000
```

### 8. 매매가 안 됨
**문제**: 포지션 7개 열려있는데 MAX_OPEN_POSITIONS=3
**해결**: MAX_OPEN_POSITIONS=10으로 증가

## 📈 개발 타임라인

### 2025-10-02

**03:59**: 마지막 시그널 생성 (이후 9시간 중단)

**11:00 ~ 13:00**: 문제 진단
- 대시보드 접속
- 시그널 0개, 매매 0개 확인
- 디버깅 시작

**13:00 ~ 14:00**: 데이터 수집 문제 해결
- `is_running = True` 추가
- DB 세션 분리
- 1분봉 DB 저장 로직 추가
- 커밋: `db4de9b`

**14:00 ~ 15:00**: 주문 실패 문제 해결
- 모의 거래 모드로 테스트 → 성공
- 실전 모드 주문 → "Invalid Parameter" 에러
- 빗썸 API 형식 분석
- 지정가 주문으로 변경
- 수량 계산 오류 수정
- **14:00 실제 매수 성공**: XRP 1.2953개 @ 4,225원
- 커밋: `41b16d3`, `2071b7b`

**15:00**: 포지션 한도 증가
- MAX_OPEN_POSITIONS: 3 → 10
- 커밋: `cdae493`

## 🎯 현재 상태 (2025-10-02 15:00)

### ✅ 작동 중
- Koyeb 배포: 실행 중
- 데이터 수집: 1분마다 100개 코인
- 트레이딩 엔진: 60초마다 스캔
- 모드: **실전 (live)**

### 📊 현재 포지션 (7개)
1. XRP LONG @ 4,233원 (2.7619개) - PnL: -0.33%
2. BTC LONG @ 168,912,000원 (0.0001개) - PnL: -0.17%
3. ETH LONG @ 6,231,000원 (0.0016개) - PnL: -0.14%
4. BTC LONG @ 168,000,000원 (0.0001개) - PnL: +0.38%
5. BTC LONG @ 168,000,000원 (0.0001개) - PnL: +0.38%
6. XRP LONG @ 4,226원 (1.2950개) - PnL: -0.17%
7. XRP LONG @ 4,225원 (1.2953개) - PnL: -0.14% ← **실제 매수 성공!**

### ⏳ 대기 중
- 15분봉 데이터 50개 수집 중
- 예상 완료: 10-15분 후
- 완료 후: 시그널 생성 → 자동 매매 시작

### 📊 통계
- 총 OHLCV: 13,544개
- 총 시그널: 727개
- 총 포지션: 7개 (OPEN)
- 계좌 잔고: 134,819원 (5,476원 사용)

## 🔄 작동 흐름

```
1. 데이터 수집 (1분마다)
   ├─ 100개 코인 현재가 조회
   ├─ 1분봉 DB 저장
   └─ 호가창 데이터 수집

2. 지표 계산 (60초마다)
   ├─ 15분봉 데이터 조회
   ├─ RSI, MACD, 볼린저밴드 등 계산
   └─ 캐시에 저장

3. 시그널 생성 (60초마다)
   ├─ 4가지 전략 적용
   ├─ AI 가중치로 최적 전략 선택
   └─ 신뢰도 60% 이상만 선택

4. 리스크 검증
   ├─ R/R 비율 1.2 이상
   ├─ 일일 손실 한도 체크
   ├─ 최대 포지션 수 체크
   └─ 포지션 크기 계산 (Kelly)

5. 주문 실행
   ├─ 빗썸 지정가 주문 (즉시 체결)
   ├─ 수량: 소수점 8자리
   ├─ 최소 금액: 5,000원
   └─ DB에 포지션 저장

6. 포지션 관리 (60초마다)
   ├─ 현재가 업데이트
   ├─ 손익 계산
   ├─ 손절(-2%) 또는 익절(+5%) 도달 시
   └─ 자동 청산
```

## 🚀 다음 단계

1. **15분 대기**: 데이터 수집 완료
2. **시그널 생성 시작**: 기술적 지표 기반
3. **자동 매매 시작**: 조건 충족 시 매수/매도
4. **손익 관리**: 목표 도달 시 자동 청산

## 📝 중요 명령어

### 로컬 실행
```bash
cd C:\Develop\unble\auto-coin

# 데이터 수집 테스트
python collect_initial_data.py

# 트레이딩 엔진 1회 실행
python run_engine_test.py

# 실시간 자동매매
python run_live_engine.py

# 상태 확인
python check_status.py

# 실제 주문 테스트
python test_real_buy.py
```

### Git 배포
```bash
git add -A
git commit -m "메시지"
git push  # Koyeb 자동 배포
```

### 데이터베이스 확인
```python
from database import SessionLocal, Position, TradingSignal
db = SessionLocal()

# 오픈 포지션
positions = db.query(Position).filter(Position.status == 'OPEN').all()

# 최근 시그널
signals = db.query(TradingSignal).order_by(TradingSignal.timestamp.desc()).limit(10).all()

db.close()
```

## 🔗 링크

- **대시보드**: https://liable-margette-untab-c8b59ae3.koyeb.app/
- **GitHub**: https://github.com/araeLaver/coin-auto
- **Koyeb**: https://app.koyeb.com/
- **텔레그램 봇**: @auto_coin_down_bot

## 📞 연락처

- Telegram Chat ID: 552300458
- Bot Token: 8289507874:AAHvAT9KNn-D7VkLrmyBzliw69UhEhiEgkM

## ⚠️ 주의사항

1. **API 키 관리**: .env 파일 절대 커밋 금지 (.gitignore에 추가됨)
2. **리스크**: 실전 모드는 실제 자금 사용
3. **모니터링**: 대시보드에서 정기적으로 확인
4. **손실 한도**: 일일 -5% 도달 시 자동 중지
5. **Koyeb 크레딧**: 무료 티어 한도 확인

## 🎓 배운 점

1. **빗썸 API**: 시장가 주문 미지원, 지정가만 가능
2. **DB 세션**: 멀티스레드에서 각 스레드별 세션 필요
3. **데이터 수집**: 메모리 캐시 + DB 병행 저장
4. **주문 검증**: 수량 소수점 8자리, 최소 금액 5,000원
5. **Koyeb 배포**: GitHub push → 자동 배포 (2-3분)

---

**마지막 업데이트**: 2025-10-02 15:00
**작성자**: Claude Code
**버전**: v2.0
