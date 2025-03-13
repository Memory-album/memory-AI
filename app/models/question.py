from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union
from enum import Enum

class QuestionLevel(str, Enum):
    """질문 난이도"""
    BASIC = "basic"       # 기본 인식/회상
    CONTEXT = "context"   # 맥락/감정
    REFLECTIVE = "reflective"  # 반성적/통합적

class QuestionCategory(str, Enum):
    """질문 카테고리"""
    TEMPORAL = "temporal"       # 시간-순차적
    SENSORY = "sensory"        # 감각-경험적
    RELATIONAL = "relational"  # 관계-사회적
    IDENTITY = "identity"      # 정체성-내러티브

class Question(BaseModel):
    """질문 모델"""
    category: str
    level: int
    question: str

class GeneratedQuestion(BaseModel):
    """생성된 질문 목록과 분석 결과"""
    questions: List[Question]
    analysis_result: Dict[str, Any]

class AnswerText(BaseModel):
    """답변 모델"""
    question_id: int
    text: str

class GeneratedStory(BaseModel):
    """생성된 스토리 모델"""
    story: str
    sentiment_score: float 