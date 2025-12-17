from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    published_date = Column(DateTime(timezone=True))
    event_start_date = Column(DateTime(timezone=True))  # 이벤트 시작 날짜/시간
    event_end_date = Column(DateTime(timezone=True))    # 이벤트 종료 날짜/시간
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    image_url = Column(String(1000))
    category = Column(String(100))
    is_notified = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Event {self.title}>"
