from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api import events, analysis, videos, subscriptions, pokedex, raids, pvp, admin

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager
    서버 시작 시 스케줄러를 자동으로 시작하고, 종료 시 정리합니다.
    Render 클라우드 서버에서 자동으로 스케줄러가 실행되도록 보장합니다.
    """
    # Startup
    logger.info("🚀 FastAPI application starting...")
    logger.info("📅 Initializing scheduler...")

    from app.scheduler import start_scheduler
    start_scheduler()

    logger.info("✅ Scheduler started successfully")
    logger.info("✅ Application is ready to handle requests")

    yield

    # Shutdown
    logger.info("🛑 FastAPI application shutting down...")
    from app.scheduler import stop_scheduler
    stop_scheduler()
    logger.info("✅ Scheduler stopped")


app = FastAPI(
    title="Pokemon GO Tracker API",
    description="API for tracking Pokemon GO events and analyzing Pokemon screenshots",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router)
app.include_router(analysis.router)
app.include_router(videos.router)
app.include_router(subscriptions.router)
app.include_router(pokedex.router)
app.include_router(raids.router)
app.include_router(pvp.router)
app.include_router(admin.router)

# Serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {
        "message": "Pokemon GO Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "events": "/api/events",
            "analysis": "/api/analysis",
            "videos": "/api/videos",
            "subscriptions": "/api/subscriptions",
            "pokedex": "/api/pokedex",
            "raids": "/api/raids",
            "pvp": "/api/pvp",
            "admin": "/api/admin",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
