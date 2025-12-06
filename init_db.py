"""
Database initialization script
Run this to set up the database for YiriAi
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, engine
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_database():
    """Initialize database tables"""
    try:
        logger.info(f"Connecting to database: {settings.database_url}")
        
        # Create tables
        await init_db()
        logger.info("✓ Database tables created successfully")
        
        # Verify tables
        async with engine.begin() as conn:
            from sqlalchemy import text
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            )
            tables = [row[0] for row in result]
            
            logger.info(f"✓ Created tables: {', '.join(tables)}")
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(initialize_database())
