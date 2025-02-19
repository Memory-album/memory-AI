class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Memory AI Service"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # React 프론트엔드
    
    class Config:
        env_file = ".env"
