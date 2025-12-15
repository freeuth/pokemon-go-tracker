from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
import logging
from app.services.pokedex_data_loader import get_data_loader
from app.services.crawler_service import crawler
from app.services.email_service import email_service
from app.core.database import SessionLocal
from app.models.event import Event

router = APIRouter(prefix="/api/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


class ReloadResponse(BaseModel):
    status: str
    message: str


@router.post("/reload-data", response_model=ReloadResponse)
async def reload_data():
    """
    Reload all JSON data files without restarting the server

    Use this endpoint after updating any of the data files:
    - pokemon_base.json
    - moves.json
    - pokemon_moves.json
    - seasonal_tiers.json
    - raid_counters.json
    - pvp_party_rankings.json

    This allows you to update season data, add new Pokémon, or modify
    tier rankings without server downtime.
    """
    try:
        loader = get_data_loader()
        loader.reload_data()

        return ReloadResponse(
            status="success",
            message="All data files reloaded successfully"
        )
    except Exception as e:
        return ReloadResponse(
            status="error",
            message=f"Failed to reload data: {str(e)}"
        )


@router.get("/data-stats")
async def get_data_stats():
    """
    Get statistics about loaded data

    Returns counts of:
    - Pokémon
    - Moves
    - Seasonal tiers
    - Raid counters
    - PvP rankings
    """
    loader = get_data_loader()

    return {
        "pokemon_count": len(loader.pokemon_base),
        "moves_count": len(loader.moves),
        "pokemon_moves_count": len(loader.pokemon_moves),
        "seasonal_tiers_count": len(loader.seasonal_tiers),
        "raid_counters_count": len(loader.raid_counters),
        "pvp_rankings_count": len(loader.pvp_party_rankings),
        "current_season": loader.get_current_season()
    }


class CrawlNowResponse(BaseModel):
    status: str
    message: str
    new_events_count: int
    new_events: List[Dict]
    email_sent: bool


@router.post("/crawl-now", response_model=CrawlNowResponse)
async def manual_crawl_now():
    """
    Manual trigger for event crawling and email notification

    수동으로 이벤트 크롤링 + 이메일 발송을 즉시 실행합니다.
    스케줄과 무관하게 즉시 실행되며, 테스트용으로 사용할 수 있습니다.

    동작:
    1. 포켓몬GO 공식 한국어 페이지 크롤링
    2. 신규 이벤트 확인 (DB와 비교)
    3. 신규 이벤트가 있으면 treehi1@gmail.com으로 이메일 발송

    Returns:
    - status: "success" 또는 "error"
    - message: 결과 메시지
    - new_events_count: 신규 이벤트 개수
    - new_events: 신규 이벤트 리스트
    - email_sent: 이메일 발송 여부
    """
    logger.info("🔧 Manual crawl triggered via /api/admin/crawl-now")

    db = SessionLocal()
    new_events = []
    email_sent = False

    try:
        # 1. 이벤트 크롤링
        logger.info("📡 Crawling Pokemon GO official Korean news page...")
        events = await crawler.fetch_events()
        logger.info(f"✅ Found {len(events)} total events from website")

        # 2. 신규 이벤트 확인 및 DB 저장
        for event_data in events:
            existing_event = db.query(Event).filter(Event.url == event_data['url']).first()

            if not existing_event:
                # 신규 이벤트 발견
                new_event = Event(
                    title=event_data['title'],
                    url=event_data['url'],
                    summary=event_data.get('summary'),
                    published_date=event_data.get('published_date'),
                    image_url=event_data.get('image_url'),
                    category=event_data.get('category', '뉴스')
                )
                db.add(new_event)
                new_events.append(event_data)
                logger.info(f"🆕 New event found: {event_data['title']}")

        db.commit()

        # 3. 이메일 발송 (신규 이벤트가 있을 때만)
        if new_events:
            logger.info(f"📧 Sending email for {len(new_events)} new events...")
            email_sent = email_service.send_daily_news_summary(new_events, None)

            if email_sent:
                logger.info("✅ Email sent successfully")
            else:
                logger.warning("⚠️ Email sending failed")
        else:
            logger.info("📭 No new events to email")

        return CrawlNowResponse(
            status="success",
            message=f"Crawled {len(events)} events. Found {len(new_events)} new events.",
            new_events_count=len(new_events),
            new_events=new_events,
            email_sent=email_sent
        )

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Manual crawl failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        return CrawlNowResponse(
            status="error",
            message=f"Crawl failed: {str(e)}",
            new_events_count=0,
            new_events=[],
            email_sent=False
        )

    finally:
        db.close()


@router.get("/scheduler-status")
async def get_scheduler_status():
    """
    스케줄러 상태 확인 API

    스케줄러가 정상적으로 실행 중인지 확인합니다.
    """
    from app.scheduler import get_scheduler_status

    try:
        status = get_scheduler_status()
        return {
            "status": "success",
            "scheduler": status
        }
    except Exception as e:
        logger.error(f"❌ Failed to get scheduler status: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
