import google.generativeai as genai
from typing import List, Dict, Any, Optional
import os
import logging
import requests
from datetime import datetime
from app.core.config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorytellingGenerator:
    """Gemini 1.5 Flash를 사용하여 스토리텔링을 생성하는 클래스"""
    
    def __init__(self):
        """초기화 및 API 키 설정"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        else:
            genai.configure(api_key=self.api_key)
    
    def create_storytelling_prompt(self, questions: List[Dict[str, Any]], 
                                   answers: List[Dict[str, Any]], 
                                   options: Optional[Dict[str, Any]] = None) -> str:
        """프롬프트 생성 메서드"""
        
        # 옵션 처리
        style = options.get("style", "emotional") if options else "emotional"
        length = options.get("length", "medium") if options else "medium"
        
        # 카테고리별 질문 분류
        categorized_qa = {}
        for q in questions:
            category = q.get("category", "general")
            if category not in categorized_qa:
                categorized_qa[category] = []
            
            # 해당 질문에 대한 답변 찾기
            q_id = q.get("id")
            answer_text = "답변 없음"
            for a in answers:
                if a.get("id") == q_id:
                    answer_text = a.get("content", "답변 없음")
                    break
            
            categorized_qa[category].append({
                "question": q.get("content", ""),
                "answer": answer_text,
                "level": q.get("level", 1),
                "theme": q.get("theme", "general")
            })
        
        # 프롬프트 구성
        prompt = f"""# 스토리텔링 생성 요청

## 배경 정보
사진에 담긴 추억과 관련된 질문-답변을 기반으로 감성적인 스토리텔링을 생성해주세요.
이미지와 텍스트를 함께 분석하여 사용자의 기억을 생생하고 의미있게 재구성해 주세요.

## 질문과 답변 정보
다음은 사진과 관련된 질문과 답변입니다:

"""
        
        # 카테고리별 질문-답변 추가
        for category, qa_list in categorized_qa.items():
            prompt += f"\n### {category.upper()} 카테고리\n"
            for qa in qa_list:
                prompt += f"- 질문: {qa['question']}\n"
                prompt += f"  답변: {qa['answer']}\n"
        
        # 스타일 지침 추가
        prompt += f"\n## 스타일 가이드라인\n"
        prompt += f"- 스타일: {style} (감정적이고 개인적인 어조로 작성)\n"
        prompt += f"- 길이: {length} (중간 길이의 이야기로, 약 300-500자)\n"
        
        # 추가 지침
        prompt += """
## 작성 지침
1. 답변에서 언급된 시간, 장소, 감정, 인물을 중심으로 스토리를 구성하세요.
2. 사진에 보이는 요소들을 스토리에 자연스럽게 통합하세요.
3. 사용자의 감정과 기억을 존중하고 긍정적인 메시지를 담아주세요.
4. 1인칭 또는 3인칭 시점을 자유롭게 선택하여 몰입감 있는 스토리를 만들어주세요.
5. 문학적 표현과 생생한 묘사를 통해 감성을 자극하는 스토리를 작성하세요.

## 출력 형식
- 제목은 필요하지 않습니다.
- 마크다운 서식을 사용하지 말고 일반 텍스트로 작성해주세요.
- 단락 구분을 통해 읽기 쉽게 구성해주세요.
"""
        
        return prompt
    
    async def generate_story(self, media_id: int, 
                            questions: List[Dict[str, Any]], 
                            answers: List[Dict[str, Any]], 
                            image_url: Optional[str] = None,
                            options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """스토리 생성 메서드"""
        try:
            logger.info(f"미디어 ID {media_id}에 대한 스토리 생성 시작")
            
            # Gemini 모델 및 구성 설정
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 1,
                    "top_k": 32,
                    "max_output_tokens": 800,
                }
            )
            
            # 프롬프트 생성
            prompt = self.create_storytelling_prompt(questions, answers, options)
            logger.info(f"프롬프트 생성 완료: {len(prompt)} 자")
            
            # 이미지 처리
            content_parts = [prompt]
            
            if image_url:
                logger.info(f"이미지 URL이 제공되었습니다: {image_url}")
                try:
                    # 이미지 데이터 가져오기
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        # 이미지 데이터를 Gemini에 맞는 형식으로 변환
                        image_data = {"mime_type": "image/jpeg", "data": image_response.content}
                        content_parts = [prompt, image_data]
                        logger.info("이미지가 성공적으로 로드되었습니다.")
                    else:
                        logger.warning(f"이미지를 가져올 수 없습니다 (상태 코드: {image_response.status_code})")
                except Exception as e:
                    logger.error(f"이미지 로딩 중 오류 발생: {str(e)}")
            
            # Gemini 모델 호출
            response = model.generate_content(content_parts)
            
            # 응답 처리
            story_content = response.text.strip()
            logger.info(f"스토리 생성 완료: {len(story_content)} 자")
            
            # 응답 구성
            return {
                "status": "success",
                "media_id": media_id,
                "story_content": story_content,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"스토리 생성 중 오류 발생: {str(e)}")
            return {
                "status": "error",
                "media_id": media_id,
                "message": str(e),
                "created_at": datetime.now().isoformat()
            } 