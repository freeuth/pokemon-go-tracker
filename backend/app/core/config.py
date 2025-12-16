from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Mode
    MODE: str = "test"  # test or production

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/pokemon_go_db"

    # SendGrid Email (Render 클라우드 서버용)
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@pokemongo-tracker.com"
    TO_EMAIL: str = "treehi1@gmail.com"

    # Gmail SMTP (Deprecated - 기존 코드 호환성 유지)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    NOTIFICATION_EMAIL: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Crawler
    CRAWLER_INTERVAL_MINUTES: int = 30
    POKEMONGO_NEWS_URL: str = "https://pokemongolive.com/en/post/"

    # OCR
    TESSERACT_CMD: Optional[str] = None

    # YouTube RSS Feeds (comma-separated URLs)
    YOUTUBE_RSS_FEEDS: str = ""

    # CORS - comma-separated list of allowed origins
    ALLOWED_ORIGINS_STR: str = "http://localhost:3000,http://127.0.0.1:3000,https://pokemon-go-tracker.vercel.app"

    @property
    def ALLOWED_ORIGINS(self) -> list:
        """Parse comma-separated origins string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(",") if origin.strip()]
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
