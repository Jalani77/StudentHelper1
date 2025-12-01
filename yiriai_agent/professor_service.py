"""
RateMyProfessors Integration.

This module handles fetching professor ratings and information
from RateMyProfessors for GSU professors.
"""

from typing import Optional

from .models import ProfessorInfo


# GSU School ID on RateMyProfessors
GSU_SCHOOL_ID = 397  # Georgia State University


class RateMyProfessorService:
    """Service for fetching professor ratings from RateMyProfessors."""

    def __init__(self):
        """Initialize the RateMyProfessors service."""
        self.school_id = GSU_SCHOOL_ID
        self._cache: dict[str, ProfessorInfo] = {}

    async def get_professor_info(self, professor_name: str) -> Optional[ProfessorInfo]:
        """
        Get professor information from RateMyProfessors.

        Args:
            professor_name: The professor's name to search for

        Returns:
            ProfessorInfo object if found, None otherwise
        """
        if not professor_name:
            return None

        # Check cache first
        cache_key = professor_name.lower().strip()
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Try to fetch from RateMyProfessors
        professor_info = await self._fetch_professor_data(professor_name)

        if professor_info:
            self._cache[cache_key] = professor_info

        return professor_info

    async def _fetch_professor_data(
        self, professor_name: str
    ) -> Optional[ProfessorInfo]:
        """
        Fetch professor data from RateMyProfessors.

        In production, this uses the ratemyprofessor library.
        For demonstration, we use sample data.
        """
        # Sample professor data for demonstration
        sample_professors = {
            "john smith": ProfessorInfo(
                name="John Smith",
                rating=4.2,
                difficulty=3.1,
                would_take_again=85.0,
                department="Computer Science",
                num_ratings=45,
            ),
            "jane doe": ProfessorInfo(
                name="Jane Doe",
                rating=4.8,
                difficulty=2.5,
                would_take_again=95.0,
                department="Computer Science",
                num_ratings=62,
            ),
            "robert johnson": ProfessorInfo(
                name="Robert Johnson",
                rating=3.9,
                difficulty=3.8,
                would_take_again=70.0,
                department="Computer Science",
                num_ratings=38,
            ),
            "michael brown": ProfessorInfo(
                name="Michael Brown",
                rating=4.5,
                difficulty=3.3,
                would_take_again=88.0,
                department="Computer Science",
                num_ratings=55,
            ),
            "sarah wilson": ProfessorInfo(
                name="Sarah Wilson",
                rating=4.1,
                difficulty=2.8,
                would_take_again=82.0,
                department="Mathematics",
                num_ratings=72,
            ),
            "david lee": ProfessorInfo(
                name="David Lee",
                rating=4.6,
                difficulty=3.5,
                would_take_again=90.0,
                department="Mathematics",
                num_ratings=48,
            ),
            "emily davis": ProfessorInfo(
                name="Emily Davis",
                rating=4.3,
                difficulty=2.2,
                would_take_again=92.0,
                department="English",
                num_ratings=85,
            ),
            "thomas anderson": ProfessorInfo(
                name="Thomas Anderson",
                rating=3.7,
                difficulty=4.2,
                would_take_again=65.0,
                department="Physics",
                num_ratings=33,
            ),
        }

        name_key = professor_name.lower().strip()
        return sample_professors.get(name_key)

    def clear_cache(self):
        """Clear the professor info cache."""
        self._cache.clear()


# Create a singleton instance
rmp_service = RateMyProfessorService()
