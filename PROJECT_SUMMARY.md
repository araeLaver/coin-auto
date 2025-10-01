# 🎯 Auto Coin Trading System - 프로젝트 완료 요약

## ✅ 완성된 시스템

### 📁 프로젝트 구조

```
auto-coin/
├── 📄 main.py                          # 메인 실행 파일
├── 📄 config.py                        # 전역 설정
├── 📄 requirements.txt                 # 패키지 의존성
├── 📄 .env                            # 환경 변수
├── 📄 README.md                       # 전체 문서
├── 📄 QUICKSTART.md                   # 빠른 시작 가이드
├── 📄 run.bat / run.sh                # 실행 스크립트
│
├── 📂 database/                       # 데이터베이스 레이어
│   ├── schema.sql                    # PostgreSQL 스키마 (13개 테이블)
│   ├── models.py                     # SQLAlchemy ORM 모델
│   └── init_db.py                    # DB 초기화 스크립트
│
├── 📂 api/                           # 거래소 API
│   ├── bithumb_client.py             # 빗썸 REST API + WebSocket
│   └── __init__.py
│
├── 📂 collectors/                    # 데이터 수집 (차별화 핵심)
│   ├── orderbook_collector.py        # ⭐ 호가창 수집 및 불균형 분석
│   ├── price_collector.py            # OHLCV 가격 데이터
│   └── __init__.py
│
├── 📂 analysis/                      # 분석 엔진
│   ├── indicators.py                 # 기술적 지표 (RSI, MACD, BB 등)
│   └── __init__.py
│
├── 📂 strategies/                    # 매매 전략
│   ├── base_strategy.py              # 전략 베이스 클래스
│   ├── trend_following.py            # 추세 추종 전략
│   ├── mean_reversion.py             # 평균 회귀 전략
│   ├── momentum_breakout.py          # 모멘텀 돌파 전략
│   ├── orderbook_imbalance.py        # ⭐ 호가창 불균형 전략
│   ├── strategy_selector.py          # 🧠 AI 기반 전략 선택기
│   └── __init__.py
│
├── 📂 core/                          # 핵심 트레이딩 엔진
│   ├── trading_engine.py             # 메인 트레이딩 엔진
│   ├── risk_manager.py               # 리스크 관리 시스템
│   ├── order_executor.py             # 주문 실행 모듈
│   └── __init__.py
│
└── 📂 utils/                         # 유틸리티
    ├── telegram_notifier.py          # 텔레그램 알림
    └── __init__.py
```

## 🎨 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                     Trading Engine                       │
│                   (메인 오케스트레이터)                    │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│  Data Collect  │  │  Analysis   │  │   Strategies    │
├────────────────┤  ├─────────────┤  ├─────────────────┤
│ • 호가창 수집   │  │ • RSI       │  │ • 추세 추종      │
│ • 가격 수집     │  │ • MACD      │  │ • 평균 회귀      │
│ • 불균형 분석   │  │ • BB        │  │ • 모멘텀 돌파    │
│ • 이상 감지     │  │ • ADX       │  │ • 호가창 전략    │
└────────────────┘  └─────────────┘  └─────────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                ┌───────────▼───────────┐
                │   Strategy Selector   │
                │   (AI 기반 최적화)     │
                └───────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│ Risk Manager   │  │   Order     │  │   Telegram      │
│                │  │  Executor   │  │   Notifier      │
├────────────────┤  ├─────────────┤  ├─────────────────┤
│ • 손절/익절     │  │ • 주문 실행  │  │ • 거래 알림      │
│ • 포지션 제한   │  │ • 포지션 관리│  │ • 시그널 알림    │
│ • 일일 한도     │  │ • 잔고 관리  │  │ • 리스크 경고    │
└────────────────┘  └─────────────┘  └─────────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                ┌───────────▼───────────┐
                │   PostgreSQL DB       │
                │  (auto_coin_trading)  │
                └───────────────────────┘
```

## 🌟 핵심 차별화 요소

### 1. 호가창 불균형 분석 (OrderbookImbalanceStrategy)
**대부분의 개인 투자자가 사용하지 않는 데이터**

- 실시간 매수/매도 벽 감지
- 불균형 비율 계산 (1.8배 이상 시 시그널)
- 대형 주문 ("고래") 추적
- 스프레드 급등 감지

**수집 데이터:**
- 호가창 스냅샷 (1초 주기)
- 매수/매도 총 물량
- 가격별 물량 분포
- 이상 패턴 (whale_wall, spread_spike, volume_surge)

### 2. AI 기반 전략 선택 (StrategySelector)
**시장 상황에 따라 최적 전략 자동 선택**

```python
# 전략 가중치 자동 계산
- 과거 30일 성과 분석
- 승률 40% + 샤프비율 30% + 평균수익 30%
- 시장 적합도 계산

# 시장 상황별 전략 매칭
- 강한 추세 → Trend Following
- 횡보장 → Mean Reversion
- 거래량 급증 → Momentum Breakout
- 호가 불균형 → Orderbook Imbalance
```

### 3. 멀티 레이어 리스크 관리

```python
# 레벨 1: 포지션별
- 자동 손절: -2%
- 자동 익절: +5%
- 트레일링 스톱: 수익 5% 이상 시

# 레벨 2: 계좌 전체
- 최대 포지션 크기: 10%
- 동시 포지션 수: 3개
- Kelly Criterion 기반 사이징

# 레벨 3: 일일 한도
- 일일 최대 손실: -5%
- 한도 초과 시 당일 거래 중단
```

## 📊 데이터베이스 스키마

### 핵심 테이블 (13개)

1. **ohlcv_data** - OHLCV 캔들 데이터
2. **orderbook_snapshots** - 호가창 스냅샷 ⭐
3. **orderbook_anomalies** - 호가창 이상 패턴 ⭐
4. **technical_indicators** - 기술적 지표
5. **strategies** - 전략 정의
6. **strategy_performance** - 전략 성과
7. **trading_signals** - 트레이딩 시그널
8. **positions** - 오픈 포지션
9. **orders** - 주문 내역
10. **trades** - 청산된 거래
11. **daily_performance** - 일일 성과
12. **account_balance** - 계좌 잔고
13. **system_logs** - 시스템 로그

### 유용한 뷰 (3개)

- **v_active_positions** - 현재 활성 포지션
- **v_strategy_summary** - 전략별 성과 요약
- **v_recent_signals** - 최근 시그널

## 🚀 실행 방법

### 방법 1: 배치 파일 (Windows)
```bash
run.bat
```

### 방법 2: 쉘 스크립트 (Linux/Mac)
```bash
./run.sh
```

### 방법 3: 직접 실행
```bash
# 1. DB 초기화
python main.py --mode init

# 2. 데이터 수집
python main.py --mode collect

# 3. 페이퍼 트레이딩
python main.py --mode run --interval 60
```

## ⚙️ 설정 파라미터 (.env)

```bash
# 거래 모드
TRADE_MODE=paper          # paper: 모의, live: 실전

# 초기 설정
INITIAL_CAPITAL=1000000   # 100만원
MAX_POSITION_SIZE=0.1     # 10%
MAX_OPEN_POSITIONS=3      # 3개

# 리스크 관리
STOP_LOSS_PERCENT=0.02    # 2%
TAKE_PROFIT_PERCENT=0.05  # 5%
MAX_DAILY_LOSS=0.05       # 5%

# 대상 코인 (config.py)
TARGET_PAIRS = ['BTC', 'ETH', 'XRP', 'ADA', 'SOL']
```

## 📈 전략 요약

| 전략 | 시장 상황 | 주요 지표 | 특징 |
|------|----------|----------|------|
| **Trend Following** | 강한 추세 | EMA, MACD, ADX | 추세 방향 매매 |
| **Mean Reversion** | 횡보장 | BB, RSI, Stoch | 과매수/과매도 |
| **Momentum Breakout** | 변동성 증가 | Volume, ATR | 돌파 매매 |
| **Orderbook Imbalance** ⭐ | 모든 시장 | 호가창 불균형 | 차별화 핵심 |

## 🎓 학습 곡선

### Week 1: 데이터 수집
- 24시간 이상 데이터 수집
- 시스템 안정성 확인

### Week 2-3: 페이퍼 트레이딩
- 모의 투자로 전략 검증
- AI가 전략 가중치 학습
- 예상 승률: 45-55% → 55-65%

### Week 4+: 소액 실전
- 10만원 이하로 시작
- 점진적 확대
- 지속적 모니터링

## 📊 성과 지표

시스템이 자동 추적하는 지표:
- 승률 (Win Rate)
- 총 손익 (Total PnL)
- 샤프 비율 (Sharpe Ratio)
- 최대 낙폭 (Max Drawdown)
- 평균 보유 시간
- 전략별 성과

## 🔧 유지보수

### 일일 체크
```sql
SELECT * FROM auto_coin_trading.daily_performance
WHERE date = CURRENT_DATE;
```

### 주간 체크
```sql
SELECT * FROM auto_coin_trading.v_strategy_summary;
```

### 로그 확인
```bash
tail -f logs/trading.log
```

## ⚠️ 중요 안전 수칙

1. ✅ **반드시 페이퍼 트레이딩부터 시작**
2. ✅ **소액으로 실전 시작 (10만원 이하)**
3. ✅ **일일 손실 한도 준수**
4. ✅ **정기적인 성과 분석**
5. ✅ **텔레그램 알림 설정**
6. ❌ **전 재산 투자 금지**
7. ❌ **레버리지 사용 금지**

## 📞 지원

- README.md: 전체 문서
- QUICKSTART.md: 빠른 시작
- config.py: 모든 설정
- GitHub Issues: 버그 리포트

## 🎉 완료!

**시스템이 완전히 구현되었습니다!**

이제 할 일:
1. `python main.py --mode init` - DB 초기화
2. `python main.py --mode collect` - 24시간 데이터 수집
3. `python main.py --mode run` - 페이퍼 트레이딩 시작

---

**행운을 빕니다! 하지만 리스크 관리를 잊지 마세요! 🍀**
