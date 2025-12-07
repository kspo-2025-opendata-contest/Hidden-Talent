from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, talent, programs, facilities, dashboard, me


app = FastAPI(
    title="숨인재 API",
    description="청소년 스포츠 재능 발굴 및 매칭 플랫폼 백엔드",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://hidden-talent-web.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(talent.router, prefix="/api/talent", tags=["Talent Diagnosis"])
app.include_router(programs.router, prefix="/api/programs", tags=["Programs"])
app.include_router(facilities.router, prefix="/api/facilities", tags=["Facilities"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(me.router, prefix="/api/me", tags=["MyPage"])


@app.get("/")
async def root():
    """API 서버 상태 확인"""
    return {
        "message": "숨인재 API 서버 실행 중",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy"}
