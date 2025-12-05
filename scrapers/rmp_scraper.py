"""
RateMyProfessors Scraper - Production Version
Real GraphQL API implementation with caching and retry logic
"""
import httpx
from typing import Optional, Dict
import logging
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import settings
from cache import cache_manager, professor_cache_key
from database import AsyncSessionLocal, ProfessorCache, ScraperLog

logger = logging.getLogger(__name__)


class RateMyProfessorsScraper:
    """Production scraper for RateMyProfessors using GraphQL API"""
    
    def __init__(self):
        self.base_url = settings.rmp_base_url
        self.graphql_url = settings.rmp_graphql_url
        self.school_id = settings.rmp_school_id
        self.headers = {
            "User-Agent": settings.scraper_user_agent,
            "Authorization": settings.rmp_authorization,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._session: Optional[httpx.AsyncClient] = None
        
        # Cache to avoid repeated lookups in same session
        self._memory_cache = {}
    
    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP session"""
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(
                timeout=settings.scraper_timeout,
                headers=self.headers,
                follow_redirects=True
            )
        return self._session
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.is_closed:
            await self._session.aclose()
    
    @retry(
        stop=stop_after_attempt(settings.scraper_max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
    )
    async def get_professor_rating(
        self,
        professor_name: str,
        school: str = "Georgia State University",
        use_cache: bool = True
    ) -> Optional[Dict]:
        """
        Get professor rating from RateMyProfessors using GraphQL API
        
        Args:
            professor_name: Full name of professor
            school: School name (default: GSU)
            use_cache: Use cached data if available
            
        Returns:
            Dict with rating data or None if not found
        """
        start_time = datetime.now()
        
        # Check memory cache first
        cache_key = professor_cache_key(professor_name)
        if cache_key in self._memory_cache:
            logger.info(f"Memory cache hit for {professor_name}")
            return self._memory_cache[cache_key]
        
        # Check Redis cache
        if use_cache:
            cached_data = await cache_manager.get(cache_key)
            if cached_data:
                logger.info(f"Redis cache hit for {professor_name}")
                self._memory_cache[cache_key] = cached_data
                return cached_data
        
        # Check database cache
        if use_cache:
            db_data = await self._get_from_db(professor_name)
            if db_data:
                logger.info(f"Database cache hit for {professor_name}")
                self._memory_cache[cache_key] = db_data
                await cache_manager.set(cache_key, db_data, ttl=settings.cache_ttl_professor)
                return db_data
        
        # Fetch fresh data
        try:
            logger.info(f"Fetching fresh data for {professor_name}")
            professor_data = await self._search_professor(professor_name, self.school_id)
            
            if professor_data:
                # Cache the result
                if use_cache:
                    await cache_manager.set(
                        cache_key,
                        professor_data,
                        ttl=settings.cache_ttl_professor
                    )
                    await self._store_in_db(professor_name, professor_data)
                
                self._memory_cache[cache_key] = professor_data
                
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                await self._log_success(professor_name, duration_ms)
                
                return professor_data
            else:
                logger.info(f"No rating found for {professor_name}")
                await self._log_not_found(professor_name)
                return None
                
        except Exception as e:
            logger.error(f"Error fetching rating for {professor_name}: {str(e)}")
            await self._log_error(professor_name, str(e))
            return None
    
    async def _search_professor(
        self,
        professor_name: str,
        school_id: str
    ) -> Optional[Dict]:
        """
        Search for professor using RMP GraphQL API
        
        The real RMP GraphQL API structure (as of 2024)
        """
        
        # Parse name
        name_parts = professor_name.strip().split()
        if len(name_parts) < 2:
            logger.warning(f"Invalid professor name format: {professor_name}")
            return None
        
        first_name = name_parts[0]
        last_name = name_parts[-1]
        
        # RMP GraphQL query for teacher search
        query = """
        query NewSearchTeachersQuery($query: TeacherSearchQuery!) {
          newSearch {
            teachers(query: $query) {
              edges {
                cursor
                node {
                  id
                  legacyId
                  firstName
                  lastName
                  school {
                    name
                    id
                  }
                  department
                  avgRating
                  avgDifficulty
                  wouldTakeAgainPercent
                  numRatings
                  courseCodes {
                    courseName
                    courseCount
                  }
                }
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }
        """
        
        variables = {
            "query": {
                "text": professor_name,
                "schoolID": school_id,
                "fallback": True,
                "departmentID": None
            }
        }
        
        session = await self._get_session()
        
        try:
            response = await session.post(
                self.graphql_url,
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for errors
            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return None
            
            # Extract teachers
            teachers = data.get("data", {}).get("newSearch", {}).get("teachers", {}).get("edges", [])
            
            if not teachers:
                logger.info(f"No teachers found for {professor_name}")
                return None
            
            # Find best match
            best_match = self._find_best_match(teachers, first_name, last_name)
            
            if best_match:
                node = best_match["node"]
                
                # Extract top courses
                top_courses = []
                if node.get("courseCodes"):
                    top_courses = [
                        course["courseName"] 
                        for course in sorted(
                            node["courseCodes"],
                            key=lambda x: x.get("courseCount", 0),
                            reverse=True
                        )[:5]
                    ]
                
                result = {
                    "rating": node.get("avgRating"),
                    "difficulty": node.get("avgDifficulty"),
                    "would_take_again": node.get("wouldTakeAgainPercent"),
                    "num_ratings": node.get("numRatings", 0),
                    "department": node.get("department"),
                    "professor_id": node.get("legacyId") or node.get("id"),
                    "first_name": node.get("firstName"),
                    "last_name": node.get("lastName"),
                    "school_name": node.get("school", {}).get("name"),
                    "top_courses": top_courses,
                    "rmp_url": f"{self.base_url}/professor/{node.get('legacyId')}" if node.get('legacyId') else None
                }
                
                logger.info(f"Found match for {professor_name}: {result['rating']}/5.0")
                return result
            
            logger.info(f"No exact match found for {professor_name}")
            return None
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching for professor: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error searching for professor: {str(e)}")
            raise
    
    def _find_best_match(
        self,
        teachers: list,
        first_name: str,
        last_name: str
    ) -> Optional[Dict]:
        """
        Find best matching professor from search results
        
        Scoring based on:
        - Exact last name match (required)
        - First name match or initial match
        - Has ratings
        """
        
        candidates = []
        
        for teacher_edge in teachers:
            node = teacher_edge["node"]
            teacher_first = node.get("firstName", "").lower()
            teacher_last = node.get("lastName", "").lower()
            
            # Must match last name
            if teacher_last != last_name.lower():
                continue
            
            score = 100  # Base score for last name match
            
            # First name scoring
            if teacher_first == first_name.lower():
                score += 50  # Exact match
            elif teacher_first.startswith(first_name[0].lower()):
                score += 25  # Initial match
            else:
                score -= 20  # No match
            
            # Bonus for having ratings
            num_ratings = node.get("numRatings", 0)
            if num_ratings > 0:
                score += min(num_ratings, 20)  # Up to 20 bonus points
            else:
                score -= 30  # Penalty for no ratings
            
            candidates.append((score, teacher_edge))
        
        if not candidates:
            return None
        
        # Return highest scoring candidate
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_teacher = candidates[0]
        
        if best_score < 80:  # Threshold for accepting a match
            logger.warning(f"Best match score {best_score} is below threshold")
            return None
        
        return best_teacher
    
    async def _get_from_db(self, professor_name: str) -> Optional[Dict]:
        """Get professor data from database cache"""
        try:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select
                
                stmt = select(ProfessorCache).where(
                    ProfessorCache.professor_name == professor_name,
                    ProfessorCache.expires_at > datetime.utcnow()
                )
                result = await session.execute(stmt)
                prof = result.scalar_one_or_none()
                
                if prof:
                    return {
                        "rating": prof.avg_rating,
                        "difficulty": prof.avg_difficulty,
                        "would_take_again": prof.would_take_again_percent,
                        "num_ratings": prof.num_ratings,
                        "department": prof.department,
                        "professor_id": prof.rmp_id,
                        "tags": prof.tags
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error reading from database: {e}")
            return None
    
    async def _store_in_db(self, professor_name: str, data: Dict):
        """Store professor data in database"""
        try:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select
                
                # Check if exists
                stmt = select(ProfessorCache).where(
                    ProfessorCache.professor_name == professor_name
                )
                result = await session.execute(stmt)
                prof = result.scalar_one_or_none()
                
                expires_at = datetime.utcnow() + timedelta(seconds=settings.cache_ttl_professor)
                
                if prof:
                    # Update existing
                    prof.avg_rating = data.get("rating")
                    prof.avg_difficulty = data.get("difficulty")
                    prof.would_take_again_percent = data.get("would_take_again")
                    prof.num_ratings = data.get("num_ratings")
                    prof.department = data.get("department")
                    prof.rmp_id = data.get("professor_id")
                    prof.raw_data = data
                    prof.updated_at = datetime.utcnow()
                    prof.expires_at = expires_at
                else:
                    # Create new
                    prof = ProfessorCache(
                        professor_name=professor_name,
                        school_id=self.school_id,
                        rmp_id=data.get("professor_id"),
                        avg_rating=data.get("rating"),
                        avg_difficulty=data.get("difficulty"),
                        would_take_again_percent=data.get("would_take_again"),
                        num_ratings=data.get("num_ratings"),
                        department=data.get("department"),
                        raw_data=data,
                        expires_at=expires_at
                    )
                    session.add(prof)
                
                await session.commit()
                logger.info(f"Stored professor {professor_name} in database")
                
        except Exception as e:
            logger.error(f"Error storing in database: {e}")
    
    async def _log_success(self, professor_name: str, duration_ms: int):
        """Log successful lookup"""
        try:
            async with AsyncSessionLocal() as session:
                log = ScraperLog(
                    source="rmp",
                    operation="get_professor",
                    status="success",
                    query_params={"professor": professor_name},
                    items_found=1,
                    duration_ms=duration_ms
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"Error logging success: {e}")
    
    async def _log_not_found(self, professor_name: str):
        """Log professor not found"""
        try:
            async with AsyncSessionLocal() as session:
                log = ScraperLog(
                    source="rmp",
                    operation="get_professor",
                    status="not_found",
                    query_params={"professor": professor_name},
                    items_found=0
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"Error logging not found: {e}")
    
    async def _log_error(self, professor_name: str, error_msg: str):
        """Log error"""
        try:
            async with AsyncSessionLocal() as session:
                log = ScraperLog(
                    source="rmp",
                    operation="get_professor",
                    status="error",
                    query_params={"professor": professor_name},
                    error_message=error_msg[:500]
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"Error logging error: {e}")
    
    def clear_cache(self):
        """Clear memory cache"""
        self._memory_cache.clear()
    
    async def batch_get_ratings(
        self,
        professor_names: list[str],
        school: str = "Georgia State University"
    ) -> Dict[str, Optional[Dict]]:
        """
        Get ratings for multiple professors efficiently
        
        Args:
            professor_names: List of professor names
            school: School name
            
        Returns:
            Dict mapping professor names to their rating data
        """
        results = {}
        
        # Check cache for all professors first
        cache_keys = [professor_cache_key(name) for name in professor_names]
        cached_data = await cache_manager.get_many(cache_keys)
        
        # Separate cached and uncached
        to_fetch = []
        for name, cache_key in zip(professor_names, cache_keys):
            if cache_key in cached_data:
                results[name] = cached_data[cache_key]
            else:
                to_fetch.append(name)
        
        # Fetch uncached professors
        for name in to_fetch:
            rating = await self.get_professor_rating(name, school)
            results[name] = rating
        
        return results
