"""
Pydantic models for the YiriAi Agent API.

This module defines the data models for student preferences,
course information, professor ratings, and API responses.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ClassPreference(BaseModel):
    """Student's class preference model."""
    subject: str = Field(..., description="Subject code (e.g., 'CSC', 'MATH')")
    course_number: Optional[str] = Field(
        None, description="Course number (e.g., '1301', '2010')"
    )
    preferred_time: Optional[str] = Field(
        None, description="Preferred time slot (e.g., 'morning', 'afternoon', 'evening')"
    )
    preferred_days: Optional[list[str]] = Field(
        None, description="Preferred days (e.g., ['M', 'W', 'F'])"
    )
    min_professor_rating: Optional[float] = Field(
        None, ge=0.0, le=5.0, description="Minimum professor rating (0-5)"
    )


class StudentEvaluation(BaseModel):
    """Student's evaluation/transcript data model."""
    completed_courses: list[str] = Field(
        default_factory=list,
        description="List of completed course codes (e.g., ['CSC1301', 'MATH1113'])"
    )
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="Current GPA")
    credits_completed: Optional[int] = Field(
        None, ge=0, description="Total credits completed"
    )
    major: Optional[str] = Field(None, description="Student's major")


class StudentRequest(BaseModel):
    """Combined student request with preferences and evaluation."""
    preferences: list[ClassPreference] = Field(
        ..., description="List of class preferences"
    )
    evaluation: Optional[StudentEvaluation] = Field(
        None, description="Student evaluation data"
    )
    term: str = Field(
        ..., description="Academic term (e.g., 'Spring 2025', 'Fall 2024')"
    )


class ProfessorInfo(BaseModel):
    """Professor information from RateMyProfessors."""
    name: str = Field(..., description="Professor's full name")
    rating: Optional[float] = Field(None, description="Overall rating (0-5)")
    difficulty: Optional[float] = Field(None, description="Difficulty rating (0-5)")
    would_take_again: Optional[float] = Field(
        None, description="Percentage who would take again"
    )
    department: Optional[str] = Field(None, description="Professor's department")
    num_ratings: Optional[int] = Field(None, description="Number of ratings")


class CourseResult(BaseModel):
    """A matched course result."""
    crn: str = Field(..., description="Course Registration Number")
    subject: str = Field(..., description="Subject code")
    course_number: str = Field(..., description="Course number")
    section: str = Field(..., description="Section number")
    title: str = Field(..., description="Course title")
    credits: str = Field(..., description="Credit hours")
    days: Optional[str] = Field(None, description="Meeting days")
    time: Optional[str] = Field(None, description="Meeting time")
    location: Optional[str] = Field(None, description="Meeting location")
    instructor: Optional[str] = Field(None, description="Instructor name")
    seats_available: Optional[int] = Field(None, description="Available seats")
    professor_info: Optional[ProfessorInfo] = Field(
        None, description="Professor rating information"
    )
    match_score: float = Field(
        0.0, description="How well this course matches preferences (0-100)"
    )


class CourseSearchResponse(BaseModel):
    """Response containing matched courses."""
    success: bool = Field(..., description="Whether the search was successful")
    message: str = Field(..., description="Response message")
    term: str = Field(..., description="Academic term searched")
    courses: list[CourseResult] = Field(
        default_factory=list, description="List of matched courses"
    )
    crn_list: str = Field(
        "", description="Comma-separated list of CRNs for easy registration"
    )
    paws_registration_url: str = Field(
        "https://paws.gsu.edu/",
        description="Direct link to PAWS registration"
    )
    total_results: int = Field(0, description="Total number of results found")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    service: str = Field(..., description="Service name")
