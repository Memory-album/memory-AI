from typing import List, Dict, Any
import logging
from enum import Enum
from google.cloud import translate_v2 as translate
from app.core.config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionLevel(Enum):
    """질문 난이도 레벨"""
    BASIC = 1      # 기본 인식/회상
    CONTEXT = 2    # 맥락/감정
    REFLECTIVE = 3 # 반성적/통합적

class QuestionCategory(Enum):
    """질문 카테고리"""
    TEMPORAL = "temporal"      # 시간-순차적
    SENSORY = "sensory"       # 감각-경험적
    RELATIONAL = "relational" # 관계-사회적
    IDENTITY = "identity"     # 정체성-내러티브

class QuestionGenerator:
    def __init__(self):
        """질문 생성기 초기화"""
        self.translate_client = None
        try:
            self.translate_client = translate.Client()
            logger.info("번역 클라이언트가 성공적으로 초기화되었습니다.")
        except Exception as e:
            logger.warning(f"번역 클라이언트 초기화 실패: {str(e)}")
            logger.warning("번역 기능이 비활성화된 상태로 실행됩니다.")

        # 영어-한국어 단어 매핑
        self.word_mapping = {
            # 장소
            'beach': '해변',
            'mountain': '산',
            'park': '공원',
            'restaurant': '식당',
            'house': '집',
            'office': '사무실',
            'sea': '바다',
            'indoor': '실내',
            'room': '방',
            'interior': '실내',
            
            # 활동
            'party': '파티',
            'wedding': '결혼식',
            'graduation': '졸업식',
            'travel': '여행',
            'sport': '운동',
            'dining': '식사',
            'vacation': '휴가',
            'ceremony': '행사',
            'award': '시상식',
            'performance': '공연',
            
            # 감정
            'happiness': '행복',
            'joy': '기쁨',
            'fun': '즐거움',
            'smile': '미소',
            'sadness': '슬픔',
            'serious': '진지함',
            'anger': '분노',
            
            # 시간
            'morning': '아침',
            'afternoon': '오후',
            'evening': '저녁',
            'night': '밤',
            
            # 날씨
            'sunny': '맑은',
            'rainy': '비오는',
            'cloudy': '흐린',
            'snowy': '눈오는'
        }

        self.question_templates = {
            QuestionCategory.TEMPORAL: {
                QuestionLevel.BASIC: [
                    "이 사진은 언제 찍은 것인가요?",
                    "이 날의 날씨는 어땠나요?",
                    "이 순간은 얼마나 오래 지속되었나요?"
                ],
                QuestionLevel.CONTEXT: [
                    "이 순간을 기록하게 된 특별한 계기가 있었나요?",
                    "이 때 가장 기억에 남는 순간은 언제인가요?",
                    "이 시기에 일상생활은 어떠했나요?"
                ],
                QuestionLevel.REFLECTIVE: [
                    "이 순간이 당신의 인생에서 어떤 의미를 가지나요?",
                    "이 때와 비교해서 지금은 무엇이 가장 크게 변했나요?",
                    "이 경험이 당신의 삶에 어떤 영향을 주었나요?"
                ]
            },
            QuestionCategory.SENSORY: {
                QuestionLevel.BASIC: [
                    "이 장소에서 들리던 소리들을 기억하시나요?",
                    "이 곳의 특별한 촉감이나 질감이 기억나시나요?",
                    "주변의 냄새나 향기가 기억나시나요?"
                ],
                QuestionLevel.CONTEXT: [
                    "이 장소의 전반적인 분위기는 어떠했나요?",
                    "주변 환경의 모습과 색감은 어땠나요?",
                    "그 곳의 온도나 공기는 어떤 느낌이었나요?"
                ],
                QuestionLevel.REFLECTIVE: [
                    "이 장소에서의 경험 중 가장 인상 깊은 감각은 무엇인가요?",
                    "이 곳의 어떤 감각적 기억이 지금도 생생한가요?",
                    "비슷한 장소에 갈 때마다 이 때의 기억이 떠오르나요?"
                ]
            },
            QuestionCategory.RELATIONAL: {
                QuestionLevel.BASIC: [
                    "사진 속 사람들은 누구인가요?",
                    "함께 있는 사람들과는 어떤 관계인가요?",
                    "이 순간을 함께 한 사람은 몇 명인가요?"
                ],
                QuestionLevel.CONTEXT: [
                    "이 사람들과 나눈 대화나 활동이 기억나시나요?",
                    "함께 있어서 특별했던 순간이 있었나요?",
                    "서로에 대해 새롭게 알게 된 점이 있나요?"
                ],
                QuestionLevel.REFLECTIVE: [
                    "이 사람들과의 관계가 현재는 어떻게 변했나요?",
                    "이 만남이 이후의 관계에 어떤 영향을 주었나요?",
                    "이 사람들과의 추억 중 가장 소중한 것은 무엇인가요?"
                ]
            },
            QuestionCategory.IDENTITY: {
                QuestionLevel.BASIC: [
                    "이 때 당신의 나이는 몇 살이었나요?",
                    "이 시기에 어떤 일을 하고 계셨나요?",
                    "당시의 취미나 관심사는 무엇이었나요?"
                ],
                QuestionLevel.CONTEXT: [
                    "이 시기에 당신에게 가장 중요했던 것은 무엇인가요?",
                    "이 때의 꿈이나 목표는 무엇이었나요?",
                    "당시의 생활방식은 어떠했나요?"
                ],
                QuestionLevel.REFLECTIVE: [
                    "이 경험이 당신을 어떻게 성장시켰나요?",
                    "이 시기의 선택들이 현재의 당신을 만드는데 어떤 영향을 주었나요?",
                    "지금 돌아보면 이 때의 자신에게 해주고 싶은 말이 있나요?"
                ]
            }
        }

    def _translate_context(self, text: str) -> str:
        """컨텍스트를 고려하여 영어 텍스트를 한국어로 변환합니다."""
        if not text:
            return text
            
        # 소문자로 변환하여 매핑 검색
        text_lower = text.lower()
        
        # 매핑된 단어가 있으면 사용
        if text_lower in self.word_mapping:
            return self.word_mapping[text_lower]
            
        # 매핑이 없는 경우 Translation API 사용 시도
        try:
            if self.translate_client:
                result = self.translate_client.translate(
                    text,
                    target_language='ko',
                    source_language='en'
                )
                return result['translatedText']
        except Exception as e:
            logger.warning(f"번역 실패, 기본 매핑 사용: {str(e)}")
            
        # 실패 시 원본 반환
        return text

    def _extract_context(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """이미지 분석 결과에서 컨텍스트 정보를 추출합니다."""
        context = {
            'location': None,
            'activity': None,
            'emotion': None,
            'time_of_day': None,
            'weather': None,
            'people_count': len(analysis_result.get('faces', [])),
            'is_indoor': False
        }
        
        # 레이블 분석
        labels = analysis_result.get('labels', [])
        for label in labels:
            desc = label['description'].lower()
            score = label['score']
            
            # 한국어로 변환
            korean_desc = self._translate_context(desc)
            
            # 감정 분석
            if desc in ['happiness', 'joy', 'fun', 'smile']:
                context['emotion'] = {'type': 'positive', 'score': score, 'label': korean_desc}
            elif desc in ['sadness', 'serious', 'anger']:
                context['emotion'] = {'type': 'negative', 'score': score, 'label': korean_desc}
                
            # 장소 분석
            if any(word in desc for word in ['beach', 'mountain', 'park', 'restaurant', 'house', 'office', 'sea']):
                context['location'] = {'type': desc, 'score': score, 'label': korean_desc}
                
            # 활동 분석
            if any(word in desc for word in ['party', 'wedding', 'graduation', 'travel', 'sport', 'dining', 'vacation']):
                context['activity'] = {'type': desc, 'score': score, 'label': korean_desc}
                
            # 실내/실외 분석
            if any(word in desc for word in ['indoor', 'room', 'interior']):
                context['is_indoor'] = True
                
            # 시간/날씨 분석
            if any(word in desc for word in ['morning', 'afternoon', 'evening', 'night']):
                context['time_of_day'] = {'type': desc, 'score': score, 'label': korean_desc}
            elif any(word in desc for word in ['sunny', 'rainy', 'cloudy', 'snowy']):
                context['weather'] = {'type': desc, 'score': score, 'label': korean_desc}
        
        return context

    def generate_questions(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Vision API 분석 결과를 기반으로 질문을 생성합니다.
        
        Args:
            analysis_result: Vision API의 이미지 분석 결과
            
        Returns:
            List[Dict[str, Any]]: 생성된 질문 목록
        """
        questions = []
        
        # 컨텍스트 정보 추출
        context = self._extract_context(analysis_result)
        
        # 1. 시간-순차적 질문 생성
        temporal_questions = self._generate_temporal_questions(analysis_result, context)
        questions.extend(temporal_questions[:3])
        
        # 2. 감각-경험적 질문 생성
        sensory_questions = self._generate_sensory_questions(analysis_result, context)
        questions.extend(sensory_questions[:3])
        
        # 3. 관계-사회적 질문 생성
        relational_questions = self._generate_relational_questions(analysis_result, context)
        questions.extend(relational_questions[:3])
        
        # 4. 정체성-내러티브 질문 생성 (필요한 경우)
        if len(questions) < 5:
            identity_questions = self._generate_identity_questions(analysis_result)
            questions.extend(identity_questions[:3])  # 최대 3개
        
        # 최소 5개 질문 확보
        while len(questions) < 5:
            questions.append({
                "category": QuestionCategory.TEMPORAL.value,
                "level": QuestionLevel.BASIC.value,
                "question": "이 순간에 대해 기억나는 것을 자유롭게 이야기해주세요."
            })
        
        return questions[:10]  # 최대 10개 질문 반환

    def _generate_temporal_questions(self, analysis_result: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """컨텍스트를 고려한 시간-순차적 질문을 생성합니다."""
        questions = []
        base_questions = self.question_templates[QuestionCategory.TEMPORAL]
        
        # 기본 시간 관련 질문 추가
        questions.append({
            "category": QuestionCategory.TEMPORAL.value,
            "level": QuestionLevel.BASIC.value,
            "question": base_questions[QuestionLevel.BASIC][0]
        })
        
        # 활동이나 이벤트가 감지된 경우
        if context['activity']:
            activity_label = context['activity']['label']
            question = f"이 {activity_label}을(를) 계획하게 된 계기가 있었나요?"
            questions.append({
                "category": QuestionCategory.TEMPORAL.value,
                "level": QuestionLevel.CONTEXT.value,
                "question": question
            })
        
        # 특별한 감정이 감지된 경우
        if context['emotion'] and context['emotion']['score'] > 0.8:
            questions.append({
                "category": QuestionCategory.TEMPORAL.value,
                "level": QuestionLevel.REFLECTIVE.value,
                "question": "이 순간의 감정이 이후의 삶에 어떤 영향을 주었나요?"
            })
        
        return questions

    def _generate_sensory_questions(self, analysis_result: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """컨텍스트를 고려한 감각-경험적 질문을 생성합니다."""
        questions = []
        base_questions = self.question_templates[QuestionCategory.SENSORY]
        
        # 장소가 감지된 경우 특화된 질문 생성
        if context['location']:
            location_label = context['location']['label']
            question = f"이 {location_label}에서의 특별한 소리나 냄새가 기억나시나요?"
            questions.append({
                "category": QuestionCategory.SENSORY.value,
                "level": QuestionLevel.BASIC.value,
                "question": question
            })
        
        # 날씨나 시간대가 감지된 경우
        if context['weather'] or context['time_of_day']:
            weather = context['weather']['label'] if context['weather'] else None
            time = context['time_of_day']['label'] if context['time_of_day'] else None
            if weather and time:
                question = f"{time}의 {weather} 날씨는 어떤 느낌이었나요?"
                questions.append({
                    "category": QuestionCategory.SENSORY.value,
                    "level": QuestionLevel.CONTEXT.value,
                    "question": question
                })
        
        # 실내/실외 여부에 따른 질문
        space_type = '실내' if context['is_indoor'] else '실외'
        questions.append({
            "category": QuestionCategory.SENSORY.value,
            "level": QuestionLevel.REFLECTIVE.value,
            "question": f"이 {space_type} 공간의 분위기는 어떠했나요?"
        })
        
        return questions

    def _generate_relational_questions(self, analysis_result: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """컨텍스트를 고려한 관계-사회적 질문을 생성합니다."""
        questions = []
        base_questions = self.question_templates[QuestionCategory.RELATIONAL]
        
        # 얼굴이 감지된 경우
        if context['people_count'] > 0:
            questions.append({
                "category": QuestionCategory.RELATIONAL.value,
                "level": QuestionLevel.BASIC.value,
                "question": base_questions[QuestionLevel.BASIC][0]
            })
            
            # 여러 명의 얼굴이 감지된 경우
            if context['people_count'] > 1:
                questions.append({
                    "category": QuestionCategory.RELATIONAL.value,
                    "level": QuestionLevel.CONTEXT.value,
                    "question": "이 자리에서 서로 어떤 이야기를 나누었나요?"
                })
        
        # 특별한 활동이나 감정이 감지된 경우
        if context['activity'] or (context['emotion'] and context['emotion']['type'] == 'positive'):
            questions.append({
                "category": QuestionCategory.RELATIONAL.value,
                "level": QuestionLevel.REFLECTIVE.value,
                "question": "이 순간이 서로의 관계에 어떤 의미를 가져다주었나요?"
            })
        
        return questions

    def _generate_identity_questions(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """정체성-내러티브 질문을 생성합니다."""
        questions = []
        
        # 특별한 활동이나 성취가 감지된 경우
        achievement_labels = ["graduation", "ceremony", "award", "performance", "sport"]
        if any(label["description"].lower() in achievement_labels for label in analysis_result.get("labels", [])):
            questions.append({
                "category": QuestionCategory.IDENTITY.value,
                "level": QuestionLevel.BASIC.value,
                "question": self.question_templates[QuestionCategory.IDENTITY][QuestionLevel.BASIC][1]
            })
            
            questions.append({
                "category": QuestionCategory.IDENTITY.value,
                "level": QuestionLevel.REFLECTIVE.value,
                "question": self.question_templates[QuestionCategory.IDENTITY][QuestionLevel.REFLECTIVE][0]
            })
        
        return questions 