from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    channel_name = Column(String(200), nullable=False)
    channel_id = Column(String(100))
    thumbnail_url = Column(String(1000))
    description = Column(Text)
    published_at = Column(DateTime(timezone=True))
    view_count = Column(Integer, default=0)
    video_url = Column(String(500))
    tags = Column(JSON, default=list)  # 태그 목록 (배틀 리그, 가이드 등)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<YouTubeVideo {self.title}>"
