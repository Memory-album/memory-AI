from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any, Optional
from app.models.question import Question, GeneratedQuestion, AnswerText, GeneratedStory
from app.models.story import StoryRequest, StoryResponse
from app.core.vision import VisionAIClient
from app.core.question_generator import QuestionGenerator
from app.core.storytelling import StorytellingGenerator
import aiofiles
import os
from app.core.config import settings
import logging
import json
from datetime import datetime
import httpx
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
vision_client = VisionAIClient()
question_generator = QuestionGenerator()
storytelling_generator = StorytellingGenerator()

# 디렉토리 생성
os.makedirs(settings.TEMP_UPLOAD_DIR, exist_ok=True)
os.makedirs("analysis_results", exist_ok=True)

# 이미지 URL 요청 모델
class ImageUrlRequest(BaseModel):
    image_url: str
    auth_token: Optional[str] = None

async def send_to_backend(data: Dict[str, Any], endpoint: str, auth_token: str = None) -> Dict[str, Any]:
    """데이터를 백엔드 서버로 전송
    
    Args:
        data: 전송할 데이터
        endpoint: 백엔드 엔드포인트
        auth_token: 인증 토큰 (optional)
        
    Returns:
        Dict[str, Any]: 백엔드 응답
    """
    try:
        headers = {"Content-Type": "application/json"}
        
        # 인증 토큰이 제공된 경우 헤더에 추가
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            logger.info("인증 토큰이 요청 헤더에 추가되었습니다.")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.BACKEND_SERVER_HOST}{endpoint}",
                json=data,
                headers=headers,
                timeout=5.0  # 5초 타임아웃 설정
            )
            response.raise_for_status()
            logger.info(f"데이터가 백엔드로 전송되었습니다: {endpoint}")
            return response.json()
    except Exception as e:
        logger.warning(f"백엔드 서버 연결 실패: {str(e)}")
        return {
            'status': 'pending',
            'message': '백엔드 서버가 준비되지 않았습니다. 테스트 환경에서는 무시됩니다.'
        }

async def save_analysis_result(data: Dict[str, Any], prefix: str = "analysis") -> str:
    """분석 결과를 JSON 파일로 저장
    
    Args:
        data: 저장할 데이터
        prefix: 파일명 접두사
        
    Returns:
        str: 저장된 파일 경로
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.json"
    filepath = os.path.join("analysis_results", filename)
    
    async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(data, indent=2, ensure_ascii=False))
    
    logger.info(f"분석 결과가 저장되었습니다: {filepath}")
    return filepath

@router.get("/test-connection")
async def test_connection():
    """서버 연결 테스트용 엔드포인트"""
    return {"status": "success", "message": "서버가 정상적으로 동작 중입니다."}

@router.get("/test-questions")
async def test_questions() -> Dict[str, Any]:
    """테스트용 질문 생성"""
    # 테스트용 분석 결과
    analysis_result = {
        "labels": [
            {"description": "Family", "score": 0.95},
            {"description": "Park", "score": 0.85},
            {"description": "Smile", "score": 0.9}
        ],
        "faces": [
            {"joy_likelihood": "VERY_LIKELY", "confidence": 0.98}
        ]
    }
    
    # 질문 생성
    generated_questions = question_generator.generate_questions(analysis_result)
    
    # Spring 백엔드가 기대하는 응답 구조로 반환
    return {
        "analysis_result": analysis_result,
        "questions": [
            {
                "category": q["category"],
                "level": q["level"],
                "question": q["question"]
            } for q in generated_questions
        ]
    }

@router.post("/analyze-image")
async def analyze_image(
    image: UploadFile = File(...), 
    auth_token: str = None
) -> Dict[str, Any]:
    """이미지를 분석하여 관련 질문을 생성합니다."""
    try:
        # 파일 크기 검증
        content = await image.read()
        if len(content) > settings.max_image_size_int:
            raise HTTPException(
                status_code=400, 
                detail={
                    "error_code": "FILE_TOO_LARGE",
                    "message": f"이미지 크기가 너무 큽니다. 최대 허용 크기: {settings.max_image_size_int/1024/1024}MB"
                }
            )
            
        # 이미지 포맷 검증
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail={
                    "error_code": "INVALID_FILE_TYPE",
                    "message": "지원되지 않는 파일 형식입니다. 이미지 파일만 업로드 가능합니다."
                }
            )
            
        # 이미지 분석
        try:
            analysis_result = await vision_client.analyze_image(content)
            logger.info(f"이미지 분석 완료: {image.filename}")
        except Exception as e:
            logger.error(f"이미지 분석 오류: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail={
                    "error_code": "ANALYSIS_FAILED",
                    "message": "이미지 분석 중 오류가 발생했습니다."
                }
            )
        
        # 분석 결과를 기반으로 질문 생성
        generated_questions = question_generator.generate_questions(analysis_result)
        
        # Spring이 기대하는 응답 구조로 데이터 생성
        response_data = {
            "analysis_result": analysis_result,
            "questions": [
                {
                    "category": q["category"],
                    "level": q["level"],
                    "question": q["question"]
                } for q in generated_questions
            ]
        }
        
        # 분석 결과를 JSON 파일로 저장
        result_file = await save_analysis_result(
            response_data,
            f"analysis_{image.filename.split('.')[0]}"
        )
        
        # 백엔드로 전송 (인증 토큰이 제공된 경우 포함)
        backend_response = await send_to_backend(
            response_data,
            "/api/v1/questions/create",
            auth_token=auth_token
        )
        
        return response_data
            
    except HTTPException as http_exc:
        # 이미 HTTPException인 경우 그대로 전달
        logger.error(f"HTTP 예외 발생: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"이미지 분석 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error_code": "UNKNOWN_ERROR",
                "message": f"이미지 분석 중 오류가 발생했습니다: {str(e)}"
            }
        )
    finally:
        await image.close()

@router.post("/analyze-image-url")
async def analyze_image_from_url(request: ImageUrlRequest) -> Dict[str, Any]:
    """S3 URL로부터 이미지를 분석하고 결과를 반환합니다."""
    try:
        # URL에서 이미지 다운로드
        image_url = request.image_url
        if not image_url:
            raise HTTPException(
                status_code=400, 
                detail={
                    "error_code": "MISSING_IMAGE_URL",
                    "message": "이미지 URL이 제공되지 않았습니다"
                }
            )
            
        logger.info(f"이미지 URL로부터 분석 요청: {image_url}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=10.0)
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=400, 
                        detail={
                            "error_code": "DOWNLOAD_FAILED",
                            "message": f"이미지를 다운로드할 수 없습니다. 상태 코드: {response.status_code}"
                        }
                    )
                
                image_content = response.content
        except Exception as e:
            logger.error(f"이미지 다운로드 오류: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail={
                    "error_code": "DOWNLOAD_FAILED",
                    "message": f"이미지를 다운로드할 수 없습니다: {str(e)}"
                }
            )
            
        # 이미지 분석
        try:
            analysis_result = await vision_client.analyze_image(image_content)
            logger.info("이미지 URL 분석 완료")
        except Exception as e:
            logger.error(f"이미지 URL 분석 오류: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail={
                    "error_code": "ANALYSIS_FAILED",
                    "message": "이미지 분석 중 오류가 발생했습니다."
                }
            )
        
        # 분석 결과를 기반으로 질문 생성
        generated_questions = question_generator.generate_questions(analysis_result)
        
        # Spring이 기대하는 응답 구조로 데이터 생성
        response_data = {
            "analysis_result": analysis_result,
            "questions": [
                {
                    "category": q["category"],
                    "level": q["level"],
                    "question": q["question"]
                } for q in generated_questions
            ]
        }
        
        # 분석 결과를 JSON 파일로 저장
        filename = image_url.split('/')[-1].split('?')[0]  # URL에서 파일명 추출
        result_file = await save_analysis_result(
            response_data,
            f"analysis_url_{filename}"
        )
        
        # 백엔드로 전송 (인증 토큰이 있으면 함께 전송)
        backend_response = await send_to_backend(
            response_data,
            "/api/v1/questions/create",
            auth_token=request.auth_token
        )
        
        return response_data
            
    except HTTPException as http_exc:
        # 이미 HTTPException인 경우 그대로 전달
        logger.error(f"HTTP 예외 발생: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"이미지 URL 분석 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error_code": "UNKNOWN_ERROR",
                "message": f"이미지 URL 분석 중 오류가 발생했습니다: {str(e)}"
            }
        )

@router.post("/test-answer")
async def test_answer(answer: AnswerText) -> Dict[str, Any]:
    """테스트용 답변 처리"""
    try:
        return {
            "status": "success",
            "message": "답변이 저장되었습니다.",
            "data": {
                "answer_id": 123,
                "question_id": answer.question_id,
                "text": answer.text
            }
        }
    except Exception as e:
        logger.error(f"답변 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health-check")
async def health_check() -> Dict[str, Any]:
    """서버 상태 확인용 엔드포인트"""
    return {
        "status": "healthy",
        "api_version": "1.0",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/spring-connection-test")
async def spring_connection_test(auth_token: str = None) -> Dict[str, Any]:
    """Spring 백엔드 연결 테스트용 엔드포인트
    
    Args:
        auth_token: JWT 인증 토큰 (쿼리 파라미터)
    """
    try:
        # 백엔드 연결 테스트
        backend_response = await send_to_backend(
            {"message": "테스트 요청"},
            "/api/v1/test/connection",
            auth_token=auth_token
        )
        
        return {
            "status": "success",
            "message": "Spring 백엔드 연결 테스트 성공",
            "backend_response": backend_response,
            "auth_token_provided": auth_token is not None
        }
    except Exception as e:
        logger.error(f"Spring 백엔드 연결 테스트 실패: {str(e)}")
        return {
            "status": "error",
            "message": f"Spring 백엔드 연결 테스트 실패: {str(e)}",
            "error_details": str(e),
            "auth_token_provided": auth_token is not None
        }

@router.post("/generate-story")
async def generate_story(request: StoryRequest) -> Dict[str, Any]:
    """질문과 답변을 기반으로 스토리텔링을 생성합니다."""
    try:
        logger.info(f"스토리 생성 요청 수신: media_id={request.media_id}")
        
        # 스토리텔링 생성 - API 키 인자 제거
        response = await storytelling_generator.generate_story(
            request.media_id,
            request.questions,
            request.answers,
            request.image_url,
            request.options
        )
        
        # 응답 로깅 및 저장
        logger.info(f"스토리 생성 완료: media_id={request.media_id}")
        if response["status"] == "success":
            result_file = await save_analysis_result(
                response,
                f"story_{request.media_id}"
            )
            logger.info(f"스토리 결과 저장 완료: {result_file}")
            
        # Spring 백엔드로 결과 전송 (선택적)
        try:
            backend_response = await send_to_backend(
                response,
                "/api/v1/stories/save",
                None  # 인증 토큰은 선택적
            )
            logger.info("스토리 결과가 백엔드로 전송되었습니다.")
        except Exception as e:
            logger.warning(f"백엔드 전송 실패 (무시): {str(e)}")
        
        return response
        
    except Exception as e:
        logger.error(f"스토리 생성 중 오류 발생: {str(e)}")
        return {
            "status": "error",
            "media_id": request.media_id,
            "message": str(e),
            "created_at": datetime.now().isoformat()
        }
   