# 배포 가이드 - Render.com + Vercel

이 가이드는 Pokemon GO Tracker를 Render.com (백엔드)과 Vercel (프론트엔드)에 배포하는 방법을 설명합니다.

## 📦 배포 아키텍처

- **프론트엔드**: Vercel (이미 배포됨 - https://pokemon-go-tracker.vercel.app)
- **백엔드**: Render.com (무료 플랜)
- **데이터베이스**: SQLite (Render 디스크에 저장)

---

## 🚀 1단계: Render.com 계정 생성

1. [Render.com](https://render.com) 접속
2. **Sign Up** 클릭
3. GitHub 계정으로 로그인

---

## 🔧 2단계: 백엔드 배포

### A. Render에서 Web Service 생성

1. Render 대시보드에서 **New +** 클릭
2. **Web Service** 선택
3. GitHub 저장소 연결:
   - Repository: `freeuth/pokemon-go-tracker` 선택
   - **Connect** 클릭

### B. 서비스 설정

다음 정보를 입력하세요:

**기본 설정:**
- **Name**: `pokemon-go-tracker-backend`
- **Region**: `Oregon (US West)` (또는 가장 가까운 지역)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**빌드 & 실행 명령:**
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**인스턴스 타입:**
- **Instance Type**: `Free` 선택

### C. 환경 변수 설정

**Environment Variables** 섹션에서 다음을 추가하세요:

```
MODE=production
DATABASE_URL=sqlite:///./pokemon_go.db

# Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=treehi1@gmail.com
SMTP_PASSWORD=ezpftysfzozwdoag
EMAIL_FROM=treehi1@gmail.com
NOTIFICATION_EMAIL=treehi1@gmail.com

# Frontend URL
FRONTEND_URL=https://pokemon-go-tracker.vercel.app

# Crawler Settings
CRAWLER_INTERVAL_MINUTES=30
POKEMONGO_NEWS_URL=https://pokemongolive.com/ko/post/

# YouTube RSS Feeds
YOUTUBE_RSS_FEEDS=https://www.youtube.com/feeds/videos.xml?channel_id=UCdr_Wan875nODI7QyAmxtPg,https://www.youtube.com/feeds/videos.xml?channel_id=UC_zHkjuptaH8SEc83KTFqog,https://www.youtube.com/feeds/videos.xml?channel_id=UCeTdRAJjiQ299P_p--0Op7g,https://www.youtube.com/feeds/videos.xml?channel_id=UCfoSf_Kr6WxhfDCoH1elk9Q,https://www.youtube.com/feeds/videos.xml?channel_id=UCyGyht0Dv0Knt7bUB-ZQEkQ,https://www.youtube.com/feeds/videos.xml?channel_id=UCNk_2WQ8kdo16wJD7XSvDmg,https://www.youtube.com/feeds/videos.xml?channel_id=UCIknZLG6_estRW_rHVYNbeA,https://www.youtube.com/feeds/videos.xml?channel_id=UCWNAsZwR-I219wzIKdTQ-Gg,https://www.youtube.com/feeds/videos.xml?channel_id=UCIqDCG3pWKWKviFytutCs8w,https://www.youtube.com/feeds/videos.xml?channel_id=UCMU4_bvUD-zmpFYX-f2ndAQ

# CORS
ALLOWED_ORIGINS=["https://pokemon-go-tracker.vercel.app", "http://localhost:3000"]
```

### D. 배포 시작

1. **Create Web Service** 클릭
2. 배포가 시작되고 로그를 확인할 수 있습니다
3. 배포 완료 후 URL을 확인하세요 (예: `https://pokemon-go-tracker-backend.onrender.com`)

---

## 🌐 3단계: Vercel 환경 변수 업데이트

Render에서 백엔드 URL을 확인한 후:

1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. `pokemon-go-tracker` 프로젝트 선택
3. **Settings** → **Environment Variables** 이동
4. 새 환경 변수 추가:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://pokemon-go-tracker-backend.onrender.com` (Render에서 제공한 실제 URL)
   - **Environment**: `Production`, `Preview`, `Development` 모두 체크
5. **Save** 클릭
6. **Deployments** 탭으로 이동
7. 가장 최근 배포에서 **...** 클릭 → **Redeploy** 선택

---

## ✅ 4단계: 배포 확인

### 백엔드 확인

브라우저에서 백엔드 URL을 열어보세요:
```
https://pokemon-go-tracker-backend.onrender.com/
```

다음과 같은 JSON 응답이 나와야 합니다:
```json
{
  "message": "Pokemon GO Tracker API",
  "version": "1.0.0",
  "endpoints": {
    "events": "/api/events",
    "analysis": "/api/analysis",
    "videos": "/api/videos",
    "subscriptions": "/api/subscriptions",
    "docs": "/docs"
  }
}
```

### 프론트엔드 확인

브라우저에서 프론트엔드를 열어보세요:
```
https://pokemon-go-tracker.vercel.app
```

뉴스와 영상이 제대로 로드되는지 확인하세요!

---

## ⚠️ 중요 사항

### Render 무료 플랜 제약사항

- **스핀다운**: 15분 동안 요청이 없으면 서버가 중지됩니다
- **재시작 시간**: 첫 요청 시 30초~1분 정도 소요될 수 있습니다
- **월 750시간**: 무료 플랜은 월 750시간 실행 시간 제공
- **SQLite 데이터**: Render 재시작 시 데이터가 유지됩니다 (디스크에 저장됨)

### 스케줄러 동작

- 매일 오전 10시(Asia/Seoul)에 뉴스 및 YouTube 영상 수집
- Render 서버가 스핀다운 상태여도 첫 요청 시 자동으로 재시작됩니다
- 하지만 스케줄러는 서버가 실행 중일 때만 작동합니다

### 데이터 지속성

- SQLite 데이터베이스는 Render의 디스크에 저장됩니다
- 무료 플랜의 경우 재배포 시 데이터가 초기화될 수 있습니다
- 프로덕션에서는 PostgreSQL 사용을 권장합니다

---

## 🔒 보안

- ✅ `.env` 파일은 `.gitignore`에 포함되어 GitHub에 업로드되지 않습니다
- ✅ Gmail 앱 비밀번호는 Render 환경 변수에 안전하게 저장됩니다
- ✅ CORS 설정으로 허용된 도메인만 API 접근 가능합니다

---

## 🐛 문제 해결

### 백엔드 로그 확인
Render Dashboard → 서비스 선택 → **Logs** 탭

### 프론트엔드 로그 확인
Vercel Dashboard → 프로젝트 선택 → **Deployments** → 배포 선택 → **View Function Logs**

### CORS 오류
- Render 환경 변수의 `ALLOWED_ORIGINS`에 Vercel URL이 포함되어 있는지 확인
- 백엔드 로그에서 CORS 관련 에러 메시지 확인

### 데이터가 로드되지 않음
- 백엔드 URL이 올바른지 확인 (`/health` 엔드포인트 테스트)
- Vercel 환경 변수 `NEXT_PUBLIC_API_URL`이 올바르게 설정되었는지 확인
- 브라우저 개발자 도구(F12)의 Network 탭에서 API 요청 확인

---

## 📚 추가 리소스

- [Render 문서](https://render.com/docs)
- [Vercel 문서](https://vercel.com/docs)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
