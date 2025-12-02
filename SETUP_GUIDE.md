# Pokemon GO Tracker - 빠른 시작 가이드

## 🚀 빠른 시작 (Docker 사용 - 추천)

### 1. 필수 요구사항
- Docker & Docker Compose
- SendGrid API 키 (무료 계정으로 충분)
- (선택사항) YouTube Data API v3 키

### 2. 설치 단계

```bash
# 1. 프로젝트 폴더로 이동
cd pokemon-go-tracker

# 2. 환경 변수 설정
cp .env.example .env

# 3. .env 파일 편집 (SendGrid API 키 입력 필수)
nano .env
```

**.env 파일 예시:**
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
NOTIFICATION_EMAIL=your-email@gmail.com
```

```bash
# 4. Docker Compose로 모든 서비스 시작
docker-compose up -d

# 5. 데이터베이스 마이그레이션 실행
docker-compose exec backend alembic upgrade head

# 6. 완료! 브라우저에서 접속
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

## 📱 기능 소개

### 1️⃣ 이벤트 뉴스 (메인 페이지)
- 포켓몬고 공식 사이트에서 최신 이벤트 자동 크롤링
- 30분마다 자동으로 새 이벤트 확인
- 이메일 구독 기능으로 새 이벤트 알림 받기

### 2️⃣ IV 계산기
- 포켓몬 스크린샷 업로드
- OCR로 자동 CP/HP 인식
- IV 퍼센티지, 공격/방어/체력 개체값 계산
- 배틀/레이드 등급 제공
- 육성 추천 및 기술 추천

### 3️⃣ 배틀 영상
- 유명 포켓몬고 배틀 유튜버 영상 자동 수집
- FPSticks, HomeSliceHenry, ZyoniK 등 수상 경력 유튜버
- 섬네일 및 링크로 편리한 시청

### 4️⃣ 이메일 구독 관리
- 메인 페이지에서 이메일 입력 및 수정
- 새 이벤트 발생 시 자동 이메일 발송
- 언제든지 구독 취소 가능

## 🛠 로컬 개발 환경 설정

### Backend (FastAPI)

```bash
cd backend

# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# Tesseract OCR 설치 (IV 계산기용)
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr

# Windows
# https://github.com/UB-Mannheim/tesseract/wiki 에서 다운로드

# PostgreSQL 설치 및 데이터베이스 생성
createdb pokemon_go_db

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 시작
python run.py
```

Backend는 http://localhost:8000 에서 실행됩니다.

### Frontend (Next.js)

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm run dev
```

Frontend는 http://localhost:3000 에서 실행됩니다.

## 🔧 설정 옵션

### Backend 환경 변수 (.env)

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `DATABASE_URL` | PostgreSQL 연결 문자열 | ✅ |
| `SENDGRID_API_KEY` | SendGrid API 키 | ✅ |
| `SENDGRID_FROM_EMAIL` | 발신 이메일 주소 | ✅ |
| `NOTIFICATION_EMAIL` | 기본 수신 이메일 | ✅ |
| `YOUTUBE_API_KEY` | YouTube Data API v3 키 | ❌ (없으면 Mock 데이터 사용) |
| `CRAWLER_INTERVAL_MINUTES` | 크롤링 주기 (기본: 30분) | ❌ |
| `TESSERACT_CMD` | Tesseract 실행 파일 경로 | ❌ |

### YouTube API 키 발급 (선택사항)

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. "API 및 서비스" > "라이브러리"에서 "YouTube Data API v3" 활성화
4. "사용자 인증 정보" > "API 키" 생성
5. `.env` 파일에 `YOUTUBE_API_KEY=your_api_key` 추가

**참고:** YouTube API 키가 없어도 Mock 데이터로 작동합니다.

### SendGrid 설정

1. [SendGrid](https://sendgrid.com/) 가입 (무료 플랜 사용 가능)
2. Settings > API Keys > Create API Key
3. "Full Access" 권한으로 생성
4. API 키를 `.env` 파일에 추가
5. Sender Identity 인증 (발신자 이메일 확인)

## 📊 API 엔드포인트

### 이벤트 API
- `GET /api/events` - 이벤트 목록 조회
- `GET /api/events/{id}` - 특정 이벤트 조회
- `POST /api/events/crawl` - 수동 크롤링 실행

### IV 분석 API
- `POST /api/analysis/upload` - 스크린샷 업로드 및 분석
- `GET /api/analysis/history` - 분석 기록 조회
- `GET /api/analysis/{id}` - 특정 분석 결과 조회

### YouTube 영상 API
- `GET /api/videos` - 배틀 영상 목록 조회
- `POST /api/videos/refresh` - 수동 영상 업데이트

### 이메일 구독 API
- `POST /api/subscriptions` - 이메일 구독
- `GET /api/subscriptions/{email}` - 구독 상태 확인
- `PUT /api/subscriptions/{email}` - 이메일 변경
- `DELETE /api/subscriptions/{email}` - 구독 취소

자세한 API 문서: http://localhost:8000/docs

## 🔍 문제 해결

### Q: 이벤트가 표시되지 않아요
**A:** 수동으로 크롤링을 실행해보세요:
```bash
curl -X POST http://localhost:8000/api/events/crawl
```

### Q: IV 계산이 정확하지 않아요
**A:**
- 스크린샷이 선명한지 확인하세요
- 포켓몬 이름, CP, HP가 명확하게 보이는지 확인하세요
- Tesseract OCR이 올바르게 설치되었는지 확인하세요

### Q: 이메일이 전송되지 않아요
**A:**
- SendGrid API 키가 유효한지 확인하세요
- SendGrid에서 발신자 이메일이 인증되었는지 확인하세요
- SendGrid 대시보드에서 이메일 전송 로그를 확인하세요

### Q: YouTube 영상이 표시되지 않아요
**A:**
- YouTube API 키가 없으면 Mock 데이터가 표시됩니다
- API 키가 있다면 할당량을 확인하세요 (일일 10,000 units)

## 📝 데이터베이스 관리

### 새 마이그레이션 생성
```bash
cd backend
alembic revision --autogenerate -m "설명"
```

### 마이그레이션 적용
```bash
alembic upgrade head
```

### 마이그레이션 롤백
```bash
alembic downgrade -1
```

## 🚀 배포

### Docker Compose로 프로덕션 배포

```bash
# 프로덕션 환경 변수 설정
cp .env.example .env
nano .env  # DEBUG=False 설정

# 백그라운드에서 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 개별 서비스 재시작
```bash
docker-compose restart backend
docker-compose restart frontend
```

## 📚 추가 정보

- 메인 README: [README.md](README.md)
- API 문서: http://localhost:8000/docs
- 프로젝트 GitHub: (여기에 GitHub 링크 추가)

## 💡 팁

1. **크롤링 주기 조정**: `.env`에서 `CRAWLER_INTERVAL_MINUTES` 값 변경
2. **더 많은 유튜버 추가**: `backend/app/services/youtube_service.py`에서 `POKEMON_GO_BATTLE_CHANNELS` 수정
3. **포켓몬 베이스 스탯 추가**: `backend/app/services/iv_calculator.py`에서 `POKEMON_BASE_STATS` 수정

## 🤝 기여

버그 리포트나 기능 제안은 GitHub Issues를 통해 알려주세요!

---

즐거운 포켓몬고 하세요! ⚡️
