"""
YiriAi - GSU Course Selection Assistant
FastAPI application that helps GSU students find and select courses
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
from datetime import datetime

from models import CoursePreferences, MatchedCourse, RegistrationResponse
from scrapers.paws_scraper import PAWSScraper
from scrapers.rmp_scraper import RateMyProfessorsScraper
from utils.course_matcher import CourseMatcher
from utils.file_parser import FileParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YiriAi - GSU Course Assistant",
    description="Automates course selection for GSU students by matching preferences with available courses",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
paws_scraper = PAWSScraper()
rmp_scraper = RateMyProfessorsScraper()
course_matcher = CourseMatcher()
file_parser = FileParser()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "YiriAi",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "message": "GSU Course Selection Assistant is running"
    }


@app.post("/api/upload-preferences", response_model=RegistrationResponse)
async def upload_preferences(
    eval_file: Optional[UploadFile] = File(None),
    prefs_file: UploadFile = File(...),
    term: str = "202508",  # e.g., Spring 2025
    include_ratings: bool = True
):
    """
    Upload student evaluation and course preferences
    
    Args:
        eval_file: Optional student evaluation file (PDF, TXT, or Excel)
        prefs_file: Course preferences file (JSON, CSV, or Excel)
        term: GSU term code (e.g., 202508 for Spring 2025)
        include_ratings: Whether to include RateMyProfessors data
    
    Returns:
        RegistrationResponse with matched courses, CRNs, and PAWS link
    """
    try:
        logger.info(f"Processing course preferences for term {term}")
        
        # Parse evaluation file if provided
        eval_data = None
        if eval_file:
            eval_content = await eval_file.read()
            eval_data = file_parser.parse_evaluation(eval_content, eval_file.filename)
            logger.info(f"Parsed evaluation data: {len(eval_data)} courses completed")
        
        # Parse preferences file
        prefs_content = await prefs_file.read()
        preferences = file_parser.parse_preferences(prefs_content, prefs_file.filename)
        logger.info(f"Parsed preferences: {len(preferences.courses)} courses requested")
        
        # Scrape GSU PAWS for available courses
        logger.info("Scraping GSU PAWS schedule...")
        available_courses = await paws_scraper.get_available_courses(
            term=term,
            subjects=preferences.subjects
        )
        logger.info(f"Found {len(available_courses)} available courses")
        
        # Match courses based on preferences and availability
        logger.info("Matching courses to preferences...")
        matched_courses = course_matcher.match_courses(
            preferences=preferences,
            available_courses=available_courses,
            completed_courses=eval_data
        )
        logger.info(f"Matched {len(matched_courses)} courses")
        
        # Enhance with RateMyProfessors data if requested
        if include_ratings and matched_courses:
            logger.info("Fetching professor ratings...")
            for course in matched_courses:
                if course.professor:
                    rating_data = await rmp_scraper.get_professor_rating(
                        professor_name=course.professor,
                        school="Georgia State University"
                    )
                    if rating_data:
                        course.professor_rating = rating_data.get("rating")
                        course.professor_difficulty = rating_data.get("difficulty")
                        course.would_take_again = rating_data.get("would_take_again")
        
        # Generate PAWS registration link
        paws_link = paws_scraper.generate_registration_link(term)
        
        # Build response
        response = RegistrationResponse(
            matched_courses=matched_courses,
            paws_link=paws_link,
            term=term,
            timestamp=datetime.now().isoformat(),
            instructions=(
                "1. Click the PAWS link below\n"
                "2. Log into your GSU account\n"
                "3. Navigate to 'Add/Drop Classes'\n"
                "4. Copy and paste each CRN into the registration form\n"
                "5. Click 'Submit Changes' to register"
            )
        )
        
        logger.info(f"Successfully generated response with {len(matched_courses)} courses")
        return response
        
    except Exception as e:
        logger.error(f"Error processing preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/api/search-courses")
async def search_courses(
    term: str,
    subject: Optional[str] = None,
    course_number: Optional[str] = None,
    keyword: Optional[str] = None
):
    """
    Search for courses in GSU PAWS
    
    Args:
        term: GSU term code
        subject: Subject code (e.g., CSC, MATH)
        course_number: Course number (e.g., 1301)
        keyword: Search keyword
    """
    try:
        courses = await paws_scraper.search_courses(
            term=term,
            subject=subject,
            course_number=course_number,
            keyword=keyword
        )
        return {"courses": courses, "count": len(courses)}
    except Exception as e:
        logger.error(f"Error searching courses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/professor-rating/{professor_name}")
async def get_professor_rating(professor_name: str):
    """
    Get RateMyProfessors rating for a professor
    
    Args:
        professor_name: Full name of the professor
    """
    try:
        rating = await rmp_scraper.get_professor_rating(
            professor_name=professor_name,
            school="Georgia State University"
        )
        if not rating:
            raise HTTPException(status_code=404, detail="Professor not found")
        return rating
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching professor rating: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
