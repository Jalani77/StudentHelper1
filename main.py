"""FastAPI application for YiriAi StudentHelper"""

from fastapi import FastAPI, Query

from gsu_paws_scraper import scrape_gsu_paws_courses

app = FastAPI(title="YiriAi StudentHelper API")


@app.get("/gsu-search")
def gsu_search(
    term: str = Query(..., description="The term to search for (e.g., 'Fall 2024')"),
    subject: str = Query(..., description="The subject code (e.g., 'CSC')"),
    campus: str = Query(..., description="The campus location (e.g., 'Atlanta')")
) -> list:
    """
    Search for GSU PAWS courses.
    
    Returns a list of courses matching the given criteria.
    """
    return scrape_gsu_paws_courses(term=term, subject=subject, campus=campus)
