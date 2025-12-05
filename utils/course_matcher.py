"""
Course Matcher
Matches student preferences with available courses
"""
from typing import List, Optional, Set
from datetime import datetime, time
import logging

from models import CoursePreferences, MatchedCourse, CompletedCourse

logger = logging.getLogger(__name__)


class CourseMatcher:
    """Matches courses based on student preferences"""
    
    def match_courses(
        self,
        preferences: CoursePreferences,
        available_courses: List[MatchedCourse],
        completed_courses: Optional[List[CompletedCourse]] = None
    ) -> List[MatchedCourse]:
        """
        Match available courses to student preferences
        
        Args:
            preferences: Student course preferences
            available_courses: List of available courses from PAWS
            completed_courses: Previously completed courses (to avoid duplicates)
            
        Returns:
            List of matched courses sorted by priority and match score
        """
        # Build set of completed courses
        completed_set = set()
        if completed_courses:
            completed_set = {
                f"{c.subject}{c.course_number}" 
                for c in completed_courses
            }
        
        matched = []
        
        for pref in preferences.courses:
            # Find courses matching this preference
            candidates = self._find_matching_courses(
                pref,
                available_courses,
                completed_set,
                preferences
            )
            
            # Score and rank candidates
            for course in candidates:
                score = self._calculate_match_score(course, pref, preferences)
                course.match_score = score
                course.priority = pref.priority
            
            # Sort by score and take best matches
            candidates.sort(key=lambda x: x.match_score, reverse=True)
            
            # Add top matches (limit to avoid overwhelming)
            matched.extend(candidates[:3])
        
        # Remove duplicates
        seen_crns = set()
        unique_matched = []
        for course in matched:
            if course.crn not in seen_crns:
                seen_crns.add(course.crn)
                unique_matched.append(course)
        
        # Check for time conflicts if requested
        if preferences.avoid_time_conflicts:
            unique_matched = self._resolve_conflicts(unique_matched)
        
        # Check credit limit
        if preferences.max_credits:
            unique_matched = self._limit_credits(unique_matched, preferences.max_credits)
        
        # Sort by priority then score
        unique_matched.sort(key=lambda x: (x.priority, -x.match_score))
        
        logger.info(f"Matched {len(unique_matched)} courses after filtering")
        return unique_matched
    
    def _find_matching_courses(
        self,
        preference,
        available_courses: List[MatchedCourse],
        completed_set: Set[str],
        preferences: CoursePreferences
    ) -> List[MatchedCourse]:
        """Find courses matching a specific preference"""
        matches = []
        
        for course in available_courses:
            course_code = f"{course.subject}{course.course_number}"
            
            # Skip if already completed
            if course_code in completed_set:
                continue
            
            # Check subject match
            if course.subject != preference.subject:
                continue
            
            # Check course number if specified
            if preference.course_number and course.course_number != preference.course_number:
                continue
            
            # Check online preference
            if preference.online_only and course.delivery_method != "Online":
                continue
            
            # Check excluded professors
            if course.professor and any(
                excl.lower() in course.professor.lower() 
                for excl in preference.exclude_professors
            ):
                continue
            
            # Check seats available
            if course.seats_available <= 0:
                continue
            
            matches.append(course)
        
        return matches
    
    def _calculate_match_score(
        self,
        course: MatchedCourse,
        preference,
        preferences: CoursePreferences
    ) -> float:
        """
        Calculate how well a course matches preferences
        
        Returns:
            Score from 0-100
        """
        score = 50.0  # Base score
        
        # Exact course number match
        if preference.course_number and course.course_number == preference.course_number:
            score += 20
        
        # Online preference bonus
        if preferences.prefer_online and course.delivery_method == "Online":
            score += 10
        elif not preferences.prefer_online and course.delivery_method == "In-Person":
            score += 5
        
        # Time preference matching
        if preference.preferred_times and course.days and course.time:
            time_match = self._check_time_match(course, preference.preferred_times)
            if time_match:
                score += 15
        
        # Seats availability bonus (prefer courses with more seats)
        if course.total_seats > 0:
            availability_ratio = course.seats_available / course.total_seats
            score += availability_ratio * 10
        
        # Professor rating bonus
        if course.professor_rating:
            # Rating is 0-5, normalize to 0-15
            score += (course.professor_rating / 5.0) * 15
        
        # Would take again bonus
        if course.would_take_again:
            score += (course.would_take_again / 100.0) * 5
        
        # Difficulty penalty (prefer easier courses slightly)
        if course.professor_difficulty:
            # Difficulty is 0-5, penalize harder courses slightly
            score -= (course.professor_difficulty / 5.0) * 3
        
        return min(100.0, max(0.0, score))
    
    def _check_time_match(self, course: MatchedCourse, preferred_times) -> bool:
        """Check if course time matches preferred times"""
        # Simple day matching for now
        if not course.days:
            return False
        
        for pref_time in preferred_times:
            # Check if days overlap
            if any(day in course.days for day in pref_time.days):
                return True
        
        return False
    
    def _resolve_conflicts(self, courses: List[MatchedCourse]) -> List[MatchedCourse]:
        """
        Remove courses with time conflicts
        Keep higher priority/score courses
        """
        result = []
        
        for course in courses:
            has_conflict = False
            
            for existing in result:
                if self._has_time_conflict(course, existing):
                    # Keep the higher priority/score course
                    if (course.priority < existing.priority or 
                        (course.priority == existing.priority and 
                         course.match_score > existing.match_score)):
                        # Remove existing, add new
                        result.remove(existing)
                        break
                    else:
                        # Skip this course
                        has_conflict = True
                        break
            
            if not has_conflict:
                result.append(course)
        
        return result
    
    def _has_time_conflict(self, course1: MatchedCourse, course2: MatchedCourse) -> bool:
        """Check if two courses have a time conflict"""
        # If either is online, no conflict
        if course1.delivery_method == "Online" or course2.delivery_method == "Online":
            return False
        
        # Check if they share any days
        if not course1.days or not course2.days:
            return False
        
        shared_days = set(course1.days) & set(course2.days)
        if not shared_days:
            return False
        
        # If they share days and have time info, would need to parse times
        # For simplicity, assume conflict if they share days
        # In production, you'd parse time strings and check actual overlap
        
        return True
    
    def _limit_credits(self, courses: List[MatchedCourse], max_credits: int) -> List[MatchedCourse]:
        """Limit total credits to max_credits"""
        result = []
        total_credits = 0
        
        for course in courses:
            if total_credits + course.credits <= max_credits:
                result.append(course)
                total_credits += course.credits
            else:
                logger.info(f"Credit limit reached, excluding {course.subject}{course.course_number}")
        
        return result
