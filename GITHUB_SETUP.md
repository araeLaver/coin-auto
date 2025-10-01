# 🚀 GitHub 및 Koyeb 배포 완료 가이드

## ✅ 완료된 작업

1. ✅ Git 저장소 초기화
2. ✅ 초기 커밋 생성 (40개 파일)
3. ✅ Docker 설정 완료
4. ✅ Koyeb 배포 설정 완료
5. ✅ GitHub Actions CI/CD 설정 완료

## 📋 다음 단계

### 1. GitHub에 푸시

```bash
# 리모트가 이미 추가되어 있습니다
# 이제 푸시만 하면 됩니다:

git push -u origin main
```

**첫 푸시 시 GitHub 인증이 필요합니다:**
- GitHub 계정 로그인
- Personal Access Token 입력 (비밀번호 대신)

**Personal Access Token 생성:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" 클릭
3. 권한 선택:
   - `repo` (전체 체크)
   - `workflow` (GitHub Actions용)
4. 생성된 토큰 복사 (한 번만 표시됨)
5. Git 푸시 시 비밀번호로 입력

### 2. GitHub Secrets 설정

GitHub 저장소 → Settings → Secrets and variables → Actions

**추가할 Secrets:**

```
KOYEB_TOKEN=<Koyeb API Token>
TELEGRAM_BOT_TOKEN=<텔레그램 봇 토큰>
TELEGRAM_CHAT_ID=<텔레그램 채팅 ID>
```

**선택사항 (Docker Hub 사용 시):**
```
DOCKER_USERNAME=<Docker Hub 사용자명>
DOCKER_PASSWORD=<Docker Hub 비밀번호>
```

**Koyeb API Token 발급:**
1. https://app.koyeb.com 로그인
2. Settings → API
3. "Create API Token" 클릭
4. 토큰 이름 입력 후 생성
5. 토큰 복사하여 GitHub Secrets에 추가

### 3. Koyeb 서비스 생성

#### 방법 A: Koyeb CLI (권장)

```bash
# CLI 설치 (Windows - PowerShell)
irm https://cli.koyeb.com/install.ps1 | iex

# 또는 Linux/Mac
curl -fsSL https://cli.koyeb.com/install.sh | sh

# 로그인
koyeb login

# 앱 생성
koyeb app create auto-coin-trading

# 서비스 배포
koyeb service create trading-bot \
  --app auto-coin-trading \
  --type worker \
  --instance-type eco \
  --region sin \
  --git github.com/araeLaver/coin-auto \
  --git-branch main \
  --docker-dockerfile Dockerfile \
  --docker-command "python main.py --mode run --interval 60"
```

#### 방법 B: Koyeb 웹 대시보드

1. https://app.koyeb.com → "Create Service"
2. **Git 소스 선택**
   - Provider: GitHub
   - Repository: `araeLaver/coin-auto`
   - Branch: `main`

3. **빌더 설정**
   - Builder: Dockerfile
   - Dockerfile path: `./Dockerfile`

4. **서비스 타입**
   - Type: **Worker** (중요!)

5. **인스턴스**
   - Type: Eco (무료) 또는 Standard
   - Region: Singapore (sin)

6. **환경변수 설정** (다음 섹션 참고)

7. **Deploy** 클릭

### 4. Koyeb 환경변수 설정

Koyeb 대시보드 → Service → Environment Variables

#### 필수 환경변수:

```bash
# 데이터베이스 (이미 설정됨)
DB_USER=unble
DB_PASSWORD=npg_1kjV0mhECxqs
DB_HOST=ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app
DB_NAME=unble
DB_SCHEMA=auto_coin_trading

# 거래 모드 (페이퍼로 시작!)
TRADE_MODE=paper

# 초기 설정
INITIAL_CAPITAL=1000000
MAX_POSITION_SIZE=0.1
MAX_OPEN_POSITIONS=3
STOP_LOSS_PERCENT=0.02
TAKE_PROFIT_PERCENT=0.05
MAX_DAILY_LOSS=0.05
```

#### 선택 환경변수:

```bash
# 텔레그램 알림 (선택)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# 빗썸 API (실전 모드 시 필요)
BITHUMB_API_KEY=your_key
BITHUMB_SECRET_KEY=your_secret
```

**중요:** 민감한 정보는 반드시 "Secret" 타입으로 설정!

### 5. 데이터베이스 초기화

#### 방법 A: Koyeb 쉘에서

```bash
# Koyeb CLI로 쉘 접속
koyeb service exec trading-bot -- bash

# DB 초기화
python main.py --mode init

# 종료
exit
```

#### 방법 B: 로컬에서

```bash
# 로컬에서 직접 DB 초기화
python database/init_db.py
```

## 🔄 자동 배포 프로세스

이제 GitHub에 푸시하면 자동으로:

```
코드 푸시 (git push)
    ↓
GitHub Actions 트리거
    ↓
Docker 빌드 및 테스트
    ↓
Koyeb 자동 재배포
    ↓
텔레그램 알림 (성공/실패)
```

## 📊 모니터링

### Koyeb 로그 확인

```bash
# CLI로 실시간 로그
koyeb service logs trading-bot --follow

# 웹 대시보드
https://app.koyeb.com → Services → trading-bot → Logs
```

### 데이터베이스 확인

```bash
# PostgreSQL 접속
psql postgresql://unble:npg_1kjV0mhECxqs@ep-divine-bird-a1f4mly5.ap-southeast-1.pg.koyeb.app/unble

# 스키마 설정
SET search_path TO auto_coin_trading;

# 오늘의 성과
SELECT * FROM daily_performance WHERE date = CURRENT_DATE;

# 활성 포지션
SELECT * FROM v_active_positions;
```

## 🎯 실행 순서

1. **지금 바로:**
   ```bash
   git push -u origin main
   ```

2. **GitHub Secrets 설정** (5분)
   - KOYEB_TOKEN 추가

3. **Koyeb 서비스 생성** (10분)
   - 웹 대시보드 또는 CLI 사용

4. **환경변수 설정** (5분)
   - 데이터베이스 설정 확인
   - TRADE_MODE=paper 설정

5. **DB 초기화** (1분)
   ```bash
   koyeb service exec trading-bot -- python main.py --mode init
   ```

6. **시스템 모니터링**
   ```bash
   koyeb service logs trading-bot --follow
   ```

## ⚠️ 중요 체크리스트

배포 전:
- [ ] `TRADE_MODE=paper` 확인
- [ ] 환경변수 모두 설정 완료
- [ ] GitHub Secrets 설정 완료
- [ ] .env 파일이 .gitignore에 포함되어 있는지 확인

배포 후:
- [ ] Koyeb 로그에서 에러 없는지 확인
- [ ] 데이터베이스 연결 확인
- [ ] 텔레그램 알림 수신 확인
- [ ] 24시간 안정성 모니터링

## 🐛 문제 해결

### 푸시 실패
```bash
# 인증 오류 시
git remote set-url origin https://<USERNAME>@github.com/araeLaver/coin-auto.git
git push -u origin main
```

### Koyeb 빌드 실패
- Dockerfile 확인
- 로컬에서 `docker build .` 테스트

### 서비스 시작 실패
- Koyeb 로그 확인
- 환경변수 확인
- 데이터베이스 연결 테스트

## 📞 지원

- DEPLOYMENT.md: 상세 배포 가이드
- README.md: 시스템 전체 문서
- QUICKSTART.md: 빠른 시작 가이드

## 🎉 완료!

이제 다음 명령어만 실행하면 됩니다:

```bash
git push -u origin main
```

그러면 자동으로:
1. GitHub에 코드 업로드
2. GitHub Actions 실행
3. Koyeb에 배포 준비 완료

**행운을 빕니다! 🚀**
