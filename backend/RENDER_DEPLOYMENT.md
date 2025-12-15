# Render 클라우드 배포 가이드

## 개요

이 문서는 Pokemon GO Tracker 백엔드를 Render 클라우드 서버에 배포하여 **자동 이벤트 크롤링 및 이메일 알림 시스템**을 구축하는 방법을 설명합니다.

## 주요 기능

### 자동화된 이벤트 알림 시스템

- **매일 오전 10시 (Asia/Seoul)** 자동 실행
- 포켓몬GO 한국 공식 페이지 크롤링
- 신규 이벤트 감지 시 `treehi1@gmail.com`로 자동 이메일 발송
- **로컬 PC가 꺼져 있어도 Render 서버에서 24/7 동작**

## 배포 준비

### 1. SendGrid API 키 발급

1. [SendGrid](https://sendgrid.com/) 가입
2. Settings > API Keys 메뉴로 이동
3. "Create API Key" 클릭
4. Full Access 권한 부여
5. API 키 복사 (한 번만 표시됩니다!)

### 2. Render 계정 생성

1. [Render](https://render.com/) 가입
2. GitHub 계정 연동

## Render 배포 설정

### Web Service 생성

1. Render 대시보드에서 "New +" > "Web Service" 선택
2. GitHub 저장소 연결: `pokemon-go-tracker`
3. 다음 설정 입력:

#### 기본 설정
- **Name**: `pokemon-go-tracker-backend`
- **Region**: `Singapore` (한국과 가장 가까움)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

#### 환경 변수 (Environment Variables)

다음 환경 변수를 설정하세요:

| 변수명 | 값 | 설명 |
|--------|-----|------|
| `MODE` | `production` | 프로덕션 모드 |
| `SENDGRID_API_KEY` | `SG.xxx...` | SendGrid API 키 (발급받은 키) |
| `EMAIL_FROM` | `noreply@pokemongo-tracker.com` | 발신자 이메일 |
| `TO_EMAIL` | `treehi1@gmail.com` | 수신자 이메일 |
| `DATABASE_URL` | (Render 자동 제공) | PostgreSQL URL |
| `FRONTEND_URL` | `https://pokemon-go-tracker.vercel.app` | 프론트엔드 URL |
| `POKEMONGO_NEWS_URL` | `https://pokemongolive.com/ko/post/` | 크롤링 대상 URL |

### PostgreSQL 데이터베이스 생성

1. Render 대시보드에서 "New +" > "PostgreSQL" 선택
2. 이름: `pokemon-go-tracker-db`
3. Web Service의 환경 변수에서 `DATABASE_URL` 자동 설정됨

## 배포 확인

### 1. 서버 상태 확인

```bash
curl https://pokemon-go-tracker-backend.onrender.com/health
```

응답:
```json
{"status": "healthy"}
```

### 2. 스케줄러 상태 확인

```bash
curl https://pokemon-go-tracker-backend.onrender.com/api/admin/scheduler-status
```

응답 예시:
```json
{
  "status": "success",
  "scheduler": {
    "running": true,
    "timezone": "Asia/Seoul",
    "jobs_count": 2,
    "jobs": [
      {
        "id": "pokemon_go_crawler",
        "name": "Crawl Pokemon GO events (Daily 10:00 Asia/Seoul)",
        "next_run_time": "2025-12-16T10:00:00+09:00",
        "trigger": "cron[hour='10', minute='0']"
      }
    ]
  }
}
```

### 3. 수동 크롤링 테스트

```bash
curl -X POST https://pokemon-go-tracker-backend.onrender.com/api/admin/crawl-now
```

응답 예시:
```json
{
  "status": "success",
  "message": "Crawled 10 events. Found 2 new events.",
  "new_events_count": 2,
  "new_events": [...],
  "email_sent": true
}
```

## 자동 실행 확인

### 로그 확인

Render 대시보드 > Web Service > Logs 에서 다음 로그를 확인할 수 있습니다:

```
🚀 FastAPI application starting...
📅 Initializing scheduler...
✅ SendGrid email service initialized. Target: treehi1@gmail.com
Scheduler started.
  - Pokemon GO news: Daily at 10:00 AM (Asia/Seoul)
✅ Scheduler started successfully
```

### 매일 오전 10시 실행 로그

```
================================================================================
🕐 [SCHEDULER] Scheduled crawl job started at 2025-12-16 10:00:00
================================================================================
📡 Fetching events from Pokemon GO website...
✅ Found 10 total events from website
🆕 New event: 메가 레쿠쟈 레이드 등장!...
📧 1 new events found. Sending email...
📤 Sending email to treehi1@gmail.com with 1 new events...
✅ Email sent successfully to treehi1@gmail.com (Status: 202)
✅ Scheduled crawl completed successfully
================================================================================
```

## 이메일 형식

### 제목
```
[포켓몬고] 오늘 신규 이벤트 알림
```

### 본문 (HTML)
- 신규 이벤트 제목
- 이벤트 요약
- 이벤트 링크
- Pokemon GO Tracker 바로가기 버튼

## API 엔드포인트

### 관리자 API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/api/admin/crawl-now` | 수동 크롤링 + 이메일 발송 |
| `GET` | `/api/admin/scheduler-status` | 스케줄러 상태 확인 |
| `GET` | `/health` | 서버 상태 확인 |

### 일반 API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/api/events` | 이벤트 목록 조회 |
| `GET` | `/api/pokedex` | 포켓몬 도감 조회 |
| `GET` | `/docs` | API 문서 (Swagger UI) |

## 문제 해결

### 이메일이 발송되지 않는 경우

1. **SendGrid API 키 확인**
   ```bash
   curl https://pokemon-go-tracker-backend.onrender.com/api/admin/scheduler-status
   ```

2. **로그 확인**
   - Render 대시보드 > Logs 에서 `SendGrid` 관련 에러 확인
   - `❌ SENDGRID_API_KEY not configured` 메시지가 있으면 환경 변수 확인

3. **수동 테스트**
   ```bash
   curl -X POST https://pokemon-go-tracker-backend.onrender.com/api/admin/crawl-now
   ```

### 스케줄러가 실행되지 않는 경우

1. **스케줄러 상태 확인**
   ```bash
   curl https://pokemon-go-tracker-backend.onrender.com/api/admin/scheduler-status
   ```

2. **서버 재시작**
   - Render 대시보드 > Manual Deploy > "Clear build cache & deploy"

### 크롤링이 실패하는 경우

1. **대상 URL 확인**
   - `POKEMONGO_NEWS_URL` 환경 변수 확인
   - 기본값: `https://pokemongolive.com/ko/post/`

2. **로그 확인**
   - `❌ ERROR in scheduled_crawl_job` 메시지 확인

## 비용

### Render 무료 플랜
- Web Service: 750시간/월 무료
- PostgreSQL: 90일 무료 (이후 $7/월)
- **충분히 테스트 및 운영 가능**

### SendGrid 무료 플랜
- 100 이메일/일 무료
- **일일 1회 발송이므로 충분**

## 보안 주의사항

1. **API 키 노출 금지**
   - `.env` 파일은 절대 GitHub에 올리지 마세요
   - Render 환경 변수로만 관리

2. **이메일 수신자 변경**
   - `TO_EMAIL` 환경 변수 변경
   - 또는 코드에서 `treehi1@gmail.com` 검색 후 수정

## 결론

이제 Render 클라우드 서버에서 **24시간 자동으로** 포켓몬GO 이벤트를 크롤링하고, 신규 이벤트가 있을 때 이메일로 알림을 받을 수 있습니다!

**로컬 PC를 켜놓을 필요가 없으며**, Render 서버가 살아있는 한 매일 오전 10시에 자동으로 실행됩니다.
