from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
from app.models.question import Question, GeneratedQuestion, AnswerText, GeneratedStory
from app.core.vision import VisionAIClient
from app.core.question_generator import QuestionGenerator
import aiofiles
import os
from app.core.config import settings
import logging
import json
from datetime import datetime
import httpx

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
vision_client = VisionAIClient()
question_generator = QuestionGenerator()

# 디렉토리 생성
os.makedirs(settings.TEMP_UPLOAD_DIR, exist_ok=True)
os.makedirs("analysis_results", exist_ok=True)

async def send_to_backend(data: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
    """데이터를 백엔드 서버로 전송
    
    Args:
        data: 전송할 데이터
        endpoint: 백엔드 엔드포인트
        
    Returns:
        Dict[str, Any]: 백엔드 응답
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.BACKEND_SERVER_HOST}{endpoint}",
                json=data,
                timeout=5.0  # 5초 타임아웃 설정
            )
            response.raise_for_status()
            logger.info(f"데이터가 백엔드로 전송되었습니다: {endpoint}")
            return response.json()
    except Exception as e:
        logger.warning(f"백엔드 서버 연결 실패 (정상적인 테스트 환경): {str(e)}")
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
async def test_questions() -> GeneratedQuestion:
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
    
    # 응답 생성
    questions_response = GeneratedQuestion(
        questions=[
            Question(
                category=q["category"],
                level=q["level"],
                question=q["question"]
            ) for q in generated_questions
        ],
        analysis_result=analysis_result
    )
    
    # 백엔드로 전송될 데이터를 로깅
    logger.info("백엔드로 전송될 데이터:")
    logger.info(json.dumps(questions_response.dict(), indent=2, ensure_ascii=False))
    
    return questions_response

@router.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)) -> Dict[str, Any]:
    """이미지를 분석하여 관련 질문을 생성하고 백엔드로 전송합니다."""
    try:
        # 파일 크기 검증
        content = await image.read()
        if len(content) > settings.max_image_size_int:
            raise HTTPException(
                status_code=400,
                detail=f"이미지 크기가 너무 큽니다. 최대 허용 크기: {settings.max_image_size_int/1024/1024}MB"
            )
            
        # 이미지 분석
        analysis_result = await vision_client.analyze_image(content)
        logger.info(f"이미지 분석 완료: {image.filename}")
        
        # 분석 결과를 기반으로 질문 생성
        generated_questions = question_generator.generate_questions(analysis_result)
        
        # 생성된 질문 객체 생성
        questions_response = GeneratedQuestion(
            questions=[
                Question(
                    category=q["category"],
                    level=q["level"],
                    question=q["question"]
                ) for q in generated_questions
            ],
            analysis_result=analysis_result
        )
        
        # 분석 결과를 JSON 파일로 저장
        result_file = await save_analysis_result(
            questions_response.dict(),
            f"analysis_{image.filename.split('.')[0]}"
        )
        
        # 백엔드로 전송
        backend_response = await send_to_backend(
            questions_response.dict(),
            "/api/v1/questions/create"
        )
        
        return {
            "status": "success",
            "message": "이미지 분석 및 질문 생성이 완료되었습니다.",
            "data": questions_response.dict(),
            "saved_file": result_file,
            "backend_status": backend_response
        }
            
    except Exception as e:
        logger.error(f"이미지 분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await image.close()

@router.post("/test-answer")
async def test_answer(answer: AnswerText) -> Dict[str, Any]:
    """테스트용 답변 처리 및 백엔드 전송"""
    try:
        # 답변 데이터를 JSON 파일로 저장
        result_file = await save_analysis_result(
            answer.dict(),
            f"answer_{answer.question_id}"
        )
        
        # 백엔드로 전송
        backend_response = await send_to_backend(
            answer.dict(),
            "/api/v1/answers/create"
        )
        
        return {
            "status": "success",
            "message": "답변이 성공적으로 처리되었습니다.",
            "data": answer.dict(),
            "saved_file": result_file,
            "backend_status": backend_response
        }
    except Exception as e:
        logger.error(f"답변 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
   