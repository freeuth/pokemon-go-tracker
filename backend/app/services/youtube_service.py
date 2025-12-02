import httpx
import feedparser
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging
import re
from app.core.config import settings

logger = logging.getLogger(__name__)


class YouTubeRSSService:
    """
    YouTube RSS Feed를 사용하여 영상 정보를 수집하는 서비스
    YouTube Data API 없이 무료로 사용 가능
    """

    def __init__(self):
        self.rss_feeds = self._parse_rss_feeds()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def _parse_rss_feeds(self) -> List[str]:
        """환경변수에서 RSS 피드 URL 목록 파싱"""
        if not settings.YOUTUBE_RSS_FEEDS:
            return []

        # 쉼표로 구분된 URL들을 파싱
        feeds = [feed.strip() for feed in settings.YOUTUBE_RSS_FEEDS.split(',')]
        return [feed for feed in feeds if feed]

    async def fetch_latest_videos(self, max_results: int = 50) -> List[Dict]:
        """
        모든 RSS 피드에서 최신 영상 수집

        Args:
            max_results: 각 피드당 최대 수집 개수

        Returns:
            영상 정보 딕셔너리 리스트
        """
        all_videos = []

        if not self.rss_feeds:
            logger.warning("No RSS feeds configured, returning empty list")
            return []

        for feed_url in self.rss_feeds:
            try:
                videos = await self._fetch_feed(feed_url, max_results)
                all_videos.extend(videos)
                logger.info(f"Fetched {len(videos)} videos from {feed_url}")
            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {str(e)}")
                continue

        # 게시 날짜 기준으로 정렬 (최신순)
        all_videos.sort(key=lambda x: x.get('published_at', datetime.min), reverse=True)

        logger.info(f"Total videos fetched: {len(all_videos)}")
        return all_videos[:max_results]

    async def _fetch_feed(self, feed_url: str, max_results: int) -> List[Dict]:
        """
        단일 RSS 피드에서 영상 정보 추출

        Args:
            feed_url: YouTube RSS 피드 URL
            max_results: 최대 수집 개수

        Returns:
            영상 정보 딕셔너리 리스트
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(feed_url, headers=self.headers)
                response.raise_for_status()

            # feedparser로 RSS 파싱
            feed = feedparser.parse(response.text)

            videos = []
            two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)

            for entry in feed.entries[:max_results]:
                try:
                    video_data = self._parse_entry(entry)
                    if video_data:
                        # 최근 2주일 영상만 수집
                        published_at = video_data.get('published_at')
                        if published_at and published_at >= two_weeks_ago:
                            videos.append(video_data)
                except Exception as e:
                    logger.error(f"Error parsing entry: {str(e)}")
                    continue

            return videos

        except Exception as e:
            logger.error(f"Failed to fetch RSS feed: {str(e)}")
            return []

    def _parse_entry(self, entry) -> Optional[Dict]:
        """
        RSS 엔트리에서 영상 정보 추출

        YouTube RSS 피드 구조:
        - entry.id: yt:video:VIDEO_ID
        - entry.title: 영상 제목
        - entry.published: 게시 날짜
        - entry.author: 채널 이름
        - entry.media_thumbnail: 썸네일 (feedparser가 파싱)
        """
        try:
            # video_id 추출 (yt:video:VIDEO_ID 형식)
            video_id = entry.id.split(':')[-1] if hasattr(entry, 'id') else None
            if not video_id:
                return None

            # 제목
            title = entry.title if hasattr(entry, 'title') else ''

            # 채널 이름
            channel_name = ''
            if hasattr(entry, 'author_detail'):
                channel_name = entry.author_detail.get('name', '')
            elif hasattr(entry, 'author'):
                channel_name = entry.author

            # 설명 (요약)
            description = ''
            if hasattr(entry, 'summary'):
                description = entry.summary
            elif hasattr(entry, 'description'):
                description = entry.description

            # HTML 태그 제거
            description = re.sub(r'<[^>]+>', '', description)[:500]

            # 게시 날짜
            published_at = datetime.now(timezone.utc)
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except:
                    pass

            # 채널 ID 추출 (link에서)
            channel_id = None
            if hasattr(entry, 'author_detail') and 'href' in entry.author_detail:
                # href 형식: http://www.youtube.com/channel/CHANNEL_ID
                match = re.search(r'/channel/([^/]+)', entry.author_detail['href'])
                if match:
                    channel_id = match.group(1)

            # YouTube URL 생성
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # 썸네일 URL 생성 (YouTube 썸네일 규칙 사용)
            thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

            # 조회수는 RSS에 없으므로 0으로 설정
            view_count = 0

            # 태그 생성 (제목에서 키워드 추출)
            tags = self._extract_tags(title, description)

            return {
                'video_id': video_id,
                'title': title,
                'channel_name': channel_name,
                'channel_id': channel_id,
                'description': description,
                'published_at': published_at,
                'video_url': video_url,
                'thumbnail_url': thumbnail_url,
                'view_count': view_count,
                'tags': tags
            }

        except Exception as e:
            logger.error(f"Error parsing RSS entry: {str(e)}")
            return None

    def _extract_tags(self, title: str, description: str) -> List[str]:
        """
        제목과 설명에서 태그 추출

        포켓몬GO 배틀 관련 키워드 감지
        """
        tags = []
        text = f"{title} {description}".lower()

        # 배틀 리그 태그
        if 'great league' in text or 'gl' in text:
            tags.append('Great League')
        if 'ultra league' in text or 'ul' in text:
            tags.append('Ultra League')
        if 'master league' in text or 'ml' in text:
            tags.append('Master League')
        if 'go battle league' in text or 'gbl' in text:
            tags.append('GO Battle League')

        # 일반 태그
        if 'pvp' in text:
            tags.append('PvP')
        if 'raid' in text:
            tags.append('Raid')
        if 'shadow' in text:
            tags.append('Shadow')
        if 'mega' in text:
            tags.append('Mega')
        if 'tournament' in text:
            tags.append('Tournament')
        if 'guide' in text or 'tutorial' in text:
            tags.append('Guide')
        if 'team' in text:
            tags.append('Team Building')

        # 한국어 키워드
        if '배틀' in text or '대전' in text:
            tags.append('Battle')
        if '가이드' in text or '공략' in text:
            tags.append('Guide')
        if '리그' in text:
            tags.append('League')

        return list(set(tags))  # 중복 제거


youtube_service = YouTubeRSSService()
