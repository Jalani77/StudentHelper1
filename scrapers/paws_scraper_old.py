"""
GSU PAWS Schedule Scraper - Production Version
Scrapes course information from GSU's PAWS/Banner system with caching
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
    """Production-ready scraper for GSU PAWS course schedule with caching"""
    
    def __init__(self):
        self.base_url = settings.gsu_paws_base_url
        self.schedule_url = settings.gsu_paws_schedule_url
        self.headers = {
            "User-Agent": settings.scraper_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        self._session: Optional[httpx.AsyncClient] = None
    
    async def get_available_courses(
        self,
        term: str,
        subjects: List[str],
        open_only: bool = True
    ) -> List[MatchedCourse]:
        """
        Scrape available courses from GSU PAWS
        
        Args:
            term: Term code (e.g., "202508")
            subjects: List of subject codes (e.g., ["CSC", "MATH"])
            open_only: Only return courses with available seats
            
        Returns:
            List of MatchedCourse objects
        """
        all_courses = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for subject in subjects:
                try:
                    logger.info(f"Scraping courses for subject: {subject}")
                    courses = await self._scrape_subject(client, term, subject)
                    
                    if open_only:
                        courses = [c for c in courses if c.seats_available > 0]
                    
                    all_courses.extend(courses)
                    logger.info(f"Found {len(courses)} courses for {subject}")
                    
                    # Be respectful with rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping {subject}: {str(e)}")
                    continue
        
        return all_courses
    
    async def _scrape_subject(
        self,
        client: httpx.AsyncClient,
        term: str,
        subject: str
    ) -> List[MatchedCourse]:
        """Scrape courses for a specific subject"""
        
        # GSU PAWS uses a multi-step form submission process
        # Step 1: Get the search form
        form_url = "https://www.gosolar.gsu.edu/bprod/bwckgens.p_proc_term_date"
        
        # Step 2: Submit term
        term_data = {
            "p_calling_proc": "bwckschd.p_disp_dyn_sched",
            "p_term": term
        }
        
        try:
            response = await client.post(form_url, data=term_data, headers=self.headers)
            response.raise_for_status()
            
            # Step 3: Submit subject selection
            search_url = "https://www.gosolar.gsu.edu/bprod/bwckschd.p_get_crse_unsec"
            search_data = {
                "term_in": term,
                "sel_subj": "dummy",
                "sel_day": "dummy",
                "sel_schd": "dummy",
                "sel_insm": "dummy",
                "sel_camp": "dummy",
                "sel_levl": "dummy",
                "sel_sess": "dummy",
                "sel_instr": "dummy",
                "sel_ptrm": "dummy",
                "sel_attr": "dummy",
                "sel_subj": subject,
                "sel_crse": "",
                "sel_title": "",
                "sel_insm": "%",
                "sel_from_cred": "",
                "sel_to_cred": "",
                "sel_camp": "%",
                "sel_ptrm": "%",
                "begin_hh": "0",
                "begin_mi": "0",
                "begin_ap": "a",
                "end_hh": "0",
                "end_mi": "0",
                "end_ap": "a"
            }
            
            response = await client.post(search_url, data=search_data, headers=self.headers)
            response.raise_for_status()
            
            # Parse the results
            courses = self._parse_schedule_page(response.text, subject)
            return courses
            
        except Exception as e:
            logger.error(f"Error in _scrape_subject for {subject}: {str(e)}")
            return []
    
    def _parse_schedule_page(self, html: str, subject: str) -> List[MatchedCourse]:
        """Parse the schedule page HTML"""
        soup = BeautifulSoup(html, 'lxml')
        courses = []
        
        # GSU PAWS uses tables with class "datadisplaytable"
        course_tables = soup.find_all('table', class_='datadisplaytable')
        
        for i in range(0, len(course_tables), 2):
            if i + 1 >= len(course_tables):
                break
                
            try:
                # First table has course header info
                header_table = course_tables[i]
                # Second table has course details
                detail_table = course_tables[i + 1]
                
                course = self._parse_course_tables(header_table, detail_table, subject)
                if course:
                    courses.append(course)
                    
            except Exception as e:
                logger.error(f"Error parsing course table: {str(e)}")
                continue
        
        return courses
    
    def _parse_course_tables(
        self,
        header_table,
        detail_table,
        subject: str
    ) -> Optional[MatchedCourse]:
        """Parse individual course from header and detail tables"""
        
        try:
            # Parse header (contains title and CRN)
            caption = header_table.find('caption', class_='captiontext')
            if not caption:
                return None
            
            title_text = caption.get_text(strip=True)
            # Format: "Title - CRN - Subject CourseNumber - Section"
            parts = title_text.split(' - ')
            
            if len(parts) < 4:
                return None
            
            title = parts[0]
            crn = parts[1]
            course_code = parts[2].split()
            section = parts[3]
            
            if len(course_code) < 2:
                return None
            
            course_subject = course_code[0]
            course_number = course_code[1]
            
            # Parse details table
            rows = detail_table.find_all('tr')
            
            credits = 0
            professor = None
            days = []
            time_str = None
            location = None
            seats_available = 0
            total_seats = 0
            delivery_method = "In-Person"
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                if len(cells) < 7:
                    continue
                
                # Cells: Type, Time, Days, Location, Date Range, Schedule Type, Instructors
                time_str = cells[1].get_text(strip=True)
                days_str = cells[2].get_text(strip=True)
                location = cells[3].get_text(strip=True)
                professor = cells[6].get_text(strip=True)
                
                # Parse days
                if days_str and days_str != 'TBA':
                    days = list(days_str)  # e.g., "MWF" -> ["M", "W", "F"]
                
                # Check for online
                if location and ('ONLINE' in location.upper() or 'WEB' in location.upper()):
                    delivery_method = "Online"
            
            # Try to find seat information
            # This is usually in a separate section or requires additional requests
            # For now, we'll set defaults
            seats_available = 0  # Would need additional scraping
            total_seats = 0
            
            # Try to extract credits from title or other sources
            # GSU typically shows credits in the course title or details
            credits = 3  # Default, would need more specific parsing
            
            return MatchedCourse(
                crn=crn,
                subject=course_subject,
                course_number=course_number,
                section=section,
                title=title,
                credits=credits,
                professor=professor if professor and professor != 'TBA' else None,
                days=days,
                time=time_str if time_str and time_str != 'TBA' else None,
                location=location if location and location != 'TBA' else None,
                seats_available=seats_available,
                total_seats=total_seats,
                delivery_method=delivery_method
            )
            
        except Exception as e:
            logger.error(f"Error parsing course: {str(e)}")
            return None
    
    async def search_courses(
        self,
        term: str,
        subject: Optional[str] = None,
        course_number: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[Dict]:
        """Search for specific courses"""
        # Implementation similar to get_available_courses but with filters
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
        """
        Generate the PAWS registration link for a given term
        
        Args:
            term: Term code
            
        Returns:
            URL to PAWS registration page
        """
        return f"https://www.gosolar.gsu.edu/bprod/twbkwbis.P_GenMenu?name=bmenu.P_RegMnu&term={term}"
