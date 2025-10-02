# 문제 해결 가이드

## 🔍 자주 발생하는 문제

### 1. 시그널이 생성되지 않음

**증상**: 대시보드에 시그널 0개

**원인 확인**:
```python
python check_status.py
```

**가능한 원인**:
1. OHLCV 데이터 부족 (최소 50개 필요)
2. 데이터 수집 스레드 중단
3. Koyeb 엔진 중지

**해결**:
```python
# 데이터 수집
python collect_initial_data.py

# 엔진 재시작
# Koyeb 대시보드에서 재배포
```

### 2. 매매가 실행되지 않음

**증상**: 시그널은 있는데 포지션 0개

**원인 확인**:
```python
python check_why_no_trade.py
```

**가능한 원인**:
1. **포지션 한도 도달** (현재/최대 확인)
2. 리스크 검증 실패 (R/R < 1.2, 신뢰도 < 60%)
3. 일일 손실 한도 초과
4. 계좌 잔고 부족 (최소 5,000원)

**해결**:
```bash
# .env 파일 수정
MAX_OPEN_POSITIONS=10  # 증가

# 또는 기존 포지션 수동 청산
```

### 3. 주문 실패 - "Invalid Parameter"

**원인**: 빗썸 API 파라미터 오류

**확인 사항**:
- ✅ 수량: 소수점 8자리 이하
- ✅ 주문 금액: 5,000원 이상
- ✅ 주문 타입: 'bid' 또는 'ask' (시장가 X)

**테스트**:
```python
python test_real_order.py
```

### 4. DB 세션 에러

**증상**: "This session is in 'prepared' state"

**원인**: 여러 스레드가 같은 DB 세션 사용

**해결**: 이미 수정됨 (각 스레드별 세션)
```python
def collect_prices():
    thread_db = SessionLocal()  # 스레드 전용
    # ...
    thread_db.close()
```

### 5. Koyeb 배포 실패

**증상**: 배포 후 엔진 작동 안 함

**확인**:
1. Koyeb 로그 확인
2. 환경변수 설정 확인
3. Procfile 확인: `web: python app.py`

**해결**:
```bash
# GitHub 재배포
git add -A
git commit -m "Fix deployment"
git push
```

### 6. 데이터 중복 에러

**증상**: "duplicate key value violates unique constraint"

**원인**: 로컬과 Koyeb 동시 실행

**해결**: 정상 동작 (에러 무시됨)
- 중복 데이터는 자동으로 skip

### 7. 타임존 문제

**증상**: 시간이 9시간 빠름 (UTC)

**해결**: 이미 수정됨 (KST 변환)
```javascript
const kstDate = new Date(date.getTime() + (9 * 60 * 60 * 1000));
```

### 8. 텔레그램 알림 안 옴

**확인**:
```python
from utils.telegram_notifier import TelegramNotifier
notifier = TelegramNotifier()
notifier.send_message("테스트")
```

**설정**:
```env
TELEGRAM_BOT_TOKEN=8289507874:AAHvAT9KNn-D7VkLrmyBzliw69UhEhiEgkM
TELEGRAM_CHAT_ID=552300458
```

## 🛠️ 디버깅 도구

### 현재 상태 확인
```python
python check_status.py
```

출력:
- 최근 30분 시그널 수
- 오픈 포지션 수
- 수집된 OHLCV 수
- 최신 데이터 시각

### 매매 안 되는 이유 분석
```python
python check_why_no_trade.py
```

출력:
- 최근 시그널 목록
- 계좌 잔고
- 리스크 검증 결과
- 실패 이유

### 데이터 확인
```python
python check_data.py
```

출력:
- OHLCV 데이터 통계
- 타임프레임별 개수

### 실제 주문 테스트
```python
# 5,500원 매수 테스트
python test_real_buy.py
```

## 📊 모니터링

### 대시보드
https://liable-margette-untab-c8b59ae3.koyeb.app/

**섹션**:
1. 계좌 상태 (총 자산, 가용 KRW)
2. 실제 보유 코인
3. 오픈 포지션
4. 최근 거래 내역
5. 전략별 성과
6. 최근 시그널

### Koyeb 로그
1. https://app.koyeb.com/ 로그인
2. Services → auto-coin
3. Logs 탭 확인

### DB 직접 확인
```python
from database import SessionLocal, Position, TradingSignal, OHLCVData
db = SessionLocal()

# 오픈 포지션
positions = db.query(Position).filter(Position.status == 'OPEN').all()
print(f"오픈 포지션: {len(positions)}개")

# 최근 시그널
from datetime import datetime, timedelta
recent = datetime.now() - timedelta(hours=1)
signals = db.query(TradingSignal).filter(
    TradingSignal.timestamp >= recent
).count()
print(f"최근 1시간 시그널: {signals}개")

# 데이터 통계
ohlcv_count = db.query(OHLCVData).count()
print(f"총 OHLCV: {ohlcv_count}개")

db.close()
```

## ⚡ 긴급 대응

### 엔진 중지
```python
# Koyeb에서 중지
# 또는 로컬에서 Ctrl+C
```

### 모든 포지션 수동 청산
```python
from database import SessionLocal, Position
from core.order_executor import OrderExecutor
from api.bithumb_client import BithumbAPI

db = SessionLocal()
executor = OrderExecutor()
api = BithumbAPI()

positions = db.query(Position).filter(Position.status == 'OPEN').all()

for pos in positions:
    # 현재가 조회
    ticker = api.get_ticker(pos.symbol)
    current_price = float(ticker['data']['closing_price'])

    # 청산
    executor.close_position(pos, current_price, "MANUAL")
    print(f"{pos.symbol} 청산 완료")

db.close()
```

### 실전 → 모의 전환
```bash
# .env 수정
TRADE_MODE=paper

# 재배포
git add .env
git commit -m "Switch to paper trading"
git push
```

## 📝 로그 분석

### 주요 로그 메시지

**정상**:
- `[DB 저장] 1분봉 100개 코인 저장 완료`
- `[OrderExecutor] 포지션 오픈: BTC BUY ...`
- `시그널 X개 생성`

**경고**:
- `데이터 부족: XXX 15m` → 정상 (데이터 수집 중)
- `최대 포지션 수 도달` → 포지션 한도 증가 필요

**에러**:
- `[OrderExecutor ERROR] 주문 실패` → 파라미터 확인
- `[DB 커밋 에러] duplicate key` → 정상 (무시됨)
- `This session is in 'prepared' state` → DB 세션 문제

## 🔧 설정 변경

### 리스크 조정
```env
# .env 수정
STOP_LOSS_PERCENT=0.03      # -3% (더 여유롭게)
TAKE_PROFIT_PERCENT=0.03    # +3% (더 자주 익절)
MAX_OPEN_POSITIONS=15       # 더 많은 기회
```

### 포지션 크기 조정
```env
MAX_POSITION_SIZE=0.15      # 15% (더 크게)
MAX_POSITION_SIZE=0.05      # 5% (더 작게)
```

### 대상 코인 변경
```python
# config.py
TARGET_PAIRS = ['BTC', 'ETH', 'XRP']  # 3개만
# 또는
TARGET_PAIRS = [...100개...]  # 전체
```

## 🆘 완전 초기화

### 1. DB 초기화
```python
from database.init_db import main as init_db
init_db()  # 모든 테이블 재생성
```

### 2. 데이터 재수집
```python
python collect_initial_data.py
```

### 3. 엔진 재시작
```bash
git push  # Koyeb 재배포
```

## 📞 문의

문제 해결 안 될 시:
1. GitHub Issues 등록
2. 텔레그램 봇으로 로그 확인
3. Koyeb 로그 스크린샷

---

**업데이트**: 2025-10-02 15:00
