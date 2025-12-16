# Pokemon GO Tracker - 배포 가이드

## 현재 상황

현재 **백엔드만** Render에 배포되어 있습니다:
- 백엔드 API: https://pokemon-go-tracker.onrender.com/

프론트엔드 Next.js 애플리케이션은 아직 배포되지 않았습니다.

## 프론트엔드 배포하기 (Vercel 권장)

### 1단계: Vercel 계정 생성 및 준비

1. [Vercel](https://vercel.com) 접속
2. GitHub 계정으로 로그인
3. "Add New Project" 클릭

### 2단계: GitHub 저장소 연결

1. Vercel에서 `pokemon-go-tracker` 저장소 선택
2. "Import" 클릭

### 3단계: 프로젝트 설정

**Framework Preset**: Next.js (자동 감지됨)

**Root Directory**: `frontend`
- "Edit" 버튼 클릭
- `frontend` 입력

**Build Settings**:
- Build Command: `npm run build` (자동 설정됨)
- Output Directory: `.next` (자동 설정됨)
- Install Command: `npm install` (자동 설정됨)

**Environment Variables**:
다음 환경 변수를 추가하세요:

```
NEXT_PUBLIC_API_URL=https://pokemon-go-tracker.onrender.com
```

### 4단계: 배포

1. "Deploy" 버튼 클릭
2. 3-5분 대기 (빌드 및 배포 진행)
3. 배포 완료 후 Vercel URL 확인 (예: `https://pokemon-go-tracker.vercel.app`)

### 5단계: 커스텀 도메인 (선택사항)

Vercel 대시보드에서:
1. Settings → Domains
2. 원하는 도메인 추가
3. DNS 설정 (Vercel 가이드 참조)

## 배포 후 확인사항

프론트엔드가 정상적으로 배포되면:

✅ **홈페이지**: 포켓몬 GO 뉴스 목록이 보여야 함
✅ **IV 계산기**: 스크린샷 업로드 및 분석 가능
✅ **도감**: 포켓몬 검색 및 정보 확인 가능
✅ **배틀 영상**: YouTube 영상 목록이 보여야 함

## 자동 배포 설정

Vercel은 GitHub와 자동 연동됩니다:
- `main` 브랜치에 푸시 → 자동 배포
- Pull Request 생성 → 프리뷰 배포 생성

## 트러블슈팅

### 빌드 에러 발생 시

1. Vercel 대시보드 → Deployments → 실패한 배포 클릭
2. Build Logs 확인
3. 에러 메시지 복사하여 해결

### API 연결 안 될 때

1. Environment Variables에 `NEXT_PUBLIC_API_URL`이 올바르게 설정되었는지 확인
2. Vercel 대시보드 → Settings → Environment Variables
3. 변경 후 "Redeploy" 필요

### CORS 에러 발생 시

백엔드 CORS 설정에 Vercel URL 추가 필요:
- `backend/app/main.py`의 `allow_origins` 리스트에 Vercel URL 추가

## 대안: Render에 프론트엔드도 배포

Vercel 대신 Render에도 배포 가능:

1. Render 대시보드 → "New Web Service"
2. GitHub 저장소 연결
3. 설정:
   - Name: `pokemon-go-tracker-frontend`
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`
   - Environment Variables:
     ```
     NEXT_PUBLIC_API_URL=https://pokemon-go-tracker.onrender.com
     ```

**단점**: Render는 Next.js 최적화가 Vercel보다 부족하며, 무료 플랜은 속도가 느립니다.

## 비용

- **Vercel**: 무료 플랜으로 충분 (개인 프로젝트)
- **Render**: 백엔드 무료 플랜 사용 중

## 요약

현재 https://pokemon-go-tracker.onrender.com/ 에서 JSON이 보이는 이유:
→ **백엔드 API만 배포되어 있기 때문**

해결 방법:
→ **위 가이드대로 Vercel에 프론트엔드 배포**

배포 후:
- 프론트엔드: `https://pokemon-go-tracker.vercel.app` (예시)
- 백엔드: `https://pokemon-go-tracker.onrender.com`
