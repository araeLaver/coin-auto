# 📊 자동매매 대시보드 가이드

## 🎯 개요

웹 브라우저에서 실시간으로 자동매매 상태를 모니터링할 수 있는 대시보드입니다.

## 🚀 로컬 실행

### 방법 1: 대시보드만 실행
```bash
python dashboard.py
```
- 접속: http://localhost:8080
- 자동매매는 별도로 실행 필요

### 방법 2: 대시보드 + 자동매매 동시 실행 (권장)
```bash
python run_all.py
```
- 대시보드: http://localhost:8080
- 자동매매: 백그라운드 실행

### 방법 3: 자동매매만 실행
```bash
python main.py --mode run --interval 60
```
- 대시보드 없이 트레이딩만 실행

## 📱 대시보드 기능

### 1. 실시간 상태
- **모드**: paper (모의) / live (실전)
- **총 자산**: 현재 보유 금액
- **가용 금액**: 매수 가능 금액
- **오픈 포지션**: 현재 보유 중인 포지션 수
- **오늘 거래**: 오늘 체결된 거래 수

### 2. 요약 통계
- 총 거래 수
- 승률 (%)
- 총 손익 (KRW)
- 총 수익률 (%)

### 3. 현재 오픈 포지션
- 심볼, 타입, 진입가, 현재가
- 실시간 손익 및 손익률
- 보유 시간

### 4. 최근 거래 내역
- 진입/청산 가격
- 손익 및 손익률
- 종료 사유 (STOP_LOSS, TAKE_PROFIT 등)
- 보유 시간

### 5. 전략별 성과
- 각 전략의 거래 수
- 전략별 총 손익
- 전략별 승률

### 6. 최근 시그널
- 생성된 매매 시그널
- 신뢰도 및 강도
- 시그널 발생 사유

## 🔄 자동 새로고침

- **10초마다 자동 갱신**
- 별도의 새로고침 버튼 불필요
- 우측 상단에 자동 새로고침 표시

## 🌐 Koyeb 배포 (클라우드)

### Procfile 구성
```
web: python dashboard.py          # 대시보드 (포트 8000)
worker: python main.py --mode run # 자동매매 백그라운드
```

### 배포 후 접속
```
https://your-app-name.koyeb.app
```

## 📊 API 엔드포인트

대시보드는 다음 REST API를 제공합니다:

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /` | 대시보드 메인 페이지 |
| `GET /api/status` | 시스템 상태 |
| `GET /api/positions` | 현재 오픈 포지션 |
| `GET /api/trades` | 최근 거래 내역 (50건) |
| `GET /api/performance` | 일일 성과 (30일) |
| `GET /api/signals` | 최근 시그널 (20건) |
| `GET /api/strategies` | 전략별 성과 |
| `GET /api/summary` | 전체 요약 통계 |

### API 사용 예시
```bash
# 시스템 상태 조회
curl http://localhost:8080/api/status

# 현재 포지션 조회
curl http://localhost:8080/api/positions

# 전략 성과 조회
curl http://localhost:8080/api/strategies
```

## 🎨 UI 특징

- **다크 테마**: 눈의 피로 감소
- **반응형 디자인**: 모바일/태블릿 지원
- **실시간 색상**: 수익(녹색), 손실(빨간색)
- **깔끔한 레이아웃**: 정보 한눈에 파악

## ⚙️ 설정

### 포트 변경
```python
# dashboard.py 마지막 줄
app.run(host='0.0.0.0', port=원하는포트, debug=False)
```

### 자동 새로고침 주기 변경
```javascript
// templates/dashboard.html 마지막 부분
setInterval(loadAll, 10000);  // 10000 = 10초
```

## 🔒 보안 주의사항

⚠️ **프로덕션 환경에서는 다음을 권장합니다:**

1. **인증 추가**: Flask-Login 또는 JWT 사용
2. **HTTPS 사용**: SSL/TLS 인증서 적용
3. **API Rate Limiting**: 과도한 요청 차단
4. **방화벽 설정**: 특정 IP만 접근 허용

## 🐛 문제 해결

### 대시보드가 안 열려요
```bash
# Flask 설치 확인
pip install flask

# 포트 충돌 확인
netstat -ano | findstr :8080  # Windows
lsof -i :8080                 # Mac/Linux
```

### 데이터가 안 보여요
1. DB 연결 확인: `.env` 파일 확인
2. 자동매매 실행 확인: `python main.py --mode run`
3. 데이터베이스 초기화: `python main.py --mode init`

### API 에러가 발생해요
- 브라우저 콘솔(F12) 확인
- 네트워크 탭에서 실패한 요청 확인
- DB 연결 상태 점검

## 📱 모바일 접속

1. **같은 Wi-Fi 연결**
2. **PC IP 확인**:
   ```bash
   ipconfig           # Windows
   ifconfig           # Mac/Linux
   ```
3. **모바일 브라우저에서 접속**:
   ```
   http://192.168.x.x:8080
   ```

## 🎯 활용 팁

1. **북마크 추가**: 자주 보는 페이지는 북마크
2. **듀얼 모니터**: 대시보드를 별도 모니터에 띄우기
3. **알림 설정**: 텔레그램 봇과 병행 사용
4. **정기 체크**: 하루 2-3회 대시보드 확인

## 📈 향후 개선 계획

- [ ] 실시간 차트 추가 (Chart.js)
- [ ] 알림 설정 UI
- [ ] 전략 파라미터 조정 UI
- [ ] 백테스팅 결과 시각화
- [ ] 손익 그래프
- [ ] WebSocket 실시간 업데이트

---

**즐거운 트레이딩 되세요! 📊🚀**
