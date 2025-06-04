from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.core.config import settings
from app.api.v1.api import router as api_v1_router

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="Memory AI Service",
    description="Memory Album AI Analysis Service",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Memory AI API 서버에 오신 것을 환영합니다~~~~!!!!🥰"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}