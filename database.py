"""
Database models and ORM setup
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Index
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Optional

from config import settings

Base = declarative_base()


class CourseCache(Base):
    """Cache for course data from PAWS"""
    __tablename__ = "course_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    crn = Column(String(10), nullable=False, index=True)
    term = Column(String(10), nullable=False, index=True)
    subject = Column(String(10), nullable=False, index=True)
    course_number = Column(String(10), nullable=False)
    section = Column(String(10))
    title = Column(String(200))
    credits = Column(Integer)
    professor = Column(String(100), index=True)
    days = Column(JSON)  # List of days
    time_start = Column(String(10))
    time_end = Column(String(10))
    location = Column(String(100))
    seats_available = Column(Integer)
    total_seats = Column(Integer)
    waitlist_available = Column(Integer, default=0)
    delivery_method = Column(String(20))
    
    # Metadata
    raw_data = Column(JSON)  # Store complete raw data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_term_subject', 'term', 'subject'),
        Index('idx_term_crn', 'term', 'crn'),
        Index('idx_subject_course', 'subject', 'course_number'),
    )


class ProfessorCache(Base):
    """Cache for professor ratings from RateMyProfessors"""
    __tablename__ = "professor_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    professor_name = Column(String(100), nullable=False, index=True)
    school_id = Column(String(50), nullable=False)
    rmp_id = Column(String(50))
    
    # Rating data
    avg_rating = Column(Float)
    avg_difficulty = Column(Float)
    would_take_again_percent = Column(Float)
    num_ratings = Column(Integer)
    department = Column(String(100))
    
    # Additional data
    tags = Column(JSON)  # Common tags from RMP
    raw_data = Column(JSON)  # Store complete response
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Ensure unique professor per school
    __table_args__ = (
        Index('idx_prof_school', 'professor_name', 'school_id', unique=True),
    )


class ScraperLog(Base):
    """Log scraping operations for monitoring and debugging"""
    __tablename__ = "scraper_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # 'paws' or 'rmp'
    operation = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, index=True)  # 'success', 'error', 'timeout'
    
    # Request details
    term = Column(String(10))
    subject = Column(String(10))
    query_params = Column(JSON)
    
    # Response details
    items_found = Column(Integer, default=0)
    duration_ms = Column(Integer)
    error_message = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# Database engine and session
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before using
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Dependency for getting database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
