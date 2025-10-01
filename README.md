# 🤖 Auto Coin Trading System

빗썸 거래소 기반 자동 암호화폐 매매 시스템

## ⚠️ 면책 조항

**이 시스템은 교육 및 연구 목적으로 제작되었습니다.**
- 암호화폐 투자는 매우 높은 리스크를 수반합니다
- 자동매매 시스템이 수익을 보장하지 않습니다
- 반드시 소액으로 충분히 테스트 후 사용하세요
- 투자 손실에 대한 모든 책임은 사용자에게 있습니다

## 🎯 주요 특징

### 차별화된 전략
1. **호가창 불균형 분석** - 대부분의 개인 투자자가 사용하지 않는 데이터
2. **멀티 전략 시스템** - 추세 추종, 평균 회귀, 모멘텀 돌파
3. **AI 기반 전략 선택** - 시장 상황에 따라 최적 전략 자동 선택
4. **철저한 리스크 관리** - 손절/익절, 포지션 사이징, 일일 손실 한도

### 핵심 모듈
- 📊 **실시간 데이터 수집**: 가격, 호가창, 거래량
- 📈 **기술적 지표 엔진**: RSI, MACD, 볼린저밴드, ADX 등
- 🧠 **AI 전략 선택기**: 과거 성과 학습 및 최적 전략 선택
- 🛡️ **리스크 관리 시스템**: 자동 손절/익절, 포지션 제한
- 🔔 **텔레그램 알림**: 실시간 거래 알림

## 📋 시스템 요구사항

- Python 3.8 이상
- PostgreSQL 데이터베이스
- 빗썸 API Key (거래용)

## 🚀 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example`을 `.env`로 복사하고 수정:

```bash
cp .env.example .env
```

`.env` 파일 편집:

```
# 빗썸 API (https://www.bithumb.com/u1/US127에서 발급)
BITHUMB_API_KEY=your_api_key_here
BITHUMB_SECRET_KEY=your_secret_key_here

# 텔레그램 봇 (선택사항)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 거래 설정
TRADE_MODE=paper  # paper: 페이퍼 트레이딩, live: 실전
INITIAL_CAPITAL=1000000  # 초기 자본 (원)
MAX_POSITION_SIZE=0.1  # 최대 포지션 크기 (10%)
STOP_LOSS_PERCENT=0.02  # 손절 비율 (2%)
TAKE_PROFIT_PERCENT=0.05  # 익절 비율 (5%)
MAX_DAILY_LOSS=0.05  # 일일 최대 손실 (5%)
MAX_OPEN_POSITIONS=3  # 최대 동시 보유 포지션
```

### 3. 데이터베이스 초기화

```bash
python main.py --mode init
```

## 📖 사용 방법

### 모드 1: 데이터 수집만 (권장 첫 단계)

시스템을 학습시키기 위해 먼저 데이터를 수집합니다:

```bash
python main.py --mode collect
```

**최소 24시간 이상 데이터 수집 권장**

### 모드 2: 페이퍼 트레이딩 (모의 투자)

```bash
# .env에서 TRADE_MODE=paper로 설정
python main.py --mode run --interval 60
```

- 실제 주문 없이 시뮬레이션
- 전략 검증 및 시스템 안정성 확인
- **최소 1주일 이상 페이퍼 트레이딩 권장**

### 모드 3: 실전 트레이딩

```bash
# .env에서 TRADE_MODE=live로 설정
python main.py --mode run --interval 60
```

⚠️ **실전 전 체크리스트:**
- [ ] 최소 1주일 페이퍼 트레이딩 완료
- [ ] 전략 승률 60% 이상
- [ ] 빗썸 API Key 발급 및 설정
- [ ] 소액으로 시작 (10만원 이하 권장)
- [ ] 텔레그램 알림 설정 완료

## 📊 모니터링

### 데이터베이스 조회

```sql
-- 오늘의 거래 내역
SELECT * FROM auto_coin_trading.trades
WHERE closed_at >= CURRENT_DATE
ORDER BY closed_at DESC;

-- 현재 오픈 포지션
SELECT * FROM auto_coin_trading.v_active_positions;

-- 전략별 성과
SELECT * FROM auto_coin_trading.v_strategy_summary;

-- 일일 성과
SELECT * FROM auto_coin_trading.daily_performance
ORDER BY date DESC
LIMIT 30;
```

### 텔레그램 알림

1. BotFather에서 텔레그램 봇 생성
2. 봇 토큰을 `.env`에 입력
3. 봇과 대화 시작 후 Chat ID 확인
4. Chat ID를 `.env`에 입력

## 🔧 시스템 구조

```
auto-coin/
├── api/                    # 빗썸 API 클라이언트
├── database/              # 데이터베이스 모델 및 스키마
├── collectors/            # 데이터 수집 (호가창, 가격)
├── analysis/              # 기술적 지표 계산
├── strategies/            # 매매 전략
│   ├── base_strategy.py
│   ├── trend_following.py
│   ├── mean_reversion.py
│   ├── momentum_breakout.py
│   ├── orderbook_imbalance.py  # 차별화 핵심
│   └── strategy_selector.py    # AI 전략 선택
├── core/                  # 핵심 엔진
│   ├── trading_engine.py
│   ├── risk_manager.py
│   └── order_executor.py
├── utils/                 # 유틸리티
│   └── telegram_notifier.py
├── config.py              # 설정
├── main.py               # 메인 실행 파일
└── requirements.txt
```

## 📈 전략 설명

### 1. 추세 추종 (Trend Following)
- EMA 크로스오버 + MACD
- 강한 추세 시장에서 유리
- ADX > 25일 때 활성화

### 2. 평균 회귀 (Mean Reversion)
- 볼린저 밴드 + RSI
- 횡보 시장에서 유리
- 과매수/과매도 구간 매매

### 3. 모멘텀 돌파 (Momentum Breakout)
- 거래량 급증 + 변동성 돌파
- 급격한 가격 변동 시 포착
- Volume > 평균 1.5배 이상

### 4. 호가창 불균형 (Orderbook Imbalance) ⭐
- 매수/매도 벽 분석
- 불균형 비율 1.8배 이상 감지
- **대부분의 개인 투자자가 사용하지 않는 데이터**

## 🛡️ 리스크 관리

1. **포지션 사이징**: 자본의 최대 10% (설정 가능)
2. **손절매**: 진입가 대비 -2% (자동 실행)
3. **익절매**: 진입가 대비 +5% (자동 실행)
4. **트레일링 스톱**: 수익 5% 이상 시 손절가 조정
5. **일일 손실 한도**: 5% 손실 시 당일 거래 중단
6. **최대 포지션 수**: 동시 3개 제한
7. **리스크/보상 비율**: 최소 1:1.2

## 🔍 백테스팅 (추후 구현)

```bash
python backtest.py --start 2024-01-01 --end 2024-12-31 --strategy all
```

## 🐛 트러블슈팅

### 데이터베이스 연결 실패
```bash
# PostgreSQL 상태 확인
psql -h ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app -U unble -d unble
```

### 빗썸 API 에러
- API Key 권한 확인 (출금 권한 불필요)
- IP 화이트리스트 설정
- Rate Limit 확인 (분당 90회)

### 메모리 부족
- 데이터 수집 주기 늘리기
- 오래된 데이터 정리

## 📞 지원

- GitHub Issues: 버그 리포트 및 기능 요청
- 이메일: support@example.com

## 📄 라이센스

MIT License

## 🙏 기여

Pull Request 환영합니다!

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## 📚 참고 자료

- [빗썸 API 문서](https://apidocs.bithumb.com/)
- [TA-Lib 문서](https://mrjbq7.github.io/ta-lib/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)

---

**⚠️ 다시 한번 강조: 암호화폐 투자는 매우 위험합니다. 손실 가능한 금액만 투자하세요.**
