# Memory AI Service

Memory Album AI Analysis Service - 사진 분석을 통한 스토리텔링 생성 서비스

## 프로젝트 개요

이 프로젝트는 사용자의 사진을 분석하여 관련 질문을 생성하고, 사용자의 답변을 바탕으로 개인화된 스토리텔링을 생성하는 AI 서비스입니다.

## 기술 스택

- Python 3.12
- FastAPI
- Google Cloud Vision API
- Google Cloud Translation API
- Pydantic
- aiofiles
- python-multipart
- uvicorn

## 프로젝트 구조

```
project/
├── app/
│   ├── api/           # API 라우터
│   │   └── v1/        # API v1 엔드포인트
│   ├── core/          # 설정, 상수 등
│   ├── schemas/       # Pydantic 모델
│   ├── services/      # 비즈니스 로직 서비스
│   └── main.py        # FastAPI 애플리케이션 진입점
├── tests/             # 테스트 코드
├── credentials/       # API 키 및 인증 파일 (gitignore)
├── temp_uploads/      # 임시 업로드 파일 저장소 (gitignore)
├── DEVELOPMENT_RULES.md  # 개발 규칙
├── QUESTION_RULES.md     # 질문 생성 규칙
├── TASK_LIST.md         # 작업 현황
├── requirements.txt     # 의존성 목록
└── .env                # 환경 변수 (gitignore)
```

## API 엔드포인트

### 기본 엔드포인트
- `GET /` - 서비스 상태 확인
- `GET /health` - 헬스 체크

### API v1 엔드포인트
- `GET /api/v1/test-connection` - 백엔드 서버 연결 테스트
- `POST /api/v1/analyze-image` - 이미지 분석 및 질문 생성
- `POST /api/v1/process-answer` - 답변 처리 및 스토리 생성
- `POST /api/v1/generate-story` - 최종 스토리 생성

## 설치 및 실행

1. 저장소 클론
```bash
git clone [repository-url]
cd memory-AI
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 필수 파일 설정

프로젝트 실행을 위해 다음 파일들을 추가해야 합니다:

### a) `.env` 파일 생성
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가:
```
# Google Cloud Vision API 설정
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=credentials/vision-api-key.json

# Google Cloud Translation API 설정
GOOGLE_CLOUD_LOCATION=global

# 이미지 처리 설정
TEMP_UPLOAD_DIR=temp_uploads
MAX_IMAGE_SIZE=10485760
```

### b) Google Cloud 인증 파일 설정
1. Google Cloud Console에서 서비스 계정 키(JSON) 다운로드
2. 프로젝트 루트에 `credentials` 디렉토리 생성
3. 다운로드한 JSON 파일을 `credentials/vision-api-key.json`로 저장

### c) API 활성화
Google Cloud Console에서 다음 API들을 활성화해야 합니다:
- Vision API
- Cloud Translation API

### d) 임시 디렉토리 생성
```bash
mkdir temp_uploads
```

5. 서버 실행
```bash
uvicorn app.main:app --reload
```

## 실행 가이드라인

### 전체 실행 과정 요약

1. 개발 환경 준비 (Python 3.12 설치)
2. 코드 다운로드 및 가상환경 설정
3. 필요한 API 키 및 환경설정
4. 서버 실행 및 테스트

### 자세한 실행 단계

#### 1. 개발 환경 준비
- Python 3.12 설치: [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드
- pip 최신 버전 확인: `python -m pip install --upgrade pip`

#### 2. 프로젝트 설정

```bash
# 코드 클론
git clone [repository-url]
cd memory-AI

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

#### 3. Google Cloud 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 로그인
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. 필요한 API 활성화:
   - Vision API
   - Cloud Translation API
4. 서비스 계정 생성:
   - IAM & Admin > 서비스 계정으로 이동
   - 서비스 계정 생성
   - 필요한 권한 부여 (Vision API 사용자, Translation API 사용자)
   - 키 생성 (JSON 형식)
5. 다운로드한 JSON 키 파일을 `credentials/vision-api-key.json`에 저장

#### 4. 환경 설정

1. 프로젝트 루트 디렉토리에 `.env` 파일 생성:
```
# Google Cloud Vision API 설정
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=credentials/vision-api-key.json

# Google Cloud Translation API 설정
GOOGLE_CLOUD_LOCATION=global

# 이미지 처리 설정
TEMP_UPLOAD_DIR=temp_uploads
MAX_IMAGE_SIZE=10485760
```

2. 임시 디렉토리 생성:
```bash
mkdir -p temp_uploads
```

#### 5. 서버 실행

```bash
# 개발 모드 실행 (자동 재시작)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 6. 서버 테스트

1. 서버가 실행되면 브라우저에서 다음 URL 접속:
   - 기본 상태 확인: `http://localhost:8000/`
   - 헬스 체크: `http://localhost:8000/health`
   - API 문서 확인: `http://localhost:8000/docs`

2. API 테스트:
   - Swagger UI (`http://localhost:8000/docs`)를 통해 API 엔드포인트 테스트
   - 또는 curl, Postman 등을 이용한 API 요청 테스트

### 문제 해결

#### 일반적인 오류
- **ModuleNotFoundError**: `pip install -r requirements.txt`를 다시 실행
- **Permission Denied**: 인증 파일 경로와 권한 확인
- **API Quota 초과**: Google Cloud Console에서 할당량 확인 및 증가 요청

#### Google Cloud 인증 오류
- 환경 변수 `GOOGLE_APPLICATION_CREDENTIALS`가 올바르게 설정되었는지 확인
- JSON 키 파일이 올바른 위치에 있는지 확인
- 서비스 계정에 필요한 권한이 부여되었는지 확인

#### 서버 시작 오류
- 포트 충돌: 사용 중인 포트를 변경 (`--port` 옵션 이용)
- 의존성 문제: 가상환경이 활성화되었는지 확인하고 의존성 재설치

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 개발 규칙

자세한 개발 규칙은 [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md)를 참조하세요.

## 작업 현황

현재 작업 현황은 [TASK_LIST.md](TASK_LIST.md)에서 확인할 수 있습니다.

## 주의사항

- `.env` 파일과 `credentials` 디렉토리의 내용은 절대 Git에 커밋하지 마세요.
- 이미지 업로드 시 최대 크기는 10MB입니다.
- API 키와 인증 정보는 안전하게 관리해야 합니다.
