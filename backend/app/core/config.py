from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Mode
    MODE: str = "test"  # test or production

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/pokemon_go_db"

    # Gmail SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
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

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://pokemon-go-tracker.vercel.app"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
