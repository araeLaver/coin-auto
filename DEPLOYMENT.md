# 🚀 Koyeb 배포 가이드

## 1. Koyeb 계정 설정

### 1.1 계정 생성
1. https://www.koyeb.com 접속
2. 계정 생성 (GitHub 연동 권장)

### 1.2 PostgreSQL 데이터베이스 확인
- 이미 Koyeb PostgreSQL이 설정되어 있음
- 호스트: `ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app`
- 데이터베이스: `unble`

## 2. GitHub 저장소 설정

### 2.1 저장소에 푸시

```bash
# 원격 저장소 추가
git remote add origin https://github.com/araeLaver/coin-auto.git

# 현재 변경사항 커밋
git add .
git commit -m "Initial commit: Auto coin trading system"

# main 브랜치로 푸시
git branch -M main
git push -u origin main
```

### 2.2 GitHub Secrets 설정

GitHub 저장소 → Settings → Secrets and variables → Actions에서 다음 추가:

**필수 시크릿:**
```
KOYEB_TOKEN=your_koyeb_api_token
DOCKER_USERNAME=your_docker_username (선택)
DOCKER_PASSWORD=your_docker_password (선택)
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
```

**Koyeb API Token 발급:**
1. Koyeb 대시보드 → Settings → API
2. "Create API Token" 클릭
3. 토큰 복사하여 GitHub Secrets에 저장

## 3. Koyeb 앱 생성

### 방법 1: Koyeb CLI (권장)

```bash
# Koyeb CLI 설치
curl -fsSL https://cli.koyeb.com/install.sh | sh

# 로그인
koyeb login

# 앱 생성 (koyeb.yaml 사용)
koyeb app create auto-coin-trading

# 서비스 생성
koyeb service create trading-bot \
  --app auto-coin-trading \
  --type worker \
  --instance-type eco \
  --region sin \
  --git github.com/araeLaver/coin-auto \
  --git-branch main \
  --git-build-command "docker build -t auto-coin-trading ." \
  --docker-command "python main.py --mode run --interval 60"
```

### 방법 2: Koyeb 웹 대시보드

1. **New Service 클릭**
2. **GitHub 연동**
   - Repository: `araeLaver/coin-auto`
   - Branch: `main`

3. **Service 타입 선택**
   - Type: `Worker` (웹 서버 아님)

4. **Build 설정**
   - Builder: `Dockerfile`
   - Dockerfile path: `./Dockerfile`

5. **인스턴스 설정**
   - Type: `Eco` (무료 티어) 또는 `Standard`
   - Region: `Singapore (sin)`

6. **Environment Variables 설정** (아래 참고)

7. **Deploy 클릭**

## 4. Koyeb 환경변수 설정

Koyeb 대시보드 → Service → Environment Variables에서 설정:

### 4.1 데이터베이스 (이미 설정됨)

```
DB_USER = unble
DB_PASSWORD = npg_1kjV0mhECxqs
DB_HOST = ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app
DB_NAME = unble
DB_SCHEMA = auto_coin_trading
```

### 4.2 빗썸 API (실전 모드 시)

```
BITHUMB_API_KEY = your_api_key
BITHUMB_SECRET_KEY = your_secret_key
```

⚠️ **페이퍼 모드에서는 필요 없음**

### 4.3 텔레그램 (선택)

```
TELEGRAM_BOT_TOKEN = your_bot_token
TELEGRAM_CHAT_ID = your_chat_id
```

### 4.4 거래 설정

```
TRADE_MODE = paper                # paper 또는 live
INITIAL_CAPITAL = 1000000         # 초기 자본
MAX_POSITION_SIZE = 0.1           # 최대 포지션 크기 (10%)
STOP_LOSS_PERCENT = 0.02          # 손절 비율 (2%)
TAKE_PROFIT_PERCENT = 0.05        # 익절 비율 (5%)
MAX_DAILY_LOSS = 0.05             # 일일 최대 손실 (5%)
MAX_OPEN_POSITIONS = 3            # 최대 동시 포지션
```

## 5. 데이터베이스 초기화

### 방법 1: Koyeb Shell 사용

```bash
# Koyeb CLI로 쉘 접속
koyeb service exec trading-bot -- bash

# DB 초기화
python main.py --mode init

# 종료
exit
```

### 방법 2: 로컬에서 직접 연결

```bash
# 로컬 환경에서 실행
PYTHONPATH=. python database/init_db.py
```

## 6. 자동 배포 설정 (CI/CD)

### 6.1 GitHub Actions 활성화

`.github/workflows/deploy.yml` 파일이 이미 생성되어 있습니다.

**자동 배포 흐름:**
```
main 브랜치에 push
  ↓
GitHub Actions 트리거
  ↓
Docker 이미지 빌드 및 테스트
  ↓
Koyeb 서비스 재배포
  ↓
텔레그램 알림
```

### 6.2 수동 재배포

```bash
# CLI로 재배포
koyeb service redeploy auto-coin-trading/trading-bot

# 또는 웹 대시보드에서 "Redeploy" 클릭
```

## 7. 모니터링

### 7.1 Koyeb 로그 확인

```bash
# CLI로 로그 스트리밍
koyeb service logs trading-bot --follow

# 웹 대시보드
Koyeb → Services → trading-bot → Logs
```

### 7.2 데이터베이스 모니터링

```bash
# PostgreSQL 접속
psql postgresql://unble:npg_1kjV0mhECxqs@ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app/unble

# 오늘의 성과
\c unble
SET search_path TO auto_coin_trading;
SELECT * FROM daily_performance WHERE date = CURRENT_DATE;

# 활성 포지션
SELECT * FROM v_active_positions;

# 최근 거래
SELECT * FROM trades ORDER BY closed_at DESC LIMIT 10;
```

### 7.3 텔레그램 알림

설정이 완료되면 다음 알림을 받습니다:
- 시스템 시작/중단
- 포지션 오픈/청산
- 시그널 감지
- 리스크 경고
- 일일 요약
- 배포 상태

## 8. 트러블슈팅

### 8.1 빌드 실패

```bash
# 로컬에서 Docker 테스트
docker build -t auto-coin-trading .
docker run --env-file .env auto-coin-trading
```

### 8.2 데이터베이스 연결 실패

```bash
# 네트워크 테스트
telnet ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app 5432

# 직접 연결 테스트
psql postgresql://unble:npg_1kjV0mhECxqs@ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app/unble
```

### 8.3 서비스가 계속 재시작됨

1. 로그 확인: `koyeb service logs trading-bot`
2. 환경변수 확인
3. 데이터베이스 스키마 초기화 확인

### 8.4 메모리 부족

`koyeb.yaml`에서 인스턴스 타입 변경:
```yaml
instance:
  type: standard  # eco → standard로 변경
```

## 9. 비용 관리

### Koyeb 무료 티어
- Eco 인스턴스: 무료
- 제한: 메모리 512MB, CPU 공유

### 유료 플랜 (필요시)
- Standard: $7-15/월
- Pro: $15-30/월

**추천:**
- 처음: Eco 인스턴스로 시작
- 성능 부족 시: Standard로 업그레이드

## 10. 보안 체크리스트

- [ ] 모든 민감한 정보는 환경변수로 설정
- [ ] `.env` 파일은 `.gitignore`에 포함
- [ ] GitHub Secrets 설정 완료
- [ ] Koyeb 환경변수는 "Secret" 타입으로 설정
- [ ] API 키는 최소 권한만 부여
- [ ] 정기적인 API 키 갱신

## 11. 체크리스트

배포 전:
- [ ] GitHub 저장소 생성 및 푸시
- [ ] GitHub Secrets 설정
- [ ] Koyeb 계정 생성
- [ ] Koyeb API Token 발급
- [ ] 환경변수 준비

배포:
- [ ] Koyeb 서비스 생성
- [ ] 환경변수 설정
- [ ] 데이터베이스 초기화
- [ ] 첫 배포 확인

배포 후:
- [ ] 로그 확인
- [ ] 텔레그램 알림 테스트
- [ ] 데이터베이스 연결 확인
- [ ] 페이퍼 트레이딩 시작
- [ ] 24시간 안정성 모니터링

## 12. 유용한 명령어

```bash
# 서비스 상태 확인
koyeb service list

# 서비스 상세 정보
koyeb service describe trading-bot

# 로그 실시간 스트리밍
koyeb service logs trading-bot --follow

# 서비스 재시작
koyeb service redeploy trading-bot

# 서비스 중단
koyeb service pause trading-bot

# 서비스 재개
koyeb service resume trading-bot

# 환경변수 확인
koyeb service env trading-bot

# 서비스 삭제
koyeb service delete trading-bot
```

## 13. 다음 단계

1. **24시간 데이터 수집**
   - 서비스를 `collect` 모드로 먼저 실행
   - 충분한 데이터 확보

2. **1주일 페이퍼 트레이딩**
   - 시스템 안정성 확인
   - 전략 성과 분석

3. **소액 실전**
   - `TRADE_MODE=live`로 변경
   - 10만원 이하로 시작

4. **점진적 확대**
   - 성과 모니터링
   - 파라미터 최적화

---

**문제 발생 시:**
- Koyeb 로그 확인
- GitHub Issues 생성
- 텔레그램 알림 확인
