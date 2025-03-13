import asyncio
import os
from app.core.vision import VisionAIClient
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_vision_api():
    """Vision API 기능을 테스트합니다."""
    try:
        # Vision API 클라이언트 초기화
        client = VisionAIClient()
        logger.info("Vision API 클라이언트가 성공적으로 초기화되었습니다.")
        
        # 테스트 이미지 경로
        test_image_path = os.path.join("tests", "test_images", "test_image.jpg")
        
        # 이미지 파일 읽기
        with open(test_image_path, "rb") as image_file:
            content = image_file.read()
        
        # 이미지 분석 실행
        result = await client.analyze_image(content)
        
        # 결과 출력
        logger.info("=== Vision API 분석 결과 ===")
        logger.info(f"감지된 레이블: {len(result['labels'])}개")
        for label in result['labels'][:3]:  # 상위 3개만 출력
            logger.info(f"- {label['description']} (신뢰도: {label['score']:.2f})")
            
        logger.info(f"\n감지된 객체: {len(result['objects'])}개")
        for obj in result['objects'][:3]:  # 상위 3개만 출력
            logger.info(f"- {obj['name']} (신뢰도: {obj['score']:.2f})")
            
        logger.info(f"\n감지된 얼굴: {len(result['faces'])}개")
        logger.info(f"감지된 텍스트: {result['text']['full_text'][:100]}...")  # 처음 100자만 출력
        
        logger.info("\n테스트가 성공적으로 완료되었습니다.")
        return True
        
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    # 테스트 실행
    success = asyncio.run(test_vision_api())
    if not success:
        logger.error("Vision API 테스트가 실패했습니다.") 