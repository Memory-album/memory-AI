# Python 개발 규칙 (Python Development Rules)

## 1. Python 코딩 스타일
- **PEP 8 준수**
  - 들여쓰기: 4칸 스페이스 사용
  - 최대 줄 길이: 79자
  - 함수/클래스 간 구분: 2줄 띄우기
  - 클래스 내 메서드 간 구분: 1줄 띄우기

- **네이밍 컨벤션**
  - 패키지/모듈: lowercase (예: `user_auth`)
  - 클래스: CapWords (예: `UserAuth`)
  - 함수/변수: lowercase_with_underscores (예: `get_user_info`)
  - 상수: UPPERCASE_WITH_UNDERSCORES (예: `MAX_CONNECTIONS`)

- **문서화**
  - 모든 함수/클래스에 Docstring 작성
  - Type Hints 사용 (Python 3.6+)
  ```python
  def get_user(user_id: int) -> dict:
      """사용자 정보를 조회합니다.
      
      Args:
          user_id (int): 사용자 ID
      
      Returns:
          dict: 사용자 정보
      """
  ```

## 2. FastAPI 개발 원칙
- **라우터 구조화**
  - 기능별 라우터 분리
  - 공통 prefix 사용
  - 태그를 통한 API 그룹화

- **Pydantic 모델 활용**
  - 요청/응답 모델 정의
  - 데이터 검증 규칙 설정
  - 모델 상속을 통한 재사용

- **의존성 주입 활용**
  - DB 세션 관리
  - 인증/인가 처리
  - 공통 기능 분리

## 3. 테스트
- **pytest 프레임워크 사용**
  - 테스트 파일명: `test_*.py`
  - 테스트 함수명: `test_*`
  - fixture 적극 활용

- **테스트 범위**
  - 단위 테스트: 개별 함수/클래스
  - 통합 테스트: API 엔드포인트
  - E2E 테스트: 전체 플로우

## 4. 프로젝트 구조
```
project/
├── app/
│   ├── api/           # API 라우터
│   ├── core/          # 설정, 상수 등
│   ├── crud/          # DB 조작 함수
│   ├── db/            # DB 설정
│   ├── models/        # DB 모델
│   └── schemas/       # Pydantic 모델
├── tests/             # 테스트 코드
├── alembic/           # DB 마이그레이션
└── requirements.txt   # 의존성 목록
```

## 5. 깃 커밋 규칙
커밋 메시지는 다음 형식을 따름:
```
<type>: <description>

[optional body]

[optional footer]
```

- **Type**
  - feat: 새로운 기능
  - fix: 버그 수정
  - docs: 문서 수정
  - style: 코드 포맷팅
  - refactor: 코드 리팩토링
  - test: 테스트 코드
  - chore: 빌드, 패키지 관련 수정

## 6. 보안 규칙
- 환경 변수 사용 (.env)
- SQL Injection 방지
- XSS 방지
- CORS 설정
- 적절한 권한 관리 