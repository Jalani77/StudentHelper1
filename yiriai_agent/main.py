"""
YiriAi Agent - Main FastAPI Application.

A FastAPI agent that helps GSU students find and select courses
based on their preferences and evaluations. YiriAi scrapes the GSU PAWS
class schedule, finds open courses, and pulls professor info from
RateMyProfessors.

Note: YiriAi only automates course selection, NOT registration.
Students handle their own PAWS login and registration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .matcher import course_matcher
from .models import (
    ClassPreference,
    CourseResult,
    CourseSearchResponse,
    HealthResponse,
    StudentRequest,
)
from .professor_service import rmp_service
from .scraper import paws_scraper

# Create FastAPI application
app = FastAPI(
    title="YiriAi Agent",
    description=(
        "A course selection assistant for GSU students. "
        "Upload your preferences and evaluation, and YiriAi will find "
        "matching open courses with professor ratings. "
        "Note: YiriAi only helps with selection - you handle registration."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        service="YiriAi Agent",
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        service="YiriAi Agent",
    )


@app.post("/api/v1/search", response_model=CourseSearchResponse)
async def search_courses(request: StudentRequest):
    """
    Search for courses matching student preferences.

    This endpoint accepts student preferences and evaluation data,
    searches the GSU PAWS schedule for matching open courses,
    enriches results with RateMyProfessors data, and returns
    a list of recommended courses with CRNs for easy registration.

    Args:
        request: StudentRequest containing preferences and evaluation

    Returns:
        CourseSearchResponse with matched courses and CRN list
    """
    if not request.preferences:
        raise HTTPException(
            status_code=400,
            detail="At least one class preference is required",
        )

    all_courses: list[CourseResult] = []
    term_code = paws_scraper.parse_term_code(request.term)

    # Search for each preference
    for preference in request.preferences:
        courses = await paws_scraper.search_courses(
            term=term_code,
            subject=preference.subject,
            course_number=preference.course_number,
        )

        # Enrich with professor information
        for course in courses:
            if course.instructor:
                professor_info = await rmp_service.get_professor_info(course.instructor)
                if professor_info:
                    course.professor_info = professor_info

            # Calculate match score
            course.match_score = course_matcher.calculate_match_score(
                course=course,
                preference=preference,
                evaluation=request.evaluation,
            )

        all_courses.extend(courses)

    # Filter by prerequisites if evaluation provided
    if request.evaluation:
        all_courses = course_matcher.filter_by_prerequisites(
            all_courses, request.evaluation
        )

    # Sort by match score (highest first)
    all_courses.sort(key=lambda c: c.match_score, reverse=True)

    # Generate CRN list for easy registration
    crn_list = ", ".join(course.crn for course in all_courses)

    return CourseSearchResponse(
        success=True,
        message=f"Found {len(all_courses)} matching courses for {request.term}",
        term=request.term,
        courses=all_courses,
        crn_list=crn_list,
        paws_registration_url="https://paws.gsu.edu/",
        total_results=len(all_courses),
    )


@app.get("/api/v1/subjects")
async def get_subjects():
    """
    Get a list of available subject codes.

    Returns a list of common GSU subject codes.
    """
    subjects = [
        {"code": "CSC", "name": "Computer Science"},
        {"code": "MATH", "name": "Mathematics"},
        {"code": "ENGL", "name": "English"},
        {"code": "PHYS", "name": "Physics"},
        {"code": "CHEM", "name": "Chemistry"},
        {"code": "BIOL", "name": "Biology"},
        {"code": "HIST", "name": "History"},
        {"code": "POLS", "name": "Political Science"},
        {"code": "PSYC", "name": "Psychology"},
        {"code": "ECON", "name": "Economics"},
    ]
    return {"subjects": subjects}


@app.post("/api/v1/quick-search")
async def quick_search(
    subject: str,
    term: str = "Spring 2025",
    course_number: str | None = None,
):
    """
    Quick search for courses by subject.

    A simplified search endpoint for quick lookups.

    Args:
        subject: Subject code (e.g., 'CSC', 'MATH')
        term: Academic term (default: 'Spring 2025')
        course_number: Optional course number filter

    Returns:
        CourseSearchResponse with matching courses
    """
    preference = ClassPreference(
        subject=subject,
        course_number=course_number,
    )

    request = StudentRequest(
        preferences=[preference],
        term=term,
    )

    return await search_courses(request)
