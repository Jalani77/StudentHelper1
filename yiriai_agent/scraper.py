"""
GSU PAWS Class Schedule Scraper.

This module handles scraping the GSU PAWS class schedule
to find available courses.
"""

import re
from typing import Optional
import httpx
from bs4 import BeautifulSoup

from .models import CourseResult


# GSU PAWS schedule search URL
GSU_SCHEDULE_URL = "https://paws.gsu.edu/pls/std/HWSKSCHD.P_CrseSchd"


class PAWSScheduleScraper:
    """Scraper for GSU PAWS class schedule."""

    def __init__(self, timeout: float = 30.0):
        """Initialize the scraper with timeout settings."""
        self.timeout = timeout
        self.base_url = GSU_SCHEDULE_URL

    async def search_courses(
        self,
        term: str,
        subject: str,
        course_number: Optional[str] = None,
    ) -> list[CourseResult]:
        """
        Search for courses in the GSU schedule.

        Args:
            term: Academic term code (e.g., '202501' for Spring 2025)
            subject: Subject code (e.g., 'CSC')
            course_number: Optional course number filter

        Returns:
            List of CourseResult objects for matching courses
        """
        courses = []

        # Simulated course data for demonstration
        # In production, this would scrape actual PAWS data
        sample_courses = self._get_sample_courses(subject, course_number)

        for course_data in sample_courses:
            course = CourseResult(
                crn=course_data["crn"],
                subject=course_data["subject"],
                course_number=course_data["course_number"],
                section=course_data["section"],
                title=course_data["title"],
                credits=course_data["credits"],
                days=course_data.get("days"),
                time=course_data.get("time"),
                location=course_data.get("location"),
                instructor=course_data.get("instructor"),
                seats_available=course_data.get("seats_available"),
            )
            courses.append(course)

        return courses

    def _get_sample_courses(
        self, subject: str, course_number: Optional[str] = None
    ) -> list[dict]:
        """
        Get sample course data for demonstration purposes.

        In production, this would be replaced with actual web scraping.
        """
        # Sample course database for demonstration
        all_courses = [
            {
                "crn": "10001",
                "subject": "CSC",
                "course_number": "1301",
                "section": "001",
                "title": "Principles of Computer Science I",
                "credits": "4",
                "days": "MWF",
                "time": "9:00 AM - 9:50 AM",
                "location": "Petit Science Center 200",
                "instructor": "John Smith",
                "seats_available": 15,
            },
            {
                "crn": "10002",
                "subject": "CSC",
                "course_number": "1301",
                "section": "002",
                "title": "Principles of Computer Science I",
                "credits": "4",
                "days": "TR",
                "time": "2:00 PM - 3:15 PM",
                "location": "Petit Science Center 205",
                "instructor": "Jane Doe",
                "seats_available": 8,
            },
            {
                "crn": "10003",
                "subject": "CSC",
                "course_number": "2010",
                "section": "001",
                "title": "Principles of Computer Science II",
                "credits": "4",
                "days": "MWF",
                "time": "10:00 AM - 10:50 AM",
                "location": "Petit Science Center 210",
                "instructor": "Robert Johnson",
                "seats_available": 20,
            },
            {
                "crn": "10004",
                "subject": "CSC",
                "course_number": "3320",
                "section": "001",
                "title": "System Level Programming",
                "credits": "4",
                "days": "TR",
                "time": "11:00 AM - 12:15 PM",
                "location": "Petit Science Center 220",
                "instructor": "Michael Brown",
                "seats_available": 12,
            },
            {
                "crn": "10005",
                "subject": "MATH",
                "course_number": "1113",
                "section": "001",
                "title": "Precalculus",
                "credits": "3",
                "days": "MWF",
                "time": "8:00 AM - 8:50 AM",
                "location": "Classroom South 309",
                "instructor": "Sarah Wilson",
                "seats_available": 25,
            },
            {
                "crn": "10006",
                "subject": "MATH",
                "course_number": "2211",
                "section": "001",
                "title": "Calculus I",
                "credits": "4",
                "days": "MTRF",
                "time": "9:00 AM - 9:50 AM",
                "location": "Classroom South 315",
                "instructor": "David Lee",
                "seats_available": 18,
            },
            {
                "crn": "10007",
                "subject": "ENGL",
                "course_number": "1101",
                "section": "001",
                "title": "English Composition I",
                "credits": "3",
                "days": "MW",
                "time": "1:00 PM - 2:15 PM",
                "location": "General Classroom Bldg 405",
                "instructor": "Emily Davis",
                "seats_available": 22,
            },
            {
                "crn": "10008",
                "subject": "PHYS",
                "course_number": "2211",
                "section": "001",
                "title": "Principles of Physics I",
                "credits": "4",
                "days": "TR",
                "time": "3:30 PM - 4:45 PM",
                "location": "Science Annex 140",
                "instructor": "Thomas Anderson",
                "seats_available": 10,
            },
        ]

        # Filter by subject
        filtered = [c for c in all_courses if c["subject"].upper() == subject.upper()]

        # Filter by course number if provided
        if course_number:
            filtered = [c for c in filtered if c["course_number"] == course_number]

        return filtered

    def parse_term_code(self, term: str) -> str:
        """
        Parse a human-readable term string to a term code.

        Args:
            term: Human-readable term (e.g., 'Spring 2025', 'Fall 2024')

        Returns:
            Term code (e.g., '202501' for Spring 2025)
        """
        term_lower = term.lower()
        year_match = re.search(r"20\d{2}", term)
        year = year_match.group() if year_match else "2025"

        if "spring" in term_lower:
            return f"{year}01"
        elif "summer" in term_lower:
            return f"{year}05"
        elif "fall" in term_lower:
            return f"{year}08"
        else:
            return f"{year}01"  # Default to spring


# Create a singleton instance
paws_scraper = PAWSScheduleScraper()
