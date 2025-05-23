# Memory AI 프로젝트 작업 내역

## 진행 중인 작업
### 2025-03-03
- [x] Vision API 통합 (1단계)
  - [x] Google Cloud Vision API 키 설정
  - [x] Vision API 클라이언트 구현
  - [x] 이미지 분석 결과 처리 로직 구현
  - [x] 에러 처리 및 로깅 구현

- [x] 질문 생성 로직 구현 (2단계)
  - [x] 이미지 분석 결과 기반 질문 템플릿 설계
  - [x] 카테고리별 질문 생성 로직 구현
  - [x] 질문 우선순위 및 필터링 로직 구현

- [x] Translation API 통합
  - [x] Google Cloud Translation API 키 설정
  - [x] Translation API 클라이언트 구현
  - [x] 영어-한국어 번역 로직 구현
  - [x] 에러 처리 및 로깅 구현
  - [ ] 번역 품질 개선 및 최적화

- [ ] 스토리 생성 로직 구현 (3단계)
  - [ ] 답변 데이터 구조화 및 전처리
  - [ ] 스토리 템플릿 설계
  - [ ] 컨텍스트 기반 스토리 생성 로직 구현
  - [ ] 스토리 품질 향상을 위한 후처리 로직 구현

- [x] 백엔드 서버 연동 구현
  - [x] 이미지 분석 결과 전송 구현
  - [x] 질문 데이터 전송 구현
  - [x] 답변 데이터 전송 구현
  - [x] 에러 처리 및 테스트 환경 구성
  - [ ] 실제 백엔드 서버 연동 테스트

## 완료된 작업
### 2025-03-03
- [x] 프로젝트 초기 설정
  - [x] 가상환경 설정
  - [x] FastAPI 설치 및 기본 설정
  - [x] 개발 규칙 문서 작성
  - [x] 작업 내역 문서 작성

- [x] API 기본 구조 구현
  - [x] CORS 설정 (localhost:8080 연동)
  - [x] 기본 라우터 구조 설정
  - [x] 데이터 모델(스키마) 정의
  - [x] 테스트용 엔드포인트 구현
    - [x] 이미지 분석 엔드포인트 (/analyze-image)
    - [x] 답변 처리 엔드포인트 (/process-answer)
    - [x] 스토리 생성 엔드포인트 (/generate-story)

## 예정된 작업
- [ ] AI 모델 통합
  - [ ] Vision API 연동
  - [ ] 질문 생성 모델 구현
  - [ ] 스토리 생성 모델 구현

- [ ] 테스트 구현
  - [ ] 단위 테스트 작성
  - [ ] 통합 테스트 작성
  - [ ] 엔드포인트 테스트 작성

## 대기 중인 정보
- Vision API 사용량 및 비용 정책
- 백엔드 서버 API 스펙