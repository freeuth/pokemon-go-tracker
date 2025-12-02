from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.youtube_video import YouTubeVideo
from app.services.youtube_service import youtube_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/videos", tags=["videos"])


class VideoResponse(BaseModel):
    id: int
    video_id: str
    title: str
    channel_name: str
    thumbnail_url: Optional[str]
    description: Optional[str]
    published_at: Optional[datetime]
    video_url: Optional[str]
    view_count: Optional[int]
    tags: Optional[List[str]] = []

    class Config:
        from_attributes = True


@router.get("/", response_model=List[VideoResponse])
async def get_videos(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get all Pokemon GO battle videos"""
    videos = (
        db.query(YouTubeVideo)
        .order_by(desc(YouTubeVideo.published_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return videos


@router.post("/refresh")
async def refresh_videos(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger video refresh"""
    background_tasks.add_task(fetch_and_store_videos, db)
    return {"message": "Video refresh started in background"}


async def fetch_and_store_videos(db: Session):
    """Background task to fetch YouTube videos and store them"""
    try:
        videos = await youtube_service.fetch_latest_videos(max_results=10)

        new_videos_count = 0

        for video_data in videos:
            # Check if video already exists
            existing_video = (
                db.query(YouTubeVideo)
                .filter(YouTubeVideo.video_id == video_data['video_id'])
                .first()
            )

            if not existing_video:
                # Create new video entry
                new_video = YouTubeVideo(
                    video_id=video_data['video_id'],
                    title=video_data['title'],
                    channel_name=video_data['channel_name'],
                    channel_id=video_data.get('channel_id'),
                    thumbnail_url=video_data.get('thumbnail_url'),
                    description=video_data.get('description'),
                    published_at=video_data.get('published_at'),
                    video_url=video_data.get('video_url'),
                    view_count=video_data.get('view_count', 0)
                )
                db.add(new_video)
                new_videos_count += 1

        db.commit()
        return {"new_videos": new_videos_count}

    except Exception as e:
        db.rollback()
        raise e
