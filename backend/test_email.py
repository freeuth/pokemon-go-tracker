#!/usr/bin/env python3
"""
테스트 이메일 발송 스크립트
최신 이벤트 1개를 가져와서 이메일로 발송합니다.
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.event import Event
from app.services.email_service import email_service
from sqlalchemy import desc


def send_test_email():
    """최신 이벤트 1개를 테스트 이메일로 발송"""
    db = SessionLocal()

    try:
        # 가장 최신 이벤트 1개 가져오기
        latest_event = db.query(Event).order_by(desc(Event.published_date)).first()

        if not latest_event:
            print("❌ 데이터베이스에 이벤트가 없습니다.")
            return

        # 이벤트 데이터를 딕셔너리로 변환
        event_data = {
            'title': latest_event.title,
            'url': latest_event.url,
            'summary': latest_event.summary,
            'category': latest_event.category,
            'published_date': latest_event.published_date
        }

        print(f"📧 테스트 이메일 발송 중...")
        print(f"제목: {event_data['title']}")
        print(f"카테고리: {event_data['category']}")
        print(f"수신자: treehi1@gmail.com")
        print()

        # 이메일 발송
        result = email_service.send_daily_news_summary(
            events=[event_data],
            recipients=['treehi1@gmail.com']
        )

        if result:
            print("✅ 테스트 이메일이 성공적으로 발송되었습니다!")
            print("📬 treehi1@gmail.com 메일함을 확인해주세요.")
        else:
            print("❌ 이메일 발송에 실패했습니다.")
            print("⚠️  SENDGRID_API_KEY가 올바르게 설정되어 있는지 확인해주세요.")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 포켓몬GO 이벤트 이메일 테스트")
    print("=" * 60)
    print()

    send_test_email()

    print()
    print("=" * 60)
