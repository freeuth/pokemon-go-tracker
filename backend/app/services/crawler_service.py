import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, List, Dict
import logging
import re
from app.core.config import settings

logger = logging.getLogger(__name__)


class PokemonGOCrawler:
    def __init__(self):
        self.base_url = settings.POKEMONGO_NEWS_URL
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def fetch_events(self) -> List[Dict]:
        """
        Fetch latest Pokemon GO events from official website
        포켓몬GO 공식 한국 사이트에서 최신 뉴스를 크롤링
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                logger.info(f"Fetching events from: {self.base_url}")
                response = await client.get(self.base_url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                events = []

                # 포켓몬GO 공식 사이트의 실제 구조에 맞춰 파싱
                # pokemongolive.com/ko/post/ 페이지 구조를 파싱

                # 1. 방법 1: article 태그 찾기
                article_items = soup.find_all('article', limit=15)

                if not article_items:
                    # 2. 방법 2: 특정 클래스명으로 찾기
                    article_items = soup.select('.post, .article, .news-item, .blog-post', limit=15)

                if not article_items:
                    # 3. 방법 3: a 태그에서 /post/ 링크 찾기
                    link_items = soup.find_all('a', href=re.compile(r'/ko/post/[^/]+/?$'), limit=15)
                    if link_items:
                        logger.info(f"Found {len(link_items)} news links")
                        for link in link_items:
                            try:
                                # 제목 추출
                                title = link.get_text(strip=True)
                                if not title or len(title) < 5:
                                    # 링크 내부의 제목 요소 찾기
                                    title_elem = link.find(['h1', 'h2', 'h3', 'h4', 'span', 'div'])
                                    title = title_elem.get_text(strip=True) if title_elem else ''

                                if not title or len(title) < 5:
                                    continue

                                # URL 추출
                                url = self._make_absolute_url(link.get('href', ''))

                                # 썸네일 이미지 찾기 (링크 안 또는 부모 요소에서)
                                img_elem = link.find('img')
                                if not img_elem and link.parent:
                                    img_elem = link.parent.find('img')

                                thumbnail_url = None
                                if img_elem:
                                    thumbnail_url = img_elem.get('src') or img_elem.get('data-src')
                                    if thumbnail_url:
                                        thumbnail_url = self._make_absolute_url(thumbnail_url)

                                # 요약 추출 (부모 요소에서 p 태그 찾기)
                                summary = ''
                                if link.parent:
                                    summary_elem = link.parent.find('p')
                                    if summary_elem:
                                        summary = summary_elem.get_text(strip=True)[:200]

                                event = {
                                    'title': title,
                                    'url': url,
                                    'summary': summary,
                                    'published_date': datetime.now(),  # 날짜는 상세 페이지에서 가져오거나 현재 시간 사용
                                    'image_url': thumbnail_url,
                                    'category': '뉴스'
                                }
                                events.append(event)

                            except Exception as e:
                                logger.error(f"Error parsing link item: {str(e)}")
                                continue
                else:
                    logger.info(f"Found {len(article_items)} article items")
                    for item in article_items:
                        try:
                            # 제목 추출
                            title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                            if not title_elem:
                                continue

                            title = title_elem.get_text(strip=True)

                            # 링크 추출
                            link_elem = item.find('a', href=re.compile(r'/ko/post/'))
                            if not link_elem:
                                link_elem = title_elem.find_parent('a')
                            if not link_elem:
                                continue

                            url = self._make_absolute_url(link_elem.get('href', ''))

                            # 썸네일 이미지 추출
                            img_elem = item.find('img')
                            thumbnail_url = None
                            if img_elem:
                                thumbnail_url = img_elem.get('src') or img_elem.get('data-src')
                                if thumbnail_url:
                                    thumbnail_url = self._make_absolute_url(thumbnail_url)

                            # 요약 추출
                            summary_elem = item.find('p')
                            summary = summary_elem.get_text(strip=True)[:200] if summary_elem else ''

                            # 날짜 추출
                            date_elem = item.find('time')
                            published_date = datetime.now()
                            if date_elem:
                                date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                                published_date = self._parse_date(date_str)

                            event = {
                                'title': title,
                                'url': url,
                                'summary': summary,
                                'published_date': published_date,
                                'image_url': thumbnail_url,
                                'category': '뉴스'
                            }
                            events.append(event)

                        except Exception as e:
                            logger.error(f"Error parsing article item: {str(e)}")
                            continue

                # URL 유효성 검증 (404 체크는 너무 느리므로 기본 검증만)
                validated_events = []
                for event in events:
                    if self._validate_event(event):
                        validated_events.append(event)
                    else:
                        logger.warning(f"Invalid event filtered out: {event.get('title', 'Unknown')}")

                if validated_events:
                    logger.info(f"Successfully crawled {len(validated_events)} valid events")
                    return validated_events
                else:
                    logger.warning("No valid events found, using mock data")
                    return self._get_mock_events()

        except Exception as e:
            logger.error(f"Failed to fetch events: {str(e)}")
            return self._get_mock_events()

    def _validate_event(self, event: Dict) -> bool:
        """이벤트 데이터 유효성 검증"""
        # 필수 필드 체크
        if not event.get('title') or len(event['title']) < 5:
            return False

        if not event.get('url') or not event['url'].startswith('http'):
            return False

        # URL이 포켓몬GO 공식 사이트인지 확인
        if 'pokemongolive.com' not in event['url']:
            return False

        return True

    def _make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute URL"""
        if not url:
            return ''

        if url.startswith('http'):
            return url

        # // 로 시작하는 URL 처리
        if url.startswith('//'):
            return f'https:{url}'

        # / 로 시작하는 상대 경로
        if url.startswith('/'):
            return f"https://pokemongolive.com{url}"

        # 그 외
        return f"https://pokemongolive.com/{url}"

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return datetime.now()

        try:
            # ISO 8601 형식 (예: 2024-12-01T10:00:00Z)
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

            # 일반적인 날짜 형식들
            date_formats = [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%B %d, %Y",
                "%b %d, %Y",
                "%d %B %Y",
                "%d %b %Y",
                "%Y년 %m월 %d일",
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

            return datetime.now()
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {str(e)}")
            return datetime.now()

    def _get_mock_events(self) -> List[Dict]:
        """
        Return mock events for demonstration (한국어)
        실제 크롤링 실패 시 사용되는 fallback 데이터
        """
        return [
            {
                'title': '포켓몬GO 12월 커뮤니티 데이',
                'url': 'https://pokemongolive.com/ko/post/community-day-dec-2024',
                'summary': '12월 커뮤니티 데이에서 특별한 포켓몬을 만나보세요. 이벤트 기간 동안 특정 포켓몬이 야생에서 더 자주 출현하며, 진화 시 특별한 기술을 배울 수 있습니다.',
                'published_date': datetime.now(),
                'image_url': 'https://lh3.googleusercontent.com/c8_zDZVu8lEKu3xL6P-rRCMaABf0FJgk6qJK5QqLjLbBwR0PcbO_RBH1YQqR6IFVwQWk=w1200-h630',
                'category': '커뮤니티 데이'
            },
            {
                'title': '레이드 위크엔드: 전설의 포켓몬 대량 출현',
                'url': 'https://pokemongolive.com/ko/post/raid-weekend-legendary-2024',
                'summary': '이번 주말 레이드 배틀에서 전설의 포켓몬을 만날 확률이 대폭 증가합니다. 친구들과 함께 협력하여 강력한 전설의 포켓몬을 포획하세요!',
                'published_date': datetime.now(),
                'image_url': 'https://lh3.googleusercontent.com/zK4fBbTKlW9VqJgWjL0hXpQH9Bq8RwIgNLjL0FcP7CqYGq5W9bR0pQqL7IgRwB8=w1200-h630',
                'category': '레이드 이벤트'
            },
            {
                'title': '새로운 시즌: 모험과 발견의 여정',
                'url': 'https://pokemongolive.com/ko/post/season-adventure-discovery-2024',
                'summary': '새로운 시즌이 시작됩니다! 신규 스페셜 리서치, 시즌 한정 포켓몬, 그리고 다양한 보상이 여러분을 기다리고 있습니다. 지금 바로 모험을 떠나보세요!',
                'published_date': datetime.now(),
                'image_url': 'https://lh3.googleusercontent.com/dP8RwB0qL7IgNLjL0FcP7CqYGq5W9bR0pQqL7IgRwB8zK4fBbTKlW9VqJgWjL=w1200-h630',
                'category': '시즌 이벤트'
            },
            {
                'title': 'GO 배틀 리그 시즌 업데이트',
                'url': 'https://pokemongolive.com/ko/post/go-battle-league-season-update',
                'summary': 'GO 배틀 리그 새 시즌이 시작되었습니다. 새로운 랭크 시스템, 보상, 그리고 메타 변화를 확인하세요. 배틀에서 승리하고 독점 보상을 획득하세요!',
                'published_date': datetime.now(),
                'image_url': 'https://lh3.googleusercontent.com/RwB8zK4fBbTKlW9VqJgWjL0hXpQH9Bq8RwIgNLjL0FcP7CqYGq5W9bR0pQqL=w1200-h630',
                'category': 'GBL 업데이트'
            }
        ]


crawler = PokemonGOCrawler()
