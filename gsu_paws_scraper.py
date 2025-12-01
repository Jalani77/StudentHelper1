"""GSU PAWS Course Scraper Module"""

from typing import Any


def scrape_gsu_paws_courses(term: str, subject: str, campus: str) -> list[dict[str, Any]]:
    """
    Scrape GSU PAWS courses for the given term, subject, and campus.
    
    Args:
        term: The term to search for (e.g., "Fall 2024")
        subject: The subject code (e.g., "CSC")
        campus: The campus location (e.g., "Atlanta")
    
    Returns:
        A list of course dictionaries with mock data.
    """
    # Mock data for now
    mock_courses = [
        {
            "course_code": f"{subject} 1010",
            "title": "Introduction to Computing",
            "crn": "12345",
            "days": "MWF",
            "start_time": "09:00",
            "end_time": "09:50",
            "campus": campus,
            "is_online": False,
            "seats_open": 15,
            "professor_name": "Dr. Smith"
        },
        {
            "course_code": f"{subject} 2010",
            "title": "Programming Fundamentals",
            "crn": "12346",
            "days": "TR",
            "start_time": "11:00",
            "end_time": "12:15",
            "campus": campus,
            "is_online": False,
            "seats_open": 8,
            "professor_name": "Dr. Johnson"
        },
        {
            "course_code": f"{subject} 3000",
            "title": "Data Structures",
            "crn": "12347",
            "days": "MW",
            "start_time": "14:00",
            "end_time": "15:15",
            "campus": campus,
            "is_online": True,
            "seats_open": 25,
            "professor_name": "Dr. Williams"
        }
    ]
    
    return mock_courses
