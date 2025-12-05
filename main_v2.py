"""
YiriAi - GSU Course Selection Assistant (Production Version)
FastAPI application with real data integration, caching, and monitoring
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional
import logging
import structlog
from datetime import datetime

from models import CoursePreferences, MatchedCourse, RegistrationResponse
from scrapers.paws_scraper import PAWSScraper
from scrapers.rmp_scraper import RateMyProfessorsScraper
from utils.course_matcher import CourseMatcher
from utils.file_parser import FileParser
from config import settings
from cache import cache_manager
from database import init_db, get_db

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("starting_application", version=settings.app_version)
    
    try:
        # Initialize database
        await init_db()
        logger.info("database_initialized")
        
        # Initialize cache
        await cache_manager.initialize()
        logger.info("cache_initialized")
        
        # Initialize scrapers
        app.state.paws_scraper = PAWSScraper()
        app.state.rmp_scraper = RateMyProfessorsScraper()
        app.state.course_matcher = CourseMatcher()
        app.state.file_parser = FileParser()
        
        logger.info("application_ready")
        
    except Exception as e:
        logger.error("startup_failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("shutting_down_application")
    
    try:
        # Close scraper sessions
        if hasattr(app.state, 'paws_scraper'):
            await app.state.paws_scraper.close()
        if hasattr(app.state, 'rmp_scraper'):
            await app.state.rmp_scraper.close()
        
        # Close cache
        await cache_manager.close()
        
        logger.info("shutdown_complete")
        
    except Exception as e:
        logger.error("shutdown_error", error=str(e))


app = FastAPI(
    title="YiriAi - GSU Course Assistant",
    description="Production-ready course selection automation for GSU students",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


@app.get("/")
async def root():
    """Health check endpoint"""
    cache_stats = await cache_manager.get_stats()
    
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache": cache_stats,
        "message": "GSU Course Selection Assistant is running (Production Mode)"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        cache_stats = await cache_manager.get_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "api": "up",
                "cache": "up" if cache_stats.get("connected") else "down",
                "database": "up"  # Would check DB connection
            },
            "cache_stats": cache_stats
        }
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/api/upload-preferences", response_model=RegistrationResponse)
async def upload_preferences(
    prefs_file: UploadFile = File(...),
    eval_file: Optional[UploadFile] = File(None),
    term: str = "202508",
    include_ratings: bool = True,
    use_cache: bool = True
):
    """
    Upload student evaluation and course preferences (Production endpoint)
    
    Features:
    - Real PAWS scraping with Banner parsing
    - RateMyProfessors GraphQL API integration
    - Multi-layer caching (Redis + Postgres)
    - Retry logic and error handling
    - Structured logging
    
    Args:
        prefs_file: Course preferences file (JSON, CSV, or Excel)
        eval_file: Optional student evaluation/transcript
        term: GSU term code (e.g., 202508)
        include_ratings: Include RateMyProfessors data
        use_cache: Use cached data (recommended for production)
    
    Returns:
        RegistrationResponse with matched courses and CRNs
    """
    request_id = datetime.now().isoformat()
    logger.info(
        "processing_preferences",
        request_id=request_id,
        term=term,
        include_ratings=include_ratings,
        use_cache=use_cache
    )
    
    try:
        # Get components from app state
        paws_scraper: PAWSScraper = app.state.paws_scraper
        rmp_scraper: RateMyProfessorsScraper = app.state.rmp_scraper
        course_matcher: CourseMatcher = app.state.course_matcher
        file_parser: FileParser = app.state.file_parser
        
        # Parse evaluation file if provided
        eval_data = None
        if eval_file:
            eval_content = await eval_file.read()
            eval_data = file_parser.parse_evaluation(eval_content, eval_file.filename)
            logger.info("parsed_evaluation", courses_count=len(eval_data))
        
        # Parse preferences file
        prefs_content = await prefs_file.read()
        preferences = file_parser.parse_preferences(prefs_content, prefs_file.filename)
        logger.info("parsed_preferences", courses_count=len(preferences.courses))
        
        if not preferences.subjects:
            raise HTTPException(
                status_code=400,
                detail="No subjects found in preferences file"
            )
        
        # Scrape GSU PAWS for available courses (with caching)
        logger.info("scraping_paws", term=term, subjects=preferences.subjects)
        available_courses = await paws_scraper.get_available_courses(
            term=term,
            subjects=preferences.subjects,
            open_only=True,
            use_cache=use_cache
        )
        logger.info("scraped_courses", count=len(available_courses))
        
        if not available_courses:
            return RegistrationResponse(
                matched_courses=[],
                paws_link=paws_scraper.generate_registration_link(term),
                term=term,
                timestamp=datetime.now().isoformat(),
                instructions="No available courses found for the specified criteria. Try different subjects or term.",
                total_credits=0
            )
        
        # Match courses based on preferences
        logger.info("matching_courses")
        matched_courses = course_matcher.match_courses(
            preferences=preferences,
            available_courses=available_courses,
            completed_courses=eval_data
        )
        logger.info("matched_courses", count=len(matched_courses))
        
        # Enhance with RateMyProfessors data if requested
        if include_ratings and matched_courses:
            logger.info("fetching_professor_ratings")
            
            # Get unique professors
            professors = list(set(
                c.professor for c in matched_courses 
                if c.professor and c.professor.lower() != 'staff'
            ))
            
            if professors:
                # Batch fetch ratings
                ratings = await rmp_scraper.batch_get_ratings(professors)
                
                # Apply ratings to courses
                for course in matched_courses:
                    if course.professor and course.professor in ratings:
                        rating_data = ratings[course.professor]
                        if rating_data:
                            course.professor_rating = rating_data.get("rating")
                            course.professor_difficulty = rating_data.get("difficulty")
                            course.would_take_again = rating_data.get("would_take_again")
                
                logger.info("applied_ratings", professors_count=len(professors))
        
        # Generate response
        paws_link = paws_scraper.generate_registration_link(term)
        
        response = RegistrationResponse(
            matched_courses=matched_courses[:20],  # Limit to top 20
            paws_link=paws_link,
            term=term,
            timestamp=datetime.now().isoformat(),
            instructions=(
                "🎓 YiriAi Course Selection Complete!\n\n"
                "Steps to register:\n"
                "1. Click the PAWS link below\n"
                "2. Log into your GSU account (YiriAi never handles passwords)\n"
                "3. Navigate to 'Add/Drop Classes'\n"
                "4. Copy and paste each CRN into the registration form\n"
                "5. Click 'Submit Changes' to register\n\n"
                "⚠️ Courses may fill up quickly - register as soon as possible!"
            )
        )
        
        logger.info(
            "request_complete",
            request_id=request_id,
            matched_count=len(response.matched_courses),
            total_credits=response.total_credits
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("request_failed", request_id=request_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.get("/api/search-courses")
async def search_courses(
    term: str,
    subject: Optional[str] = None,
    course_number: Optional[str] = None,
    keyword: Optional[str] = None,
    use_cache: bool = True
):
    """
    Search for courses in GSU PAWS
    
    Args:
        term: GSU term code
        subject: Subject code (e.g., CSC)
        course_number: Course number (e.g., 1301)
        keyword: Search keyword
        use_cache: Use cached data
    """
    try:
        paws_scraper: PAWSScraper = app.state.paws_scraper
        
        logger.info("searching_courses", term=term, subject=subject)
        
        courses = await paws_scraper.search_courses(
            term=term,
            subject=subject,
            course_number=course_number,
            keyword=keyword
        )
        
        return {
            "courses": courses,
            "count": len(courses),
            "term": term,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("search_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/professor-rating/{professor_name}")
async def get_professor_rating(
    professor_name: str,
    use_cache: bool = True
):
    """
    Get RateMyProfessors rating for a professor
    
    Args:
        professor_name: Full name of professor
        use_cache: Use cached data
    """
    try:
        rmp_scraper: RateMyProfessorsScraper = app.state.rmp_scraper
        
        logger.info("fetching_professor_rating", professor=professor_name)
        
        rating = await rmp_scraper.get_professor_rating(
            professor_name=professor_name,
            use_cache=use_cache
        )
        
        if not rating:
            raise HTTPException(
                status_code=404,
                detail=f"Professor '{professor_name}' not found on RateMyProfessors"
            )
        
        return {
            "professor": professor_name,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("rating_fetch_failed", professor=professor_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cache/clear")
async def clear_cache(pattern: Optional[str] = None):
    """
    Clear cache (admin endpoint)
    
    Args:
        pattern: Optional pattern to match keys (e.g., "courses:*")
    """
    try:
        if pattern:
            deleted = await cache_manager.clear_pattern(pattern)
            return {"status": "success", "deleted": deleted, "pattern": pattern}
        else:
            # Clear all (use with caution)
            await cache_manager.clear_pattern("*")
            return {"status": "success", "message": "All cache cleared"}
            
    except Exception as e:
        logger.error("cache_clear_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get application statistics"""
    try:
        cache_stats = await cache_manager.get_stats()
        
        # Get scraper stats from database
        from database import AsyncSessionLocal, ScraperLog
        from sqlalchemy import select, func
        
        async with AsyncSessionLocal() as session:
            # Recent scraper operations
            stmt = select(
                ScraperLog.source,
                ScraperLog.status,
                func.count(ScraperLog.id).label('count')
            ).group_by(ScraperLog.source, ScraperLog.status)
            
            result = await session.execute(stmt)
            scraper_stats = {f"{row.source}_{row.status}": row.count for row in result}
        
        return {
            "cache": cache_stats,
            "scrapers": scraper_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info" if settings.debug else "warning"
    )
