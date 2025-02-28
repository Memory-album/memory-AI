from pydantic import BaseModel
from typing import List

class AnswerText(BaseModel):
    """사용자가 입력한 답변 텍스트"""
    question_id: int
    answer: str

class GeneratedQuestion(BaseModel):
    """AI가 생성한 질문"""
    question_text: str
    category: str  # 예: "장소", "인물", "감정" 등

class GeneratedStory(BaseModel):
    """AI가 생성한 스토리텔링"""
    story: str
    metadata: dict  # 추가 정보를 위한 필드 