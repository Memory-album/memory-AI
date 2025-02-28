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

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
