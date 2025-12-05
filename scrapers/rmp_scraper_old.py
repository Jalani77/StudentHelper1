"""
RateMyProfessors Scraper
Fetches professor ratings from RateMyProfessors.com
"""
import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict
import logging
import asyncio
import json
import base64

logger = logging.getLogger(__name__)


class RateMyProfessorsScraper:
    """Scraper for RateMyProfessors data"""
    
    def __init__(self):
        self.base_url = "https://www.ratemyprofessors.com"
        self.graphql_url = "https://www.ratemyprofessors.com/graphql"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Authorization": "Basic dGVzdDp0ZXN0",  # RMP's public authorization
            "Content-Type": "application/json"
        }
        
        # Cache to avoid repeated lookups
        self._cache = {}
    
    async def get_professor_rating(
        self,
        professor_name: str,
        school: str = "Georgia State University"
    ) -> Optional[Dict]:
        """
        Get professor rating from RateMyProfessors
        
        Args:
            professor_name: Full name of professor (e.g., "John Smith")
            school: School name
            
        Returns:
            Dict with rating data or None if not found
        """
        # Check cache
        cache_key = f"{professor_name}_{school}".lower()
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # First, get the school ID
            school_id = await self._get_school_id(school)
            if not school_id:
                logger.warning(f"Could not find school ID for {school}")
                return None
            
            # Search for the professor
            professor_data = await self._search_professor(professor_name, school_id)
            
            if professor_data:
                self._cache[cache_key] = professor_data
            
            return professor_data
            
        except Exception as e:
            logger.error(f"Error fetching rating for {professor_name}: {str(e)}")
            return None
    
    async def _get_school_id(self, school_name: str) -> Optional[str]:
        """Get the school ID from RateMyProfessors"""
        
        # GSU's known ID (you can hardcode this for performance)
        if "georgia state" in school_name.lower():
            return "U2Nob29sLTM1MQ=="  # Base64 encoded school ID for GSU
        
        # Otherwise search for it
        query = """
        query SchoolSearchQuery($query: String!) {
            search(query: $query) {
                schools {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        variables = {"query": school_name}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(
                    self.graphql_url,
                    json={"query": query, "variables": variables},
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                schools = data.get("data", {}).get("search", {}).get("schools", {}).get("edges", [])
                if schools:
                    return schools[0]["node"]["id"]
                
            except Exception as e:
                logger.error(f"Error getting school ID: {str(e)}")
        
        return None
    
    async def _search_professor(
        self,
        professor_name: str,
        school_id: str
    ) -> Optional[Dict]:
        """Search for a professor by name"""
        
        # Split name into first and last
        name_parts = professor_name.strip().split()
        if len(name_parts) < 2:
            logger.warning(f"Invalid professor name format: {professor_name}")
            return None
        
        first_name = name_parts[0]
        last_name = name_parts[-1]
        
        # RateMyProfessors GraphQL query
        query = """
        query TeacherSearchQuery($query: TeacherSearchQuery!) {
            search: newSearch {
                teachers(query: $query, first: 5) {
                    edges {
                        node {
                            id
                            firstName
                            lastName
                            avgRating
                            avgDifficulty
                            wouldTakeAgainPercent
                            numRatings
                            department
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "query": {
                "text": professor_name,
                "schoolID": school_id,
                "fallback": True
            }
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(
                    self.graphql_url,
                    json={"query": query, "variables": variables},
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                teachers = data.get("data", {}).get("search", {}).get("teachers", {}).get("edges", [])
                
                # Find best match
                for teacher_edge in teachers:
                    teacher = teacher_edge["node"]
                    teacher_first = teacher["firstName"].lower()
                    teacher_last = teacher["lastName"].lower()
                    
                    # Check if names match (allow for partial matches)
                    if (teacher_last == last_name.lower() and 
                        teacher_first.startswith(first_name[0].lower())):
                        
                        return {
                            "rating": teacher.get("avgRating"),
                            "difficulty": teacher.get("avgDifficulty"),
                            "would_take_again": teacher.get("wouldTakeAgainPercent"),
                            "num_ratings": teacher.get("numRatings"),
                            "department": teacher.get("department"),
                            "professor_id": teacher.get("id")
                        }
                
                logger.info(f"No exact match found for {professor_name}")
                return None
                
            except Exception as e:
                logger.error(f"Error searching for professor: {str(e)}")
                return None
    
    def clear_cache(self):
        """Clear the rating cache"""
        self._cache.clear()
