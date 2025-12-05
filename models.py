"""
Data models for YiriAi application
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import time


class TimeSlot(BaseModel):
    """Time slot for a course"""
    days: List[str]  # e.g., ["M", "W", "F"]
    start_time: str  # e.g., "09:00"
    end_time: str    # e.g., "10:15"


class CoursePreference(BaseModel):
    """Individual course preference"""
    subject: str  # e.g., "CSC"
    course_number: Optional[str] = None  # e.g., "1301"
    priority: int = 1  # 1 = highest priority
    online_only: bool = False
    exclude_professors: List[str] = []
    preferred_times: List[TimeSlot] = []


class CoursePreferences(BaseModel):
    """Complete set of student preferences"""
    courses: List[CoursePreference]
    subjects: List[str]  # List of all subjects to search
    max_credits: Optional[int] = None
    avoid_time_conflicts: bool = True
    prefer_online: bool = False
    min_professor_rating: Optional[float] = None


class MatchedCourse(BaseModel):
    """A matched course with all details"""
    crn: str
    subject: str
    course_number: str
    section: str
    title: str
    credits: int
    professor: Optional[str] = None
    days: List[str] = []
    time: Optional[str] = None
    location: Optional[str] = None
    seats_available: int = 0
    total_seats: int = 0
    delivery_method: str = "In-Person"  # "In-Person", "Online", "Hybrid"
    
    # RateMyProfessors data
    professor_rating: Optional[float] = None
    professor_difficulty: Optional[float] = None
    would_take_again: Optional[float] = None
    
    # Matching metadata
    match_score: float = 0.0
    priority: int = 1


class RegistrationResponse(BaseModel):
    """Response containing matched courses and registration info"""
    matched_courses: List[MatchedCourse]
    paws_link: str
    term: str
    timestamp: str
    instructions: str
    total_credits: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        # Calculate total credits
        self.total_credits = sum(course.credits for course in self.matched_courses)


class CompletedCourse(BaseModel):
    """Course from student evaluation/transcript"""
    subject: str
    course_number: str
    grade: str
    term: str
