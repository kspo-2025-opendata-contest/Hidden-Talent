from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # Database
    DATABASE_URL: str = "postgresql+psycopg://shinjuyong@localhost:5432/suminjae"

    @property
    def database_url_sync(self) -> str:
        """SQLAlchemy용 동기 URL 반환 (psycopg2 또는 psycopg)"""
        url = self.DATABASE_URL
        # Render는 postgresql:// 형식을 제공하므로 변환
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24시간

    # Gemini (선택적)
    GEMINI_API_KEY: Optional[str] = None

    # App
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
