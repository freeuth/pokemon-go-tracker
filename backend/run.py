"""
Main entry point for the Pokemon GO Tracker backend
Starts both the FastAPI server and the scheduler
"""
import uvicorn
import asyncio
from app.main import app
from app.scheduler import start_scheduler, stop_scheduler
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Start the application with scheduler"""
    # Start the scheduler
    start_scheduler()
    logger.info("🚀 Pokemon GO Tracker starting...")

    try:
        # Start the FastAPI server
        uvicorn.run(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        stop_scheduler()


if __name__ == "__main__":
    main()
