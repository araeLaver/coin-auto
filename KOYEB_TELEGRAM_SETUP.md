# Koyeb 텔레그램 환경변수 설정

## 🔐 Koyeb에 환경변수 추가하기

### 1. Koyeb 대시보드 접속
https://app.koyeb.com

### 2. 서비스 선택
- 왼쪽 메뉴에서 **Services** 클릭
- **auto-coin-trading** (또는 서비스 이름) 선택

### 3. Settings 이동
- **Settings** 탭 클릭
- **Environment variables** 섹션으로 스크롤

### 4. 환경변수 추가

**추가할 변수 2개:**

#### Variable 1:
```
Name: TELEGRAM_BOT_TOKEN
Value: 8289507874:AAHvAT9KNn-D7VkLrmyBzliw69UhEhiEgkM
Type: Plain text (또는 Secret 권장)
```

#### Variable 2:
```
Name: TELEGRAM_CHAT_ID
Value: 552300458
Type: Plain text
```

#### Variable 3 (초기자본 업데이트):
```
Name: INITIAL_CAPITAL
Value: 234248
Type: Plain text
```

### 5. 저장 및 재배포
- 하단의 **Update service** 버튼 클릭
- 자동으로 재배포 시작 (1-2분 소요)

### 6. 확인
재배포 완료 후 텔레그램으로 다음 메시지를 받게 됩니다:

```
🚀 Auto Coin Trading 시작
⚙️ 모드: LIVE
💰 초기자본: 234,248원
🎯 대상코인: BTC, ETH, XRP, ADA, SOL
```

---

## ✅ 완료 체크리스트

- [x] Chat ID 확인: 552300458
- [x] 로컬 .env 파일 설정
- [ ] Koyeb TELEGRAM_BOT_TOKEN 추가
- [ ] Koyeb TELEGRAM_CHAT_ID 추가
- [ ] Koyeb INITIAL_CAPITAL 업데이트
- [ ] Update service 클릭
- [ ] 텔레그램 시작 메시지 수신 확인

---

## 📱 받게 될 알림

### 즉시 받을 알림:
- ✅ 시스템 시작 알림

### 거래 시 받을 알림:
- 🔵 시그널 감지 (BUY/SELL)
- 🟢 포지션 오픈 (매수 체결)
- 🔴 포지션 청산 (매도 체결)
- ⚠️ 리스크 경고
- 📈 일일 요약 (자정)

---

**설정이 완료되면 모든 거래를 실시간으로 받습니다!**
