from google.cloud import vision
from google.cloud.vision_v1 import ImageAnnotatorClient
from google.cloud.vision_v1.types import Image
from typing import List, Dict, Any
import io
import logging
from app.core.config import settings
import os
from pathlib import Path
from google.oauth2 import service_account

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionAIClient:
    def __init__(self):
        """Vision API 클라이언트를 초기화합니다."""
        try:
            # 프로젝트 루트 디렉토리 찾기
            base_dir = Path(__file__).parent.parent.parent
            credentials_path = os.path.join(base_dir, "credentials", "vision-api-key.json")
            
            # 디버깅 정보
            logger.info(f"인증 파일 경로: {credentials_path}")
            logger.info(f"파일 존재 여부: {os.path.exists(credentials_path)}")
            
            # 명시적으로 인증 정보 제공
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = ImageAnnotatorClient(credentials=credentials)
            logger.info("Vision API 클라이언트가 성공적으로 초기화되었습니다.")
        except Exception as e:
            logger.error(f"Vision API 클라이언트 초기화 실패: {str(e)}")
            raise

    async def analyze_image(self, image_content: bytes) -> Dict[str, Any]:
        """이미지를 분석하여 다양한 특성을 추출합니다.
        
        Args:
            image_content (bytes): 분석할 이미지의 바이너리 데이터
            
        Returns:
            Dict[str, Any]: 분석 결과를 포함하는 딕셔너리
        """
        try:
            # 이미지 객체 생성
            image = Image(content=image_content)
            
            # 다양한 분석 기능 실행
            response = {
                'labels': await self._detect_labels(image),
                'objects': await self._detect_objects(image),
                'faces': await self._detect_faces(image),
                'landmarks': await self._detect_landmarks(image),
                'text': await self._detect_text(image),
                'safe_search': await self._detect_safe_search(image),
                'colors': await self._detect_properties(image)
            }
            
            logger.info("이미지 분석이 성공적으로 완료되었습니다.")
            return response
            
        except Exception as e:
            logger.error(f"이미지 분석 중 오류 발생: {str(e)}")
            raise

    async def _detect_labels(self, image: Image) -> List[Dict[str, Any]]:
        """이미지의 레이블을 감지합니다."""
        try:
            response = self.client.label_detection(image=image)
            return [{
                'description': label.description,
                'score': label.score,
                'topicality': label.topicality
            } for label in response.label_annotations]
        except Exception as e:
            logger.error(f"레이블 감지 중 오류 발생: {str(e)}")
            return []

    async def _detect_objects(self, image: Image) -> List[Dict[str, Any]]:
        """이미지 내의 객체를 감지합니다."""
        try:
            response = self.client.object_localization(image=image)
            return [{
                'name': obj.name,
                'score': obj.score,
                'bounding_box': {
                    'left': obj.bounding_poly.normalized_vertices[0].x,
                    'top': obj.bounding_poly.normalized_vertices[0].y,
                    'right': obj.bounding_poly.normalized_vertices[2].x,
                    'bottom': obj.bounding_poly.normalized_vertices[2].y
                }
            } for obj in response.localized_object_annotations]
        except Exception as e:
            logger.error(f"객체 감지 중 오류 발생: {str(e)}")
            return []

    async def _detect_faces(self, image: Image) -> List[Dict[str, Any]]:
        """이미지 내의 얼굴을 감지합니다."""
        try:
            response = self.client.face_detection(image=image)
            return [{
                'confidence': face.detection_confidence,
                'joy': face.joy_likelihood,
                'sorrow': face.sorrow_likelihood,
                'anger': face.anger_likelihood,
                'surprise': face.surprise_likelihood,
                'bounding_box': {
                    'left': face.bounding_poly.vertices[0].x,
                    'top': face.bounding_poly.vertices[0].y,
                    'right': face.bounding_poly.vertices[2].x,
                    'bottom': face.bounding_poly.vertices[2].y
                }
            } for face in response.face_annotations]
        except Exception as e:
            logger.error(f"얼굴 감지 중 오류 발생: {str(e)}")
            return []

    async def _detect_landmarks(self, image: Image) -> List[Dict[str, Any]]:
        """이미지 내의 랜드마크를 감지합니다."""
        try:
            response = self.client.landmark_detection(image=image)
            return [{
                'description': landmark.description,
                'score': landmark.score,
                'locations': [{
                    'latitude': location.lat_lng.latitude,
                    'longitude': location.lat_lng.longitude
                } for location in landmark.locations]
            } for landmark in response.landmark_annotations]
        except Exception as e:
            logger.error(f"랜드마크 감지 중 오류 발생: {str(e)}")
            return []

    async def _detect_text(self, image: Image) -> Dict[str, Any]:
        """이미지 내의 텍스트를 감지합니다."""
        try:
            response = self.client.text_detection(image=image)
            return {
                'full_text': response.text_annotations[0].description if response.text_annotations else "",
                'texts': [{
                    'text': text.description,
                    'confidence': text.confidence,
                    'bounding_box': {
                        'left': text.bounding_poly.vertices[0].x,
                        'top': text.bounding_poly.vertices[0].y,
                        'right': text.bounding_poly.vertices[2].x,
                        'bottom': text.bounding_poly.vertices[2].y
                    }
                } for text in response.text_annotations[1:]]
            }
        except Exception as e:
            logger.error(f"텍스트 감지 중 오류 발생: {str(e)}")
            return {'full_text': "", 'texts': []}

    async def _detect_safe_search(self, image: Image) -> Dict[str, Any]:
        """이미지의 안전성을 검사합니다."""
        try:
            response = self.client.safe_search_detection(image=image)
            safe = response.safe_search_annotation
            return {
                'adult': safe.adult,
                'medical': safe.medical,
                'spoof': safe.spoof,
                'violence': safe.violence,
                'racy': safe.racy
            }
        except Exception as e:
            logger.error(f"안전성 검사 중 오류 발생: {str(e)}")
            return {}

    async def _detect_properties(self, image: Image) -> Dict[str, Any]:
        """이미지의 색상 속성을 감지합니다."""
        try:
            response = self.client.image_properties(image=image)
            return {
                'dominant_colors': [{
                    'color': {
                        'red': color.color.red,
                        'green': color.color.green,
                        'blue': color.color.blue
                    },
                    'score': color.score,
                    'pixel_fraction': color.pixel_fraction
                } for color in response.image_properties_annotation.dominant_colors.colors]
            }
        except Exception as e:
            logger.error(f"이미지 속성 감지 중 오류 발생: {str(e)}")
            return {'dominant_colors': []} 