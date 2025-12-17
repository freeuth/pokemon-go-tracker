#!/usr/bin/env python3
"""
Migration script to add event_start_date and event_end_date columns to events table

Run this on Render server via: python migrate_add_event_dates.py
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Add event_start_date and event_end_date columns if they don't exist"""

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        try:
            # Check if columns exist
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='events'
                AND column_name IN ('event_start_date', 'event_end_date');
            """))
            existing_columns = [row[0] for row in result]

            if 'event_start_date' not in existing_columns:
                logger.info("Adding event_start_date column...")
                conn.execute(text("""
                    ALTER TABLE events
                    ADD COLUMN event_start_date TIMESTAMP WITH TIME ZONE;
                """))
                conn.commit()
                logger.info("✅ event_start_date column added")
            else:
                logger.info("✓ event_start_date column already exists")

            if 'event_end_date' not in existing_columns:
                logger.info("Adding event_end_date column...")
                conn.execute(text("""
                    ALTER TABLE events
                    ADD COLUMN event_end_date TIMESTAMP WITH TIME ZONE;
                """))
                conn.commit()
                logger.info("✅ event_end_date column added")
            else:
                logger.info("✓ event_end_date column already exists")

            logger.info("🎉 Migration completed successfully!")

        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
