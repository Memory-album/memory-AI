from typing import Dict, Any
import httpx
import logging
from app.core.config import settings
from app.models.question import GeneratedQuestion

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendService:
    """백엔드 서버와의 통신을 담당하는 서비스 클래스"""
    
    def __init__(self):
        """서비스 초기화"""
        self.base_url = settings.BACKEND_SERVER_HOST
        self.client = httpx.AsyncClient(base_url=self.base_url)
        
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.client.aclose()
        
    async def send_generated_questions(self, questions: GeneratedQuestion) -> Dict[str, Any]:
        """생성된 질문과 분석 결과를 백엔드 서버로 전송
        
        Args:
            questions (GeneratedQuestion): 생성된 질문과 분석 결과
            
        Returns:
            Dict[str, Any]: 백엔드 서버의 응답
        """
        try:
            response = await self.client.post(
                '/api/v1/questions/create',
                json=questions.dict()
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"질문 전송 중 오류 발생: {str(e)}")
            raise
            
    async def send_image_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """이미지 분석 결과만 백엔드 서버로 전송"""
        try:
            # 분석 결과만 JSON 형태로 전송
            response = await self.client.post(
                '/api/v1/images/analyze',
                json=analysis_result
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"이미지 분석 결과 전송 중 오류 발생: {str(e)}")
            raise
            
    async def send_story(self, image_id: str, story: str, sentiment_score: float) -> Dict[str, Any]:
        """생성된 스토리를 백엔드 서버로 전송
        
        Args:
            image_id (str): 이미지 ID
            story (str): 생성된 스토리
            sentiment_score (float): 감정 점수
            
        Returns:
            Dict[str, Any]: 백엔드 서버의 응답
        """
        try:
            data = {
                'image_id': image_id,
                'story': story,
                'sentiment_score': sentiment_score
            }
            
            response = await self.client.post(
                '/api/v1/stories/create',
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"스토리 전송 중 오류 발생: {str(e)}")
            raise