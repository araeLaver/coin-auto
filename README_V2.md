# 🤖 Auto Coin Trading System V2 - 완전 작동 버전

**실제로 작동하는 빗썸 자동 암호화폐 매매 시스템**

## ⚡ V2의 차이점

| 기능 | V1 | V2 |
|------|----|----|
| 데이터 수집 | 수동 실행 필요 | ✅ 백그라운드 자동 수집 |
| 매수 실행 | ✅ 작동 | ✅ 작동 |
| 매도 실행 | ❌ 수동 | ✅ 완전 자동 (손절/익절) |
| 포지션 관리 | ❌ 없음 | ✅ 실시간 자동 |
| 통합 테스트 | ❌ 없음 | ✅ test_system.py |
| 에러 복구 | ❌ 크래시 | ✅ 자동 복구 |
| 실시간 알림 | ⚠️ 부분적 | ✅ 완전 통합 |

## 🚀 3단계 시작

### 1. 설치
```bash
pip install -r requirements.txt
```

### 2. 초기화
```bash
python main.py --mode init
```

### 3. 시작
```bash
python main.py --mode run
```

## ✨ 핵심 기능

### 1. 완전 자동 매매
- ✅ 자동 매수 (4개 전략)
- ✅ 자동 매도 (손절/익절)
- ✅ 트레일링 스톱
- ✅ 일일 손실 한도

### 2. 실시간 데이터
- 가격: 5초마다
- 호가창: 1초마다
- 지표: 60초마다

### 3. 리스크 관리
- 포지션당 최대 10%
- 자동 손절 -2%
- 자동 익절 +5%
- 최대 3개 동시 포지션

### 4. 차별화 전략
- 🔥 호가창 불균형 분석
- 📈 추세 추종
- 📉 평균 회귀
- 🚀 모멘텀 돌파

## 📊 실제 작동 예시

```
[사이클 #1] 2025-01-15 10:30:00

[BTC] 현재가: 85,000,000원
  시그널 2개 생성
  최적 시그널: BUY (Trend Following, 신뢰도: 75%)
  포지션 크기: 100,000원
  ✓ 포지션 오픈 성공: 1

[사이클 #2] 2025-01-15 10:31:00

[BTC] 현재가: 89,300,000원
  ✓ 포지션 청산: BTC (이유: TAKE_PROFIT)
  수익: +5,060원 (+5.06%)
```

## 🧪 테스트

```bash
python test_system.py
```

**출력:**
```
[1/10] 데이터베이스 연결 테스트... ✓
[2/10] 빗썸 API 연결 테스트... ✓
[3/10] 데이터 수집 테스트... ✓
...
총 10/10 테스트 통과
✅ 시스템 정상 작동 준비 완료
```

## 📱 텔레그램 알림

실시간 알림 받기:
- 포지션 오픈/청산
- 손익 현황
- 리스크 경고
- 시스템 상태

## ⚙️ 설정

`.env` 파일:
```bash
TRADE_MODE=paper              # paper 또는 live
INITIAL_CAPITAL=1000000       # 초기 자본
MAX_POSITION_SIZE=0.1         # 최대 10%
STOP_LOSS_PERCENT=0.02        # 2% 손절
TAKE_PROFIT_PERCENT=0.05      # 5% 익절
MAX_DAILY_LOSS=0.05           # 일일 5% 한도
MAX_OPEN_POSITIONS=3          # 최대 3개
```

## 📚 문서

- **SYSTEM_COMPLETE.md** - 완전한 사용 가이드
- **DEPLOYMENT.md** - Koyeb 배포
- **QUICKSTART.md** - 빠른 시작
- **test_system.py** - 통합 테스트

## ⚠️ 중요!

1. **페이퍼 모드로 시작** (기본값)
2. **1주일 테스트 후** 실전
3. **소액부터 시작** (10만원 이하)
4. **리스크 관리 필수**

## 🐛 문제 해결

### 시그널은 생성되는데 매매 안됨?
→ V2를 사용하세요! `main.py`가 `TradingEngineV2`를 사용하는지 확인

### 데이터 부족 에러?
→ 30초 대기하면 자동 수집됩니다

### 텔레그램 알림 안옴?
→ `.env`에 봇 토큰과 Chat ID 설정

## 🎯 성과 확인

```sql
-- 오늘의 거래
SELECT * FROM auto_coin_trading.trades
WHERE closed_at >= CURRENT_DATE;

-- 현재 포지션
SELECT * FROM auto_coin_trading.v_active_positions;

-- 승률
SELECT
    ROUND(SUM(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) as win_rate
FROM auto_coin_trading.trades;
```

## 🚀 배포 (Koyeb)

```bash
git push origin main
```

GitHub Actions가 자동으로:
1. Docker 빌드
2. Koyeb 배포
3. 텔레그램 알림

자세한 내용: `DEPLOYMENT.md`

## 📞 지원

- **GitHub Issues**: 버그 리포트
- **SYSTEM_COMPLETE.md**: 상세 가이드
- **test_system.py**: 문제 진단

## 📄 라이센스

MIT License

---

## ⚡ 빠른 명령어

```bash
# 초기화
python main.py --mode init

# 테스트
python test_system.py

# 실행
python main.py --mode run

# Windows 간편 실행
run.bat

# Linux/Mac 간편 실행
./run.sh
```

---

**🎉 완전히 작동하는 자동매매 시스템을 만나보세요!**

**주의**: 암호화폐 투자는 고위험입니다. 손실 가능한 금액만 투자하세요.
