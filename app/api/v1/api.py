from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.schemas.request import AnswerText, GeneratedQuestion, GeneratedStory
import aiofiles
import os
from datetime import datetime

router = APIRouter()

# 임시 저장소 설정
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/test-connection")
async def test_backend_connection():
    """백엔드 서버와의 연결을 테스트합니다."""
    return {"message": "AI 서버가 정상적으로 동작 중입니다."}

@router.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    """이미지를 분석하여 질문들을 생성합니다."""
    try:
        # 이미지 임시 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = os.path.join(UPLOAD_DIR, f"temp_{timestamp}_{image.filename}")
        
        async with aiofiles.open(temp_path, 'wb') as out_file:
            content = await image.read()
            await out_file.write(content)

        # TODO: Vision API 분석 로직 구현
        
        # 테스트용 응답
        questions = [
            GeneratedQuestion(
                question_text="이 사진은 언제 찍은 건가요?",
                category="시간"
            ),
            GeneratedQuestion(
                question_text="사진 속 장소는 어디인가요?",
                category="장소"
            ),
            GeneratedQuestion(
                question_text="이때 기분이 어땠나요?",
                category="감정"
            )
        ]
        
        return {"questions": questions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/process-answer")
async def process_answer(answer: AnswerText):
    """사용자의 답변을 처리하여 스토리를 생성합니다."""
    try:
        # TODO: 답변 처리 및 스토리 생성 로직 구현
        
        # 테스트용 응답
        story = GeneratedStory(
            story=f"당신의 답변 '{answer.answer}'를 바탕으로 생성된 스토리입니다...",
            metadata={
                "sentiment": "positive",
                "keywords": ["추억", "행복", "가족"]
            }
        )
        
        return story
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-story")
async def generate_story(answers: List[AnswerText]):
    """여러 답변들을 종합하여 최종 스토리를 생성합니다."""
    try:
        # TODO: 최종 스토리 생성 로직 구현
        
        # 테스트용 응답
        final_story = GeneratedStory(
            story="모든 답변들을 종합한 최종 스토리입니다...",
            metadata={
                "total_answers": len(answers),
                "theme": "가족여행",
                "keywords": ["여름", "바다", "행복"]
            }
        )
        
        return final_story
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 