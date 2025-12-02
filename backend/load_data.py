#!/usr/bin/env python3
"""
Manually trigger crawlers to load initial data
"""
import asyncio
from app.services.crawler_service import crawler
from app.services.youtube_service import youtube_service
from app.database import get_db
from app.models import Event, Video
from sqlalchemy.orm import Session


async def load_events(db: Session):
    """Load Pokemon GO events"""
    print("Loading Pokemon GO events...")
    events_data = await crawler.fetch_events()

    for event_data in events_data:
        # Check if event already exists
        existing = db.query(Event).filter_by(url=event_data['url']).first()
        if not existing:
            event = Event(
                title=event_data['title'],
                url=event_data['url'],
                summary=event_data.get('summary'),
                published_date=event_data.get('published_date'),
                image_url=event_data.get('image_url'),
                category=event_data.get('category')
            )
            db.add(event)

    db.commit()
    print(f"Loaded {len(events_data)} events")


async def load_videos(db: Session):
    """Load YouTube battle videos"""
    print("Loading YouTube battle videos...")
    videos_data = await youtube_service.fetch_latest_videos(max_results=20)

    for video_data in videos_data:
        # Check if video already exists
        existing = db.query(Video).filter_by(video_id=video_data['video_id']).first()
        if not existing:
            video = Video(
                video_id=video_data['video_id'],
                title=video_data['title'],
                channel_name=video_data['channel_name'],
                thumbnail_url=video_data.get('thumbnail_url'),
                description=video_data.get('description'),
                published_date=video_data.get('published_at'),
                video_url=video_data['video_url'],
                view_count=video_data.get('view_count')
            )
            db.add(video)

    db.commit()
    print(f"Loaded {len(videos_data)} videos")


async def main():
    """Main function to load all data"""
    # Get database session
    db_gen = get_db()
    db = next(db_gen)

    try:
        await load_events(db)
        await load_videos(db)
        print("\n✅ Data loading completed successfully!")
    except Exception as e:
        print(f"\n❌ Error loading data: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
