# Gmail SMTP 설정 가이드

## Gmail 앱 비밀번호 생성 방법

Gmail SMTP를 사용하여 이메일을 발송하려면 **앱 비밀번호**가 필요합니다.

### 1단계: Google 2단계 인증 활성화

1. [Google 계정 설정](https://myaccount.google.com/)으로 이동
2. 왼쪽 메뉴에서 **보안** 선택
3. **2단계 인증** 항목 찾기
4. 아직 활성화하지 않았다면 **2단계 인증 사용** 클릭
5. 안내에 따라 2단계 인증 설정 완료

### 2단계: 앱 비밀번호 생성

1. [Google 계정 설정](https://myaccount.google.com/) > **보안**으로 이동
2. **2단계 인증** 섹션에서 **앱 비밀번호** 클릭
3. 앱 선택: **메일** 선택
4. 기기 선택: **기타(맞춤 이름)** 선택 후 "Pokemon GO Tracker" 입력
5. **생성** 클릭
6. 생성된 16자리 앱 비밀번호를 복사 (예: `abcd efgh ijkl mnop`)

### 3단계: 환경 변수 설정

1. 터미널에서 환경 변수 설정:

```bash
# macOS/Linux
export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"

# 또는 .zshrc 또는 .bashrc에 추가하여 영구 설정
echo 'export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"' >> ~/.zshrc
source ~/.zshrc
```

2. 또는 `.env` 파일에서 직접 수정:

```bash
# /Users/mac.yoo/pokemon-go-tracker/backend/.env
SMTP_PASSWORD=abcd efgh ijkl mnop
```

**주의**: 공백은 그대로 포함하거나 제거해도 됩니다.

### 4단계: 테스트

환경 변수 설정 후 테스트 이메일 발송:

```bash
cd /Users/mac.yoo/pokemon-go-tracker/backend
source venv/bin/activate
python test_email.py
```

## 현재 설정 상태

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=treehi1@gmail.com
SMTP_PASSWORD=${GMAIL_APP_PASSWORD}  # <- 여기에 앱 비밀번호 필요
EMAIL_FROM=treehi1@gmail.com
NOTIFICATION_EMAIL=treehi1@gmail.com
```

## 문제 해결

### "Authentication failed" 오류
- 앱 비밀번호가 올바른지 확인
- 2단계 인증이 활성화되어 있는지 확인
- Gmail 계정 비밀번호가 아닌 **앱 비밀번호**를 사용해야 함

### "535-5.7.8 Username and Password not accepted" 오류
- 앱 비밀번호를 다시 생성하여 시도
- SMTP_USER가 올바른 Gmail 주소인지 확인

### 이메일이 도착하지 않는 경우
- 스팸 폴더 확인
- Gmail "보낸 편지함" 확인
- 로그에서 에러 메시지 확인
