from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AnswerText(BaseModel):
    """사용자가 입력한 답변 텍스트"""
    question_id: int
    answer: str

class Question(BaseModel):
    """생성된 질문"""
    category: str
    level: int
    question: str

class GeneratedQuestion(BaseModel):
    """AI가 생성한 질문 목록"""
    questions: List[Question]
    image_path: str
    analysis_result: Dict[str, Any]

class GeneratedStory(BaseModel):
    """AI가 생성한 스토리텔링"""
    story: str
    sentiment_score: float 