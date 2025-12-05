"""
GSU PAWS Schedule Scraper - Production Version
Real implementation with Banner system parsing, caching, and retry logic
"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from models import MatchedCourse
from config import settings
from cache import cache_manager, course_cache_key, crn_cache_key
from database import AsyncSessionLocal, CourseCache, ScraperLog

logger = logging.getLogger(__name__)


class PAWSScraper:
    """Production-ready scraper for GSU PAWS/Banner course schedule"""
    
    def __init__(self):
        self.base_url = settings.gsu_paws_base_url
        self.schedule_url = settings.gsu_paws_schedule_url
        self.headers = {
            "User-Agent": settings.scraper_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        self._session: Optional[httpx.AsyncClient] = None
    
    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP session"""
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(
                timeout=settings.scraper_timeout,
                headers=self.headers,
                follow_redirects=True,
                limits=httpx.Limits(max_connections=settings.scraper_concurrent_requests)
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
    async def get_available_courses(
        self,
        term: str,
        subjects: List[str],
        open_only: bool = True,
        use_cache: bool = True
    ) -> List[MatchedCourse]:
        """
        Get available courses from GSU PAWS with caching
        
        Args:
            term: Term code (e.g., "202508")
            subjects: List of subject codes (e.g., ["CSC", "MATH"])
            open_only: Only return courses with available seats
            use_cache: Use cached data if available
            
        Returns:
            List of MatchedCourse objects
        """
        start_time = datetime.now()
        all_courses = []
        
        for subject in subjects:
            try:
                # Check cache first
                if use_cache:
                    cache_key = course_cache_key(term, subject)
                    cached_data = await cache_manager.get(cache_key)
                    
                    if cached_data:
                        logger.info(f"Cache hit for {subject} in term {term}")
                        courses = [MatchedCourse(**c) for c in cached_data]
                        if open_only:
                            courses = [c for c in courses if c.seats_available > 0]
                        all_courses.extend(courses)
                        continue
                
                # Scrape fresh data
                logger.info(f"Scraping courses for {subject} in term {term}")
                courses = await self._scrape_subject(term, subject)
                
                # Cache the results
                if use_cache and courses:
                    cache_key = course_cache_key(term, subject)
                    cache_data = [c.dict() for c in courses]
                    await cache_manager.set(cache_key, cache_data, ttl=settings.cache_ttl_courses)
                    
                    # Also store in database
                    await self._store_courses_in_db(courses, term)
                
                if open_only:
                    courses = [c for c in courses if c.seats_available > 0]
                
                all_courses.extend(courses)
                logger.info(f"Found {len(courses)} courses for {subject}")
                
                # Rate limiting between subjects
                await asyncio.sleep(settings.scraper_retry_delay)
                
            except Exception as e:
                logger.error(f"Error scraping {subject}: {str(e)}", exc_info=True)
                await self._log_scraper_error(term, subject, str(e))
                continue
        
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        await self._log_scraper_success(term, subjects, len(all_courses), duration_ms)
        
        return all_courses
    
    async def _scrape_subject(
        self,
        term: str,
        subject: str
    ) -> List[MatchedCourse]:
        """Scrape courses for a specific subject using Banner"""
        
        session = await self._get_session()
        
        try:
            # Step 1: Initialize term selection
            form_url = f"{self.base_url}/bprod/bwckgens.p_proc_term_date"
            term_data = {
                "p_calling_proc": "bwckschd.p_disp_dyn_sched",
                "p_term": term
            }
            
            response = await session.post(form_url, data=term_data)
            response.raise_for_status()
            
            # Step 2: Submit search criteria
            search_url = f"{self.base_url}/bprod/bwckschd.p_get_crse_unsec"
            search_data = {
                "term_in": term,
                "sel_subj": ["dummy", subject],
                "sel_day": "dummy",
                "sel_schd": "dummy",
                "sel_insm": "dummy",
                "sel_camp": "dummy",
                "sel_levl": "dummy",
                "sel_sess": "dummy",
                "sel_instr": "dummy",
                "sel_ptrm": "dummy",
                "sel_attr": "dummy",
                "sel_crse": "",
                "sel_title": "",
                "sel_from_cred": "",
                "sel_to_cred": "",
                "sel_camp": "%",
                "sel_ptrm": "%",
                "sel_instr": "%",
                "begin_hh": "0",
                "begin_mi": "0",
                "begin_ap": "a",
                "end_hh": "0",
                "end_mi": "0",
                "end_ap": "a"
            }
            
            response = await session.post(search_url, data=search_data)
            response.raise_for_status()
            
            # Parse the results
            courses = self._parse_banner_schedule(response.text, subject, term)
            return courses
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping {subject}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping {subject}: {str(e)}")
            raise
    
    def _parse_banner_schedule(self, html: str, subject: str, term: str) -> List[MatchedCourse]:
        """
        Parse Banner schedule page HTML
        Banner uses a table-based layout with specific CSS classes
        """
        soup = BeautifulSoup(html, 'lxml')
        courses = []
        
        # Banner puts course data in tables with class "datadisplaytable"
        # Each course has two consecutive tables: header table and detail table
        course_tables = soup.find_all('table', class_='datadisplaytable')
        
        i = 0
        while i < len(course_tables) - 1:
            try:
                header_table = course_tables[i]
                detail_table = course_tables[i + 1]
                
                # Skip if not a course header
                caption = header_table.find('caption', class_='captiontext')
                if not caption:
                    i += 1
                    continue
                
                course = self._parse_course_from_tables(header_table, detail_table, subject, term)
                if course:
                    courses.append(course)
                
                i += 2  # Move to next course pair
                
            except Exception as e:
                logger.warning(f"Error parsing course table: {str(e)}")
                i += 1
                continue
        
        return courses
    
    def _parse_course_from_tables(
        self,
        header_table,
        detail_table,
        subject: str,
        term: str
    ) -> Optional[MatchedCourse]:
        """Parse a single course from Banner header and detail tables"""
        
        try:
            # Parse header
            caption = header_table.find('caption', class_='captiontext')
            title_text = caption.get_text(strip=True)
            
            # Title format: "Course Title - CRN - SUBJ NUM - Section"
            # Example: "Intro to Computer Science - 12345 - CSC 1301 - 01"
            parts = [p.strip() for p in title_text.split(' - ')]
            
            if len(parts) < 4:
                return None
            
            title = parts[0]
            crn = parts[1]
            course_code_parts = parts[2].split()
            section = parts[3]
            
            if len(course_code_parts) < 2:
                return None
            
            course_subject = course_code_parts[0]
            course_number = course_code_parts[1]
            
            # Parse detail table rows
            detail_rows = detail_table.find_all('tr')
            
            # Initialize with defaults
            credits = 3
            professor = None
            days = []
            time_str = None
            location = None
            seats_available = 0
            total_seats = 0
            waitlist_available = 0
            delivery_method = "In-Person"
            
            # Parse detail rows (skip header)
            for row in detail_rows[1:]:
                cells = row.find_all('td')
                if len(cells) < 7:
                    continue
                
                # Column order: Type, Time, Days, Where, Date Range, Schedule Type, Instructors
                meeting_time = cells[1].get_text(strip=True)
                meeting_days = cells[2].get_text(strip=True)
                meeting_location = cells[3].get_text(strip=True)
                instructors = cells[6].get_text(strip=True)
                
                # Store first non-TBA values
                if meeting_time and meeting_time != 'TBA' and not time_str:
                    time_str = meeting_time
                
                if meeting_days and meeting_days != 'TBA' and not days:
                    # Parse days: "MWF" -> ["M", "W", "F"]
                    days = self._parse_days(meeting_days)
                
                if meeting_location and meeting_location != 'TBA' and not location:
                    location = meeting_location
                    # Check if online
                    if any(keyword in location.upper() for keyword in ['ONLINE', 'WEB', 'INTERNET', 'VIRTUAL']):
                        delivery_method = "Online"
                
                if instructors and instructors != 'TBA' and not professor:
                    # Clean up professor name
                    professor = self._clean_professor_name(instructors)
            
            # Try to find enrollment information
            # Banner sometimes has this in a separate table or link
            enrollment_info = self._extract_enrollment_info(header_table, detail_table)
            if enrollment_info:
                seats_available = enrollment_info.get('seats_available', 0)
                total_seats = enrollment_info.get('total_seats', 0)
                waitlist_available = enrollment_info.get('waitlist_available', 0)
            
            # Try to extract credits
            credits = self._extract_credits(header_table, detail_table) or 3
            
            return MatchedCourse(
                crn=crn,
                subject=course_subject,
                course_number=course_number,
                section=section,
                title=title,
                credits=credits,
                professor=professor,
                days=days,
                time=time_str,
                location=location,
                seats_available=seats_available,
                total_seats=total_seats,
                delivery_method=delivery_method
            )
            
        except Exception as e:
            logger.warning(f"Error parsing course: {str(e)}")
            return None
    
    def _parse_days(self, days_str: str) -> List[str]:
        """
        Parse day string into list of individual days
        Handles formats like "MWF", "TR", "M", etc.
        """
        if not days_str or days_str == 'TBA':
            return []
        
        # Banner uses: M, T, W, R (Thursday), F, S (Saturday), U (Sunday)
        days = []
        i = 0
        while i < len(days_str):
            if days_str[i] in ['M', 'T', 'W', 'R', 'F', 'S', 'U']:
                days.append(days_str[i])
            i += 1
        
        return days
    
    def _clean_professor_name(self, name: str) -> str:
        """Clean and format professor name"""
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove titles
        name = re.sub(r'\b(Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s*', '', name, flags=re.IGNORECASE)
        
        # Remove email if present
        name = re.sub(r'\s*\([^)]*@[^)]*\)', '', name)
        
        # Remove (P) or similar indicators
        name = re.sub(r'\s*\([A-Z]\)', '', name)
        
        return name.strip()
    
    def _extract_enrollment_info(self, header_table, detail_table) -> Optional[Dict]:
        """
        Extract seat availability from Banner tables
        Banner may have this in various formats
        """
        # Look for enrollment link in header table
        enrollment_link = header_table.find('a', href=re.compile(r'bwckschd\.p_disp_detail_sched'))
        
        if enrollment_link:
            # Parse the enrollment text
            # Common format: "Seats: 5/30" or "Available: 5 of 30"
            text = enrollment_link.get_text()
            
            # Try pattern: "X/Y" or "X of Y"
            match = re.search(r'(\d+)\s*(?:/|of)\s*(\d+)', text)
            if match:
                available = int(match.group(1))
                total = int(match.group(2))
                return {
                    'seats_available': available,
                    'total_seats': total,
                    'waitlist_available': 0
                }
        
        # Alternative: look in all table text
        all_text = header_table.get_text() + detail_table.get_text()
        
        # Try various patterns
        patterns = [
            r'Seats\s+Avail[^:]*:\s*(\d+)',
            r'Available:\s*(\d+)',
            r'(\d+)\s+(?:seats?\s+)?remain',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                return {
                    'seats_available': int(match.group(1)),
                    'total_seats': 0,  # Unknown
                    'waitlist_available': 0
                }
        
        return None
    
    def _extract_credits(self, header_table, detail_table) -> Optional[int]:
        """Extract credit hours from tables"""
        all_text = header_table.get_text() + detail_table.get_text()
        
        # Look for credit patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s+Credits?',
            r'Credits?:\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s+(?:Credit\s+)?Hours?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                try:
                    return int(float(match.group(1)))
                except ValueError:
                    continue
        
        return None
    
    async def _store_courses_in_db(self, courses: List[MatchedCourse], term: str):
        """Store courses in database for persistent caching"""
        try:
            async with AsyncSessionLocal() as session:
                expires_at = datetime.utcnow() + timedelta(seconds=settings.cache_ttl_courses)
                
                for course in courses:
                    # Check if course already exists
                    db_course = CourseCache(
                        crn=course.crn,
                        term=term,
                        subject=course.subject,
                        course_number=course.course_number,
                        section=course.section,
                        title=course.title,
                        credits=course.credits,
                        professor=course.professor,
                        days=course.days,
                        time_start=course.time,
                        time_end=None,
                        location=course.location,
                        seats_available=course.seats_available,
                        total_seats=course.total_seats,
                        delivery_method=course.delivery_method,
                        raw_data=course.dict(),
                        expires_at=expires_at
                    )
                    session.add(db_course)
                
                await session.commit()
                logger.info(f"Stored {len(courses)} courses in database")
                
        except Exception as e:
            logger.error(f"Error storing courses in database: {e}")
    
    async def _log_scraper_success(
        self,
        term: str,
        subjects: List[str],
        items_found: int,
        duration_ms: int
    ):
        """Log successful scraping operation"""
        try:
            async with AsyncSessionLocal() as session:
                log = ScraperLog(
                    source="paws",
                    operation="get_courses",
                    status="success",
                    term=term,
                    query_params={"subjects": subjects},
                    items_found=items_found,
                    duration_ms=duration_ms
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"Error logging scraper success: {e}")
    
    async def _log_scraper_error(self, term: str, subject: str, error_msg: str):
        """Log scraping error"""
        try:
            async with AsyncSessionLocal() as session:
                log = ScraperLog(
                    source="paws",
                    operation="get_courses",
                    status="error",
                    term=term,
                    subject=subject,
                    error_message=error_msg[:500]
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"Error logging scraper error: {e}")
    
    async def search_courses(
        self,
        term: str,
        subject: Optional[str] = None,
        course_number: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[Dict]:
        """Search for specific courses"""
        subjects = [subject] if subject else []
        courses = await self.get_available_courses(term, subjects, open_only=False)
        
        # Apply filters
        if course_number:
            courses = [c for c in courses if c.course_number == course_number]
        
        if keyword:
            keyword_lower = keyword.lower()
            courses = [
                c for c in courses
                if keyword_lower in c.title.lower() or
                   keyword_lower in f"{c.subject}{c.course_number}".lower()
            ]
        
        return [c.dict() for c in courses]
    
    def generate_registration_link(self, term: str) -> str:
        """Generate PAWS registration link"""
        return f"{self.base_url}/bprod/twbkwbis.P_GenMenu?name=bmenu.P_RegMnu&term={term}"
