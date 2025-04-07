from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class StoryRequest(BaseModel):
    """스토리 생성 요청 모델"""
    media_id: int
    questions: List[Dict[str, Any]]
    answers: List[Dict[str, Any]]
    image_url: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class StoryResponse(BaseModel):
    """스토리 생성 응답 모델"""
    status: str
    media_id: int
    story_content: str
    created_at: datetime = Field(default_factory=datetime.now) 