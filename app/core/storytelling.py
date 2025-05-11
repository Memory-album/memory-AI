import google.generativeai as genai
from typing import List, Dict, Any, Optional
import os
import logging
import requests
from datetime import datetime
from app.core.config import settings
from PIL import Image
import io
import traceback

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorytellingGenerator:
    
    def __init__(self):
        """초기화 및 API 키 설정"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            self.api_key = settings.GOOGLE_API_KEY
            logger.info("API 키를 settings에서 로드했습니다.")
        else:
            logger.info("API 키를 환경 변수에서 로드했습니다.")
            
        # API 키 유효성 확인
        if not self.api_key:
            logger.error("GOOGLE_API_KEY 설정이 없습니다.")
        else:
            # API 키를 마스킹하여 로깅 (보안)
            masked_key = self.api_key[:6] + "..." + self.api_key[-4:] if len(self.api_key) > 8 else "***"
            logger.info(f"API 키 확인: {masked_key}")
    
    def create_storytelling_prompt(self, questions: List[Dict[str, Any]], 
                                   answers: List[Dict[str, Any]], 
                                   options: Optional[Dict[str, Any]] = None) -> str:
        """프롬프트 생성 메서드 """

        style = options.get("style", "warmly reflective") if options else "warmly reflective"
        length = options.get("length", "medium") if options else "medium"
        length_desc = {
            "short": "약 150-250자",
            "medium": "약 300-500자",
            "long": "약 500-700자"
        }.get(length, "약 300-500자")

        categorized_qa = {}
        for q in questions:
            category = q.get("category", "general")
            if category not in categorized_qa:
                categorized_qa[category] = []
            
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
        
        prompt = f"""# 스토리텔링 생성 요청: 사진 속 기억에 생명 불어넣기

## **Core Task:**
주어진 사진 이미지와 사용자의 질문-답변 내용을 깊이 분석하여, 단순한 정보 나열이 아닌 **사용자의 소중한 추억을 따뜻하고 의미 있게 재구성하는 감성 스토리텔링**을 생성합니다. 목표는 사용자가 그 순간의 감정과 의미를 다시 느낄 수 있도록 돕는 것입니다.

## **Input Analysis Guidance:**

1.  **Image First Analysis:**
    *   사진의 전체적인 분위기(예: 행복, 평온, 활기참, 그리움)를 파악하세요.
    *   주요 인물의 표정, 시선, 자세를 관찰하고 감정을 추론하세요.
    *   배경(장소, 시간대, 계절)과 주요 사물(특별한 의미가 있을 수 있는 것)을 주의 깊게 보세요.
    *   이 시각적 정보들을 스토리의 뼈대로 활용하세요.

2.  **Q&A Deep Dive:**
    *   각 답변에서 사용자가 강조하는 **핵심 감정, 인물, 장소, 사건**을 파악하세요.
    *   답변들 사이의 연관성을 찾아 **숨겨진 이야기나 주제**(예: 가족애, 우정, 성장의 순간, 소소한 행복)를 발견하세요.
    *   질문의 'theme'이나 'category'를 참고하여 답변의 맥락을 더 깊이 이해하세요.
    *   답변이 짧거나 추상적이더라도, 이미지 정보와 결합하여 구체적인 장면이나 감정으로 확장해 보세요.

## **Narrative Crafting Instructions:**

1.  **Find the Emotional Core:** 스토리의 중심이 될 **가장 중요한 감정이나 의미**를 결정하세요. (예: '그날의 햇살만큼 따스했던 할머니의 미소', '서툴지만 함께여서 즐거웠던 첫 캠핑의 설렘')
2.  **Weave Image and Text Seamlessly:** 사진 속 시각적 요소(색감, 빛, 사물, 인물의 모습 등)를 묘사하며, 이를 사용자의 답변 내용과 자연스럽게 연결하세요. 단순히 '사진에는 A가 있다'가 아니라, '사진 속 당신의 미소는 [답변 내용]을 떠올리게 합니다' 와 같이 통합적으로 서술하세요.
3.  **Show, Don't Just Tell:** '행복했다'고 말하기보다, 웃음소리, 따뜻한 눈빛, 편안한 분위기 등을 묘사하여 행복을 **보여주세요.**
4.  **Sensory Richness:** 시각 정보 외에도, 그 순간에 있었을 법한 소리, 냄새, 촉감, 분위기 등을 상상하여 생생함을 더하세요. (예: '왁자지껄한 웃음소리가 들리는 듯하다', '짭짤한 바다 내음이 느껴지는 것 같다')
5.  **Meaningful Reflection:** 스토리 끝에는 그 기억이 사용자에게 어떤 의미를 지니는지, 혹은 그날의 감정이 현재까지 어떻게 이어지는지에 대한 짧고 따뜻한 성찰이나 여운을 남겨주세요.
6.  **Perspective & Tone:**
    *   **스타일:** `{style}` (예: 따뜻하고 회상적인, 공감적이고 다정한, 약간은 아련한). 사용자의 감정을 존중하며 긍정적이고 부드러운 어조를 유지하세요.
    *   **시점:** 1인칭('나' 또는 '우리') 또는 사용자에게 말을 거는 듯한 2인칭('당신은', '기억하나요?')이나 따뜻한 3인칭 서술자 시점을 유연하게 사용하되, **일관성**을 유지하세요. 사용자의 답변 뉘앙스에 가장 잘 어울리는 시점을 선택하세요.

## **Output Specifications:**

*   **길이:** `{length_desc}` 로 작성해주세요.
*   **형식:** 제목 없이, 마크다운 서식(예: `#`, `*`)을 사용하지 않은 **일반 텍스트**로만 작성해주세요.
*   **가독성:** 자연스러운 단락 구분을 사용하여 읽기 편하게 구성해주세요.
*   **내용:** 긍정적이고 감동을 줄 수 있는 내용에 초점을 맞추세요.

## **질문과 답변 정보:**
다음은 분석에 사용할 질문과 답변입니다:

"""
        
        for category, qa_list in categorized_qa.items():
            prompt += f"\n### {category.upper()} 카테고리\n"
            for qa in qa_list:
                prompt += f"- 질문 ({qa['theme'] if qa.get('theme') else 'general'} / Level {qa['level']}): {qa['question']}\n"
                prompt += f"  답변: {qa['answer']}\n"
        
        prompt += "\n---\n**이제 위의 가이드라인에 따라, 이미지와 Q&A를 종합하여 감동적인 스토리텔링을 작성해주세요.**"
        
        return prompt
    
    async def generate_story(self, media_id: int, 
                            questions: List[Dict[str, Any]], 
                            answers: List[Dict[str, Any]], 
                            image_url: Optional[str] = None,
                            options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """스토리 생성 메서드"""
        try:
            logger.info(f"미디어 ID {media_id}에 대한 스토리 생성 시작")
            
            # API 키 설정
            api_key = self.api_key
            
            if not api_key:
                logger.error("API 키가 설정되지 않았습니다")
                raise Exception("API 키가 설정되지 않았습니다")
            
            # 프롬프트 생성
            prompt = self.create_storytelling_prompt(questions, answers, options)
            logger.info(f"프롬프트 생성 완료: {len(prompt)} 자")
            
            # 가장 기본적인 방식으로 Gemini API 설정
            try:
                # SDK 구성 
                genai.configure(api_key=api_key)
                logger.info("Gemini API 구성 완료")
                
                # 최대한 단순화된 방식으로 호출
                if image_url:
                    try:
                        # 이미지 데이터 가져오기
                        logger.info(f"이미지 URL이 제공되었습니다: {image_url}")
                        image_response = requests.get(image_url, timeout=10)
                        
                        if image_response.status_code == 200:
                            # 이미지 데이터를 PIL Image로 변환
                            image = Image.open(io.BytesIO(image_response.content))
                            logger.info(f"이미지 크기: {image.size}, 포맷: {image.format}")
                            
                            # 모델 초기화 (가장 기본적인 설정)
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            
                            # 단순 내용 전송 (텍스트와 이미지)
                            response = model.generate_content([prompt, image])
                            story_content = response.text
                            logger.info(f"스토리 생성 완료 (이미지 포함): {len(story_content)} 자")
                        else:
                            # 이미지 로드 실패시 텍스트만으로 진행
                            logger.warning(f"이미지를 가져올 수 없습니다 (상태 코드: {image_response.status_code})")
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            response = model.generate_content(prompt)
                            story_content = response.text
                            logger.info(f"스토리 생성 완료 (텍스트만): {len(story_content)} 자")
                    except Exception as img_error:
                        # 이미지 처리 오류시 상세 로깅 후 텍스트만으로 재시도
                        logger.error(f"이미지 처리 중 오류 발생: {str(img_error)}")
                        logger.error(traceback.format_exc())
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(prompt)
                        story_content = response.text
                        logger.info(f"이미지 없이 텍스트만으로 스토리 생성 완료: {len(story_content)} 자")
                else:
                    # 텍스트만 있는 경우 단순 처리
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    story_content = response.text
                    logger.info(f"텍스트만으로 스토리 생성 완료: {len(story_content)} 자")
                
            except Exception as api_error:
                logger.error(f"Gemini API 호출 중 오류 발생: {str(api_error)}")
                logger.error(traceback.format_exc())
                raise Exception(f"Gemini API 호출 실패: {str(api_error)}")
            
            # 응답 구성
            return {
                "status": "success",
                "media_id": media_id,
                "story_content": story_content,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"스토리 생성 중 오류 발생: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "media_id": media_id,
                "message": str(e),
                "created_at": datetime.now().isoformat()
            } 