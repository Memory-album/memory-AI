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
        """프롬프트 생성 메서드 """ # 기존 주석 유지

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

        # << 프롬프트 내용 수정 시작 >>
        prompt = f"""# 스토리텔링 생성 요청: **주어진 정보에 기반한** 사진 속 기억 재구성

## **Core Task (핵심 임무):**
주어진 사진 이미지와 사용자의 질문-답변(Q&A) 내용을 **정확히** 분석하여, 단순한 정보 나열이 아닌 **사용자의 소중한 추억을 따뜻하고 의미 있게, 그리고 사실에 기반하여** 재구성하는 감성 스토리텔링을 생성합니다. 목표는 사용자가 그 순간의 감정과 의미를 **제공된 정보를 바탕으로** 다시 느낄 수 있도록 돕는 것입니다.

## **Crucial Grounding Rules (매우 중요한 준수 사항 - 반드시 지키세요!):**
1.  **Factuality First (사실 우선 원칙):** 생성되는 모든 내용은 **반드시 제공된 질문-답변(Q&A) 내용과 사진 이미지에 명확히 나타난 정보에 근거해야 합니다.**
2.  **No Fabrication (내용 조작 절대 금지):** Q&A나 이미지에 **언급되거나 명시되지 않은 새로운 인물, 사건, 구체적인 장소, 대화 내용 등을 절대로 임의로 만들어내거나 추측하여 추가하지 마십시오.** 이는 사용자의 실제 기억과 다를 수 있으며, 서비스의 신뢰도를 저해합니다.
3.  **Stick to Provided Information (제공된 정보 내에서만 서술):** 답변이 짧거나 정보가 부족하더라도, **있는 정보를 최대한 활용하여 감성을 표현하되, 없는 사실을 상상하거나 지어내서는 안 됩니다.** 만약 Q&A 정보가 너무 부족하여 의미 있는 스토리 구성이 어렵다면, 주어진 정보만을 간결하게 요약하고 따뜻한 감상을 덧붙이는 선에서 마무리하십시오. 절대 없는 이야기를 만들지 마십시오.

## **Input Analysis Guidance (입력 분석 가이드):**

1.  **Image Analysis (이미지 분석 - Q&A 보조 역할):**
    *   사진의 전체적인 분위기(예: 행복, 평온, 활기참, 그리움)를 파악하세요. **(단, 이는 Q&A 내용과 모순되지 않는 선에서, Q&A 내용을 뒷받침하는 근거로만 활용되어야 합니다.)**
    *   주요 인물의 표정, 시선, 자세를 관찰하고 감정을 추론하세요. **(추론은 반드시 Q&A 내용을 보강하거나 설명하는 방향으로 이루어져야 하며, Q&A에 없는 새로운 감정을 부여하지 마십시오.)**
    *   배경(장소, 시간대, 계절)과 주요 사물(특별한 의미가 있을 수 있는 것)을 주의 깊게 보세요.
    *   이 시각적 정보들은 스토리의 **보조적인 묘사 수단**으로 활용하되, **Q&A 내용이 주된 정보 근거가 되어야 합니다.**

2.  **Q&A Deep Dive (Q&A 심층 분석 및 활용 원칙 - 가장 중요!):**
    *   각 답변에서 사용자가 강조하는 **핵심 감정, 인물, 장소, 사건**을 정확히 파악하여 이를 스토리의 중심으로 삼으세요.
    *   답변들 사이의 연관성을 찾아 **제공된 정보 내에서만 해석 가능한** 이야기나 주제를 발견하세요.
    *   질문의 'theme'이나 'category'를 참고하여 답변의 맥락을 더 깊이 이해하고, 이를 스토리에 반영하세요.
    *   **답변이 짧거나 추상적이더라도, 이미지 정보를 보조적으로 활용하여 구체적인 장면이나 감정으로 확장할 수 있습니다. 그러나 이는 반드시 Q&A에서 벗어나지 않는 범위 내에서, Q&A 내용을 설명하거나 구체화하는 방식으로만 이루어져야 합니다. (예: Q&A에 "즐거웠다"는 답변이 있고 사진이 웃는 모습이라면, "사진 속 환한 미소는 그때의 즐거움을 말해주는 듯합니다" 와 같이 표현하십시오. "갑자기 친구가 나타나서 즐거웠다" 와 같이 Q&A에 없는 새로운 사건을 만들지 마십시오.)**

## **Narrative Crafting Instructions (스토리 구성 지침):**

1.  **Find the Emotional Core (Q&A 기반 감정의 핵 찾기):** 스토리의 중심이 될 **가장 중요한 감정이나 의미를 Q&A에서** 찾아 명확히 하세요.
2.  **Weave Image and Text Seamlessly (사실 기반 이미지와 텍스트 결합):** 사진 속 시각적 요소(색감, 빛, 사물, 인물의 모습 등)를 묘사하며, 이를 사용자의 **답변 내용과 사실에 부합하도록, 그리고 Q&A 내용을 뒷받침하도록 자연스럽게 연결**하세요.
3.  **Show, Don't Just Tell (Q&A 내용 구체화로 보여주기):** '행복했다'고 답변했다면, 그 행복이 사진 속 어떤 모습으로 드러나는지, 또는 답변의 어떤 구체적인 표현이나 뉘앙스에서 느껴지는지 등을 묘사하여 **Q&A의 감정을 생생하게 보여주세요.**
4.  **Sensory Richness (제한적 감각 묘사 허용):** 시각 정보 외에 그 순간에 있었을 법한 소리, 냄새, 촉감 등을 상상하여 생생함을 더할 수 있습니다. 단, **이는 Q&A 내용이나 이미지에서 충분히 유추 가능하고 일반적인 상황에 국한되어야 합니다. (예: 바다 사진 -> '짭짤한 바다 내음이 느껴지는 듯합니다', 숲 사진 -> '고요한 숲 속 새소리가 들리는 듯합니다' 등. 특정 인물의 목소리, 특별한 음악, 구체적인 대화 내용 등은 Q&A에 명시적으로 언급되지 않았다면 절대 추가하지 마십시오.)**
5.  **Meaningful Reflection (Q&A 중심의 의미 있는 성찰):** 스토리 끝에는 **Q&A를 통해 드러난** 그 기억이 사용자에게 어떤 의미를 지니는지, 혹은 그날의 감정이 현재까지 어떻게 이어지는지에 대한 짧고 따뜻한 성찰이나 여운을 남겨주세요. **이 역시 Q&A 내용에 기반해야 합니다.**
6.  **Perspective & Tone (시점과 어조):**
    *   **스타일:** `{style}` (예: 따뜻하고 회상적인, 공감적이고 다정한, 약간은 아련한). **사용자의 답변 어투와 감정을 존중하며, 과장되지 않고 진솔한** 긍정적이고 부드러운 어조를 유지하세요.
    *   **시점:** 1인칭('나' 또는 '우리') 또는 사용자에게 말을 거는 듯한 2인칭('당신은', '기억하나요?')이나 따뜻한 3인칭 서술자 시점을 유연하게 사용하되, **일관성**을 유지하세요. 사용자의 답변 뉘앙스에 가장 잘 어울리는 시점을 선택하세요.

## **Output Specifications (출력 명세):**

*   **길이:** `{length_desc}` 로 작성해주세요.
*   **형식:** 제목 없이, 마크다운 서식(예: `#`, `*`)을 사용하지 않은 **일반 텍스트**로만 작성해주세요.
*   **가독성:** 자연스러운 단락 구분을 사용하여 읽기 편하게 구성해주세요.
*   **내용:** **오직 제공된 Q&A와 이미지에 명시적으로 기반한** 긍정적이고 감동을 줄 수 있는 내용에 초점을 맞추세요. **절대로 정보를 추가하거나 왜곡하거나 없는 이야기를 지어내지 마세요. 이것이 가장 중요한 원칙입니다.**

## **피해야 할 스토리텔링 예시 (환각 및 조작 예시):**

### 예시 1: 언급되지 않은 인물/사건 추가 (Q&A 위반)
*   [Q: 가장 기억에 남는 순간은? A: 졸업식 날 친구들과 사진 찍은 것]
*   [Image: 졸업식 단체 사진]
*   **잘못된 스토리 (환각):** 졸업식 날, 교장 선생님께서 깜짝 등장하셔서 모두에게 선물을 나눠주셨죠. 그리고 우리는 다 같이 교가를 불렀습니다. (-> 교장 선생님의 등장, 선물, 교가 등은 Q&A나 이미지에 없는 내용)
*   **올바른 접근:** 졸업식 날, 사진 속 친구들과 함께 환하게 웃던 그 순간의 벅찬 감정과 설렘이 고스란히 전해집니다. 함께 했던 소중한 시간들이 주마등처럼 스쳐 지나가는 듯합니다.

### 예시 2: Q&A와 무관한 과도한 상상 (Q&A 위반)
*   [Q: 이 장소에서 무엇을 했나요? A: 조용히 산책했어요.]
*   [Image: 숲길 사진]
*   **잘못된 스토리 (환각):** 이 신비로운 숲길에서 당신은 길을 잃고 헤매다 우연히 숨겨진 폭포를 발견했을지도 모릅니다. 그곳에서 소원을 빌었을 수도 있고요.
*   **올바른 접근:** 사진 속 고요하고 아름다운 숲길은 당신이 즐겼던 평화로운 산책의 순간을 떠올리게 합니다. 발밑의 낙엽 소리와 맑은 공기가 느껴지는 듯합니다.

## **질문과 답변 정보 (이 정보를 절대 벗어나거나 왜곡하지 마십시오):**
다음은 분석에 사용할 질문과 답변입니다. 여기에 없는 내용은 절대로 스토리에 포함시키지 마십시오.

"""
        # << 프롬프트 내용 수정 끝 >>

        for category, qa_list in categorized_qa.items():
            prompt += f"\n### {category.upper()} 카테고리\n"
            for qa in qa_list:
                prompt += f"- 질문 ({qa['theme'] if qa.get('theme') else 'general'} / Level {qa['level']}): {qa['question']}\n"
                prompt += f"  답변: {qa['answer']}\n"

        prompt += "\n---\n**이제 위의 모든 가이드라인, 특히 'Crucial Grounding Rules'와 '피해야 할 스토리텔링 예시'를 엄격히 준수하여, 오직 제공된 이미지와 Q&A 정보만을 바탕으로 사실에 기반한 감동적인 스토리텔링을 작성해주세요. 다시 한번 강조합니다: 절대로 제공된 정보 외의 내용을 추가하거나 지어내지 마십시오. 사용자의 실제 기억을 존중하는 것이 가장 중요합니다.**"

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
                            response = await model.generate_content_async([prompt, image]) # async로 호출하려면 await 추가
                            story_content = response.text
                            logger.info(f"스토리 생성 완료 (이미지 포함): {len(story_content)} 자")
                        else:
                            # 이미지 로드 실패시 텍스트만으로 진행
                            logger.warning(f"이미지를 가져올 수 없습니다 (상태 코드: {image_response.status_code})")
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            response = await model.generate_content_async(prompt) # async로 호출하려면 await 추가
                            story_content = response.text
                            logger.info(f"스토리 생성 완료 (텍스트만): {len(story_content)} 자")
                    except Exception as img_error:
                        # 이미지 처리 오류시 상세 로깅 후 텍스트만으로 재시도
                        logger.error(f"이미지 처리 중 오류 발생: {str(img_error)}")
                        logger.error(traceback.format_exc())
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = await model.generate_content_async(prompt) # async로 호출하려면 await 추가
                        story_content = response.text
                        logger.info(f"이미지 없이 텍스트만으로 스토리 생성 완료: {len(story_content)} 자")
                else:
                    # 텍스트만 있는 경우 단순 처리
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = await model.generate_content_async(prompt) # async로 호출하려면 await 추가
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