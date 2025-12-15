"""
Main entry point for the Pokemon GO Tracker backend
Starts the FastAPI server with scheduler via lifespan
"""
import uvicorn
from app.main import app
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Start the application
    스케줄러는 main.py의 lifespan에서 자동으로 시작됩니다.
    """
    logger.info("🚀 Pokemon GO Tracker starting...")

    try:
        # Start the FastAPI server (scheduler는 lifespan에서 자동 시작)
        uvicorn.run(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    main()
