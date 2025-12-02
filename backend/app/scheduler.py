from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.crawler_service import crawler
from app.services.email_service import email_service
from app.services.youtube_service import youtube_service
from app.models.event import Event
from app.models.youtube_video import YouTubeVideo
from app.models.email_subscription import EmailSubscription
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone='Asia/Seoul')


async def scheduled_crawl_job():
    """
    Scheduled job to crawl Pokemon GO events
    매일 10:00 (Asia/Seoul) 실행 - 새 뉴스가 있을 때만 이메일 발송
    """
    logger.info("Starting scheduled event crawl...")
    db = SessionLocal()
    new_events = []  # 새로 추가된 이벤트 목록

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

                logger.info(f"New event found: {event_data['title']}")
                new_events.append(event_data)  # 새 이벤트를 리스트에 추가
                new_events_count += 1

        # 새 뉴스가 하나라도 있을 때만 이메일 발송
        if new_events:
            logger.info(f"Found {new_events_count} new events. Sending email notification...")

            # 이메일 발송 - treehi1@gmail.com으로 고정
            recipient_email = 'treehi1@gmail.com'

            # 새로운 이벤트들을 이메일로 발송
            email_service.send_daily_news_summary(new_events, [recipient_email])

            # Mark all new events as notified
            for event_data in new_events:
                event = db.query(Event).filter(Event.url == event_data['url']).first()
                if event:
                    event.is_notified = True

            db.commit()
            logger.info(f"Email sent successfully to {recipient_email}")
        else:
            logger.info("No new events found. No email sent.")

        logger.info(f"Crawl completed. Found {new_events_count} new events.")

    except Exception as e:
        logger.error(f"Error during scheduled crawl: {str(e)}")
        db.rollback()
    finally:
        db.close()


async def scheduled_youtube_crawl_job():
    """
    Scheduled job to crawl YouTube battle videos from RSS feeds
    매일 오전 10시 실행 (Asia/Seoul)
    - 최근 2주일 영상만 수집
    - 3개월 지난 영상 자동 삭제
    """
    logger.info("Starting scheduled YouTube RSS feed crawl...")
    db = SessionLocal()
    new_videos = []  # 새로 추가된 영상 목록

    try:
        # 1. 3개월 지난 영상 삭제
        from datetime import datetime, timedelta
        three_months_ago = datetime.now() - timedelta(days=90)

        deleted_count = db.query(YouTubeVideo).filter(
            YouTubeVideo.published_at < three_months_ago
        ).delete()

        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} videos older than 3 months")

        # 2. 최근 2주일 영상 수집 (fetch_latest_videos에서 필터링됨)
        videos = await youtube_service.fetch_latest_videos(max_results=50)
        new_videos_count = 0

        for video_data in videos:
            # Check if video already exists
            existing_video = db.query(YouTubeVideo).filter(
                YouTubeVideo.video_id == video_data['video_id']
            ).first()

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
                    view_count=video_data.get('view_count', 0),
                    tags=video_data.get('tags', [])
                )
                db.add(new_video)
                new_videos.append(video_data)
                new_videos_count += 1

        db.commit()
        logger.info(f"YouTube RSS crawl completed. Found {new_videos_count} new videos from RSS feeds.")

    except Exception as e:
        logger.error(f"Error during scheduled YouTube RSS crawl: {str(e)}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """
    Initialize and start the scheduler
    - 뉴스 크롤링: 매일 10:00 (Asia/Seoul)
    - YouTube 영상 크롤링: 매일 10:00 (Asia/Seoul) - 최근 2주일 영상만, 3개월 지난 영상 자동 삭제
    """
    # Schedule the event crawl job to run daily at 10:00 AM (Asia/Seoul)
    scheduler.add_job(
        scheduled_crawl_job,
        trigger=CronTrigger(hour=10, minute=0, timezone='Asia/Seoul'),
        id='pokemon_go_crawler',
        name='Crawl Pokemon GO events (Daily 10:00 Asia/Seoul)',
        replace_existing=True
    )

    # Schedule the YouTube video crawl job to run daily at 10:00 AM (Asia/Seoul)
    scheduler.add_job(
        scheduled_youtube_crawl_job,
        trigger=CronTrigger(hour=10, minute=0, timezone='Asia/Seoul'),
        id='youtube_video_crawler',
        name='Crawl YouTube battle videos (Daily 10:00 Asia/Seoul)',
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"Scheduler started.")
    logger.info(f"  - Pokemon GO news: Daily at 10:00 AM (Asia/Seoul)")
    logger.info(f"  - YouTube videos: Daily at 10:00 AM (Asia/Seoul) - 2 weeks recent, 3 months auto-delete")

    # Run initial crawl immediately on startup
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scheduled_crawl_job())
    loop.run_until_complete(scheduled_youtube_crawl_job())
    loop.close()
    logger.info("Initial data load completed.")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped.")
