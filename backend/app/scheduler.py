from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from typing import Dict
from datetime import datetime
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.crawler_service import crawler
from app.services.email_service import email_service
from app.services.youtube_service import youtube_service
from app.models.event import Event
from app.models.youtube_video import YouTubeVideo
from app.models.email_subscription import EmailSubscription
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Render 클라우드 서버에서 안정적으로 동작하도록 설정
scheduler = AsyncIOScheduler(
    timezone='Asia/Seoul',
    job_defaults={
        'coalesce': True,  # 누락된 실행을 하나로 합침
        'max_instances': 1,  # 동시 실행 방지
        'misfire_grace_time': 300  # 5분 지연까지 허용
    }
)


async def scheduled_crawl_job():
    """
    Scheduled job to crawl Pokemon GO events
    매일 10:00 (Asia/Seoul) 실행 - 새 뉴스가 있을 때만 이메일 발송
    Render 클라우드 서버에서 자동 실행
    """
    logger.info("=" * 80)
    logger.info(f"🕐 [SCHEDULER] Scheduled crawl job started at {datetime.now()}")
    logger.info("=" * 80)

    db = SessionLocal()
    new_events = []

    try:
        # 1. 크롤링
        logger.info("📡 Fetching events from Pokemon GO website...")
        events = await crawler.fetch_events()
        logger.info(f"✅ Found {len(events)} total events from website")

        # 2. 신규 이벤트 확인 및 저장
        for event_data in events:
            existing_event = db.query(Event).filter(Event.url == event_data['url']).first()

            if not existing_event:
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
                new_events.append(event_data)
                logger.info(f"🆕 New event: {event_data['title'][:50]}...")

        db.commit()

        # 3. 이메일 발송 (신규 이벤트가 있을 때만)
        if new_events:
            logger.info(f"📧 {len(new_events)} new events found. Sending email...")
            email_sent = email_service.send_daily_news_summary(new_events, None)

            if email_sent:
                # 이메일 발송 성공 시 is_notified 업데이트
                for event_data in new_events:
                    event = db.query(Event).filter(Event.url == event_data['url']).first()
                    if event:
                        event.is_notified = True
                db.commit()
                logger.info(f"✅ Email sent successfully for {len(new_events)} events")
            else:
                logger.error("❌ Email sending failed")
        else:
            logger.info("📭 No new events. No email sent.")

        logger.info(f"✅ Scheduled crawl completed successfully")

    except Exception as e:
        logger.error(f"❌ ERROR in scheduled_crawl_job:")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error(f"   Error message: {str(e)}")
        logger.error(f"   Traceback:\n{traceback.format_exc()}")
        db.rollback()

    finally:
        db.close()
        logger.info("=" * 80)


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

    Render 클라우드 서버에서 자동으로 실행됩니다.
    초기 크롤링은 수행하지 않으며, 스케줄에 따라서만 실행됩니다.
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
    logger.info(f"✅ Scheduler started successfully")
    logger.info(f"📅 Pokemon GO news: Daily at 10:00 AM (Asia/Seoul)")
    logger.info(f"🎬 YouTube videos: Daily at 10:00 AM (Asia/Seoul)")
    logger.info(f"💡 Use POST /api/admin/crawl-now for manual testing")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped.")


def get_scheduler_status() -> Dict:
    """
    스케줄러 상태 확인
    Render 클라우드 서버에서 스케줄러가 정상 실행 중인지 확인하는 API용
    """
    try:
        is_running = scheduler.running
        jobs = scheduler.get_jobs()

        jobs_info = []
        for job in jobs:
            next_run = job.next_run_time
            jobs_info.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": next_run.isoformat() if next_run else None,
                "trigger": str(job.trigger)
            })

        return {
            "running": is_running,
            "timezone": str(scheduler.timezone),
            "jobs_count": len(jobs),
            "jobs": jobs_info,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error getting scheduler status: {str(e)}")
        return {
            "running": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
