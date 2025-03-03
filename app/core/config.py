from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API 설정
    API_V1_STR: str = "/api/v1"
    
    # 백엔드 서버 설정
    BACKEND_SERVER_HOST: str = "http://localhost:8080"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8080",  # 백엔드 서버
        "http://localhost:3000"   # 프론트엔드 서버 (필요한 경우)
    ]

    # Google Cloud 공통 설정
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    
    # Translation API 설정
    GOOGLE_CLOUD_LOCATION: str = "global"
    
    # 이미지 처리 설정
    TEMP_UPLOAD_DIR: str = "temp_uploads"
    MAX_IMAGE_SIZE: str = "10485760"  # 문자열로 변경

    class Config:
        case_sensitive = True
        env_file = ".env"

    @property
    def max_image_size_int(self) -> int:
        """MAX_IMAGE_SIZE를 정수로 변환하여 반환합니다."""
        return int(self.MAX_IMAGE_SIZE)

settings = Settings()
