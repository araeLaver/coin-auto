# 📱 텔레그램 알림 연동 가이드

## 🤖 1단계: 봇 생성

### 1-1. BotFather와 대화 시작
1. 텔레그램 앱 열기
2. 검색창에 `@BotFather` 입력
3. **BotFather** (파란색 체크마크) 클릭
4. `/start` 입력

### 1-2. 새 봇 만들기
```
/newbot
```

### 1-3. 봇 이름 입력
```
예: Auto Coin Trading Bot
```
- 원하는 이름 아무거나 (나만 볼 수 있음)

### 1-4. 봇 사용자명 입력
```
예: your_name_coin_bot
```
- 반드시 `bot`으로 끝나야 함
- 전세계에서 유일해야 함 (이미 사용 중이면 다른 이름)

### 1-5. 토큰 받기
BotFather가 다음과 같은 메시지를 보냄:
```
Done! Congratulations on your new bot.
...
Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
               ↑↑↑ 이것이 봇 토큰!
```

**🔑 이 토큰을 복사하세요!**

---

## 💬 2단계: Chat ID 얻기

### 2-1. 내 봇과 대화 시작
1. BotFather 메시지에서 봇 링크 클릭 (예: `t.me/your_name_coin_bot`)
2. 또는 텔레그램 검색에서 봇 사용자명으로 검색
3. `/start` 입력
4. 아무 메시지나 입력 (예: "hello")

### 2-2. Chat ID 조회
웹 브라우저에서 다음 URL 접속:
```
https://api.telegram.org/bot<봇토큰>/getUpdates
```

**예시**:
```
https://api.telegram.org/bot1234567890:ABCdefGHI.../getUpdates
```

### 2-3. Chat ID 찾기
응답에서 `chat` 부분을 찾으세요:
```json
{
  "ok": true,
  "result": [
    {
      "message": {
        "chat": {
          "id": 123456789,  ← 이것이 Chat ID!
          "first_name": "Your Name",
          ...
        }
      }
    }
  ]
}
```

**🔑 숫자를 복사하세요!** (예: `123456789`)

---

## ⚙️ 3단계: 환경변수 설정

### 로컬 테스트 (.env 파일)

`.env` 파일을 열고 수정:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
TELEGRAM_CHAT_ID=123456789
```

### Koyeb 배포 (프로덕션)

1. https://app.koyeb.com 접속
2. 서비스 선택
3. **Settings** → **Environment variables** 클릭
4. 추가:
   ```
   TELEGRAM_BOT_TOKEN = 1234567890:ABCdefGHI...
   TELEGRAM_CHAT_ID = 123456789
   ```
5. **Update service** 클릭 (자동 재배포)

---

## 🧪 4단계: 테스트

### 로컬에서 테스트
```bash
python utils/telegram_notifier.py
```

성공하면 텔레그램으로 테스트 메시지 받음!

### 또는 Python 직접 실행
```python
from utils.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()
notifier.send_message("테스트 메시지입니다!")
```

---

## 📬 받게 될 알림 종류

### 1. 시스템 알림
```
🚀 Auto Coin Trading 시작
⚙️ 모드: LIVE
💰 초기자본: 234,248원
🎯 대상코인: BTC, ETH, XRP, ADA, SOL
```

### 2. 시그널 알림
```
🔵 시그널 감지
💰 코인: BTC
📊 시그널: BUY
⚡️ 강도: 85/100
🔍 신뢰도: 72.5%
💵 가격: 168,416,000원
🎯 목표가: 176,836,000원
🛡 손절가: 164,887,000원
📈 전략: Trend Following
```

### 3. 거래 체결 알림
```
🟢 포지션 오픈
💰 코인: BTC
📊 방향: LONG
💵 진입가: 168,416,000원
📦 수량: 0.00013920
💸 투자금: 23,424원
🎯 익절가: 176,836,000원
🛡 손절가: 164,887,000원
```

### 4. 청산 알림
```
🟢 포지션 청산
💰 코인: BTC
💵 진입가: 168,416,000원
💵 청산가: 176,836,000원
💰 손익: +1,171원 (+5.00%)
⏱ 보유시간: 2.3시간
📝 청산이유: TAKE_PROFIT
```

### 5. 일일 요약
```
📈 일일 거래 요약
📅 날짜: 2025-10-02
💰 시작 잔고: 234,248원
💰 종료 잔고: 237,891원
💰 손익: +3,643원 (+1.56%)
📊 총 거래: 8건
✅ 수익: 6건
❌ 손실: 2건
📈 승률: 75.0%
```

### 6. 리스크 경고
```
⚠️ 리스크 경고
🚨 경고: 일일 손실 한도 근접
📊 상세: 현재 손실 -4.2% (한도 -5%)
```

---

## 🔧 문제 해결

### "Failed to send message"
- 봇 토큰이 맞는지 확인
- Chat ID가 맞는지 확인
- 봇과 대화를 시작했는지 확인 (/start 입력)

### getUpdates 결과가 빈 배열 []
- 봇에게 메시지를 보냈는지 확인
- 최소 1개 이상 메시지를 보내야 함

### Chat ID를 못 찾겠어요
다른 방법:
1. 봇과 대화 시작
2. `@userinfobot`에게 메시지 보내기
3. 내 Chat ID 확인 가능

---

## ✅ 완료 체크리스트

- [ ] BotFather에서 봇 생성
- [ ] 봇 토큰 복사
- [ ] 봇과 대화 시작 (/start)
- [ ] Chat ID 확인
- [ ] .env 파일에 설정
- [ ] 로컬에서 테스트
- [ ] Koyeb 환경변수 설정
- [ ] 재배포 후 알림 확인

---

## 📞 도움이 필요하면

1. BotFather 공식 가이드: https://core.telegram.org/bots
2. 또는 제게 물어보세요!

**알림 설정이 완료되면 모든 거래를 실시간으로 받을 수 있습니다! 📱**
