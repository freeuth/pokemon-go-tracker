from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.event import Event
from app.services.crawler_service import crawler
from app.services.email_service import email_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/events", tags=["events"])


class EventResponse(BaseModel):
    id: int
    title: str
    url: str
    summary: Optional[str]
    published_date: Optional[datetime]
    image_url: Optional[str]
    category: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[EventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get all Pokemon GO events"""
    events = db.query(Event).order_by(desc(Event.published_date)).offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get specific event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/crawl")
async def trigger_crawl(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger event crawling"""
    background_tasks.add_task(crawl_and_notify, db)
    return {"message": "Crawling started in background"}


async def crawl_and_notify(db: Session):
    """Background task to crawl events and send notifications"""
    try:
        # Fetch events from Pokemon GO website
        events = await crawler.fetch_events()

        new_events_count = 0

        for event_data in events:
            # Check if event already exists
            existing_event = db.query(Event).filter(Event.url == event_data['url']).first()

            if not existing_event:
                # Create new event
                new_event = Event(
                    title=event_data['title'],
                    url=event_data['url'],
                    summary=event_data.get('summary'),
                    published_date=event_data.get('published_date'),
                    image_url=event_data.get('image_url'),
                    category=event_data.get('category'),
                    is_notified=False
                )
                db.add(new_event)
                db.commit()
                db.refresh(new_event)

                # Send email notification
                email_service.send_new_event_notification(event_data)

                # Mark as notified
                new_event.is_notified = True
                db.commit()

                new_events_count += 1

        return {"new_events": new_events_count}

    except Exception as e:
        db.rollback()
        raise e
