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
        포켓몬GO 공식 한국 사이트(pokemongo.com/ko/news)에서 최신 뉴스를 크롤링
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                logger.info(f"Fetching events from: {self.base_url}")
                response = await client.get(self.base_url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                events = []

                # pokemongo.com/ko/news 페이지 구조에 맞춰 파싱
                # 구조: <a href="/ko/news/[slug]"><img src="...">제목 텍스트</a>

                # /ko/news/로 시작하는 모든 링크 찾기
                link_items = soup.find_all('a', href=re.compile(r'^/ko/news/[^/]+$'))

                if link_items:
                    logger.info(f"Found {len(link_items)} news links from pokemongo.com")

                    for link in link_items:
                        try:
                            # URL 추출
                            href = link.get('href', '')
                            if not href:
                                continue

                            # 절대 URL로 변환
                            url = f"https://pokemongo.com{href}"

                            # 제목 추출 - 링크의 텍스트에서 가져오기
                            title = link.get_text(strip=True)

                            # 제목이 없거나 너무 짧으면 스킵
                            if not title or len(title) < 5:
                                continue

                            # URL과 제목에서 날짜 추출
                            published_date = self._extract_date_from_url_and_title(href, title)

                            # 썸네일 이미지 찾기
                            img_elem = link.find('img')
                            thumbnail_url = None
                            if img_elem:
                                thumbnail_url = img_elem.get('src', '')
                                # Googleusercontent URL 처리
                                if thumbnail_url and not thumbnail_url.startswith('http'):
                                    if thumbnail_url.startswith('//'):
                                        thumbnail_url = f'https:{thumbnail_url}'
                                    else:
                                        thumbnail_url = f'https://pokemongo.com{thumbnail_url}'

                            event = {
                                'title': title,
                                'url': url,
                                'summary': '',  # pokemongo.com은 요약을 제공하지 않음
                                'published_date': published_date,
                                'image_url': thumbnail_url,
                                'category': '뉴스'
                            }
                            events.append(event)

                        except Exception as e:
                            logger.error(f"Error parsing link item: {str(e)}")
                            continue

                    if events:
                        logger.info(f"Successfully crawled {len(events)} events from pokemongo.com")
                        return events
                    else:
                        logger.warning("No valid events parsed from pokemongo.com")
                        return []
                else:
                    logger.warning("No news links found on pokemongo.com/ko/news")
                    return []

        except Exception as e:
            logger.error(f"Failed to fetch events from pokemongo.com: {str(e)}")
            logger.error(f"Error traceback: {e.__class__.__name__}")
            return []

    def _extract_date_from_url_and_title(self, url: str, title: str) -> datetime:
        """
        URL과 제목에서 날짜 정보를 추출

        URL 패턴:
        - /ko/news/event-name-2025 → 2025년
        - /ko/news/communityday-january-2026 → 2026년 1월

        제목 패턴:
        - "2026년 1월 커뮤니티 데이" → 2026년 1월
        - "12월 커뮤니티 데이" → 현재년도 12월
        """
        import re
        from datetime import datetime

        year = None
        month = None

        # 1. URL에서 연도 추출 (마지막 4자리 숫자)
        url_year_match = re.search(r'-(\d{4})(?:\D|$)', url)
        if url_year_match:
            year_candidate = int(url_year_match.group(1))
            if 2020 <= year_candidate <= 2030:
                year = year_candidate

        # 2. URL에서 월 이름 추출 (영어)
        month_names = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }

        url_lower = url.lower()
        for month_name, month_num in month_names.items():
            if month_name in url_lower:
                month = month_num
                break

        # 3. 제목에서 연도와 월 추출 (한국어)
        # "2026년 1월" 또는 "2026년"
        title_year_month = re.search(r'(\d{4})년\s*(\d{1,2})월', title)
        if title_year_month:
            year = int(title_year_month.group(1))
            month = int(title_year_month.group(2))
        elif re.search(r'(\d{4})년', title):
            year_match = re.search(r'(\d{4})년', title)
            year = int(year_match.group(1))

        # 4. 제목에서 월만 추출 (연도 없이)
        if not month:
            month_only = re.search(r'(\d{1,2})월', title)
            if month_only:
                month = int(month_only.group(1))

        # 5. 날짜 생성
        if year and month:
            try:
                return datetime(year, month, 1)
            except ValueError:
                pass

        if year:
            try:
                return datetime(year, 1, 1)  # 연도만 있으면 1월 1일로
            except ValueError:
                pass

        # 날짜를 추출할 수 없으면 현재 날짜 반환
        return datetime.now()

    def _validate_event(self, event: Dict) -> bool:
        """이벤트 데이터 유효성 검증"""
        # 필수 필드 체크
        if not event.get('title') or len(event['title']) < 5:
            return False

        if not event.get('url') or not event['url'].startswith('http'):
            return False

        # URL이 포켓몬GO 공식 사이트인지 확인
        if 'pokemongo.com' not in event['url']:
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
            return f"https://pokemongo.com{url}"

        # 그 외
        return f"https://pokemongo.com/{url}"

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
