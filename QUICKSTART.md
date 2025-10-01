# 🚀 빠른 시작 가이드

## 1단계: 설치 (5분)

```bash
# 1. 저장소 클론 (이미 완료)
cd C:\Develop\unble\auto-coin

# 2. 가상환경 생성 (권장)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt
```

## 2단계: 설정 (3분)

### 필수 설정

`.env` 파일이 이미 생성되어 있습니다. 다음만 설정하세요:

```
TRADE_MODE=paper  # 처음에는 반드시 paper로!
```

데이터베이스는 이미 설정되어 있습니다.

### 선택적 설정 (나중에 해도 됨)

```
# 텔레그램 알림 (선택)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 3단계: 데이터베이스 초기화 (1분)

```bash
python main.py --mode init
```

## 4단계: 데이터 수집 (24시간 권장)

```bash
python main.py --mode collect
```

- 최소 24시간 수집 권장
- Ctrl+C로 중단 가능
- 백그라운드 실행 가능

**백그라운드 실행 (Windows):**
```bash
start /B python main.py --mode collect > collect.log 2>&1
```

**백그라운드 실행 (Linux/Mac):**
```bash
nohup python main.py --mode collect > collect.log 2>&1 &
```

## 5단계: 페이퍼 트레이딩 시작

### 방법 1: 간단한 실행

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

### 방법 2: 직접 실행

```bash
python main.py --mode run --interval 60
```

## 6단계: 모니터링

### 데이터베이스에서 확인

```sql
-- 오늘의 성과
SELECT * FROM auto_coin_trading.daily_performance
WHERE date = CURRENT_DATE;

-- 활성 포지션
SELECT * FROM auto_coin_trading.v_active_positions;

-- 최근 거래
SELECT * FROM auto_coin_trading.trades
ORDER BY closed_at DESC
LIMIT 10;
```

### 로그 확인

```bash
tail -f collect.log
```

## ⚠️ 실전 거래 전 체크리스트

실전 모드(`TRADE_MODE=live`)로 전환하기 전:

- [ ] 최소 1주일 페이퍼 트레이딩 완료
- [ ] 페이퍼 트레이딩 승률 55% 이상
- [ ] 시스템 안정성 확인 (에러 없이 작동)
- [ ] 빗썸 API Key 발급
- [ ] API Key를 `.env`에 입력
- [ ] 소액으로 시작 (10만원 이하)
- [ ] 텔레그램 알림 설정

## 📊 예상 결과 (페이퍼 트레이딩)

**첫 주:**
- 승률: 45-55%
- 일평균 거래: 3-7건
- AI가 전략 학습 중

**2주차 이후:**
- 승률: 55-65%
- AI가 최적 전략 선택
- 시장 상황별 대응 개선

## 🆘 문제 해결

### 데이터베이스 연결 실패
```bash
# config.py에서 DB 설정 확인
```

### 빗썸 API 에러
- 아직 페이퍼 모드라면 정상 (API 키 불필요)
- 실전 모드: API 키 권한 확인

### 메모리 부족
```python
# config.py에서 대상 코인 줄이기
TARGET_PAIRS = ['BTC', 'ETH']  # 2개로 축소
```

## 🎯 다음 단계

1. **1주일 페이퍼 트레이딩** 후
2. **성과 분석** (승률, 수익률)
3. **전략 파라미터 조정** (필요시)
4. **소액 실전** (10만원)
5. **점진적 확대**

## 📞 도움말

- README.md: 전체 문서
- config.py: 모든 설정 파라미터
- 데이터베이스 스키마: database/schema.sql

---

**시작하세요!**

```bash
# Windows
run.bat

# Linux/Mac
./run.sh
```
