from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.schemas.request import AnswerText, GeneratedQuestion, GeneratedStory, Question
from app.core.vision import VisionAIClient
from app.core.question_generator import QuestionGenerator
import aiofiles
import os
from app.core.config import settings
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
vision_client = VisionAIClient()
question_generator = QuestionGenerator()

# 임시 업로드 디렉토리 생성
os.makedirs(settings.TEMP_UPLOAD_DIR, exist_ok=True)

@router.get("/test-connection")
async def test_connection():
    """서버 연결 테스트용 엔드포인트"""
    return {"status": "success", "message": "서버가 정상적으로 동작 중입니다."}

@router.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)) -> GeneratedQuestion:
    """이미지를 분석하여 관련 질문을 생성합니다.
    
    Args:
        image (UploadFile): 분석할 이미지 파일
        
    Returns:
        GeneratedQuestion: 생성된 질문 목록
    """
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
        
        # 임시 저장을 위한 파일 경로
        temp_path = os.path.join(settings.TEMP_UPLOAD_DIR, image.filename)
        
        # 이미지 임시 저장
        async with aiofiles.open(temp_path, 'wb') as out_file:
            await out_file.write(content)
            
        logger.info(f"이미지 분석 완료: {image.filename}")
        
        # 분석 결과를 기반으로 질문 생성
        generated_questions = question_generator.generate_questions(analysis_result)
        
        # 응답 생성
        return GeneratedQuestion(
            questions=[
                Question(
                    category=q["category"],
                    level=q["level"],
                    question=q["question"]
                ) for q in generated_questions
            ],
            image_path=temp_path,
            analysis_result=analysis_result
        )
            
    except Exception as e:
        logger.error(f"이미지 분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await image.close()

@router.post("/process-answer")
async def process_answer(answer: AnswerText) -> GeneratedStory:
    """사용자의 답변을 처리하여 스토리를 생성합니다."""
    # TODO: 답변 처리 및 스토리 생성 로직 구현
    return GeneratedStory(
        story="아직 구현되지 않은 기능입니다.",
        sentiment_score=0.0
    )

@router.post("/generate-story")
async def generate_story(answers: list[AnswerText]) -> GeneratedStory:
    """여러 답변들을 종합하여 최종 스토리를 생성합니다."""
    # TODO: 최종 스토리 생성 로직 구현
    return GeneratedStory(
        story="아직 구현되지 않은 기능입니다.",
        sentiment_score=0.0
    ) 