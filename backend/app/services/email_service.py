import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Gmail SMTP를 사용한 이메일 서비스
    """

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM

    def send_daily_news_summary(self, events: List[dict], recipients: List[str]):
        """
        Send daily news summary email with all new events
        매일 오전 10시에 새 뉴스가 있을 때만 발송
        """
        if not events:
            logger.info("No new events to send")
            return False

        if recipients is None or len(recipients) == 0:
            logger.warning("No recipients specified")
            return False

        from datetime import datetime
        today = datetime.now().strftime('%Y년 %m월 %d일')

        subject = f"[포켓몬GO] {today} 신규 뉴스 요약 ({len(events)}건)"

        # 이벤트 목록을 HTML로 변환
        events_html = ""
        for idx, event in enumerate(events, 1):
            events_html += f"""
            <div style="margin-bottom: 30px; padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="color: #EE1515; margin-top: 0;">{idx}. {event['title']}</h3>
                <p style="color: #666; line-height: 1.6; margin: 10px 0;">
                    {event.get('summary', '요약 정보가 없습니다.')}
                </p>
                <p style="margin: 10px 0;">
                    <strong style="color: #333;">카테고리:</strong>
                    <span style="background-color: #EE1515; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                        {event.get('category', '뉴스')}
                    </span>
                </p>
                <a href="{event['url']}" style="
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #EE1515;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 10px;
                ">전체 기사 보기 →</a>
            </div>
            """

        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', Arial, sans-serif;
                    max-width: 700px;
                    margin: 0 auto;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #EE1515 0%, #FF6B6B 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    padding: 30px 20px;
                    background-color: #f9f9f9;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #999;
                    font-size: 12px;
                    background-color: #333;
                    color: white;
                    border-radius: 0 0 8px 8px;
                }}
                .summary-box {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">🎮 포켓몬GO 뉴스 알림</h1>
                <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">{today}</p>
            </div>
            <div class="content">
                <div class="summary-box">
                    <strong>📌 오늘의 신규 뉴스:</strong> 총 <strong>{len(events)}건</strong>의 새로운 소식이 있습니다!
                </div>

                {events_html}

                <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #e3f2fd; border-radius: 8px;">
                    <p style="margin: 0 0 15px 0; color: #1976d2; font-weight: bold;">
                        더 많은 포켓몬GO 정보를 확인하세요!
                    </p>
                    <a href="{settings.FRONTEND_URL}" style="
                        display: inline-block;
                        padding: 12px 30px;
                        background-color: #1976d2;
                        color: white;
                        text-decoration: none;
                        border-radius: 25px;
                        font-weight: bold;
                    ">Pokemon GO Tracker 바로가기</a>
                </div>
            </div>
            <div class="footer">
                <p style="margin: 5px 0;">포켓몬GO 이벤트 & 배틀 영상 트래커</p>
                <p style="margin: 5px 0; font-size: 11px; opacity: 0.7;">
                    이 이메일은 매일 오전 10시에 새로운 뉴스가 있을 때만 발송됩니다.
                </p>
            </div>
        </body>
        </html>
        """

        try:
            for recipient in recipients:
                # MODE가 test일 때는 실제로 발송하지 않고 로그만 출력
                if settings.MODE == 'test':
                    logger.info(f"[TEST MODE] Would send email to {recipient}")
                    logger.info(f"Subject: {subject}")
                    logger.info(f"Events count: {len(events)}")
                else:
                    # Gmail SMTP로 실제 발송
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = self.from_email
                    msg['To'] = recipient

                    # HTML 파트 추가
                    html_part = MIMEText(html_content, 'html', 'utf-8')
                    msg.attach(html_part)

                    # SMTP 연결 및 발송
                    with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                        server.starttls()  # TLS 시작
                        server.login(self.smtp_user, self.smtp_password)
                        server.send_message(msg)

                    logger.info(f"Email sent successfully to {recipient}")

            return True

        except Exception as e:
            logger.error(f"Failed to send daily news summary: {str(e)}")
            return False


email_service = EmailService()
