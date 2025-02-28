# Memory AI Service

Memory Album AI Analysis Service - 사진 분석을 통한 스토리텔링 생성 서비스

## 프로젝트 개요

이 프로젝트는 사용자의 사진을 분석하여 관련 질문을 생성하고, 사용자의 답변을 바탕으로 개인화된 스토리텔링을 생성하는 AI 서비스입니다.

## 기술 스택

- Python 3.12
- FastAPI
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
│   └── schemas/       # Pydantic 모델
├── tests/             # 테스트 코드
└── requirements.txt   # 의존성 목록
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

1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 서버 실행
```bash
uvicorn app.main:app --reload --host=0.0.0.0 --port=8000
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 개발 규칙

자세한 개발 규칙은 [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md)를 참조하세요.

## 작업 현황

현재 작업 현황은 [TASK_LIST.md](TASK_LIST.md)에서 확인할 수 있습니다.
