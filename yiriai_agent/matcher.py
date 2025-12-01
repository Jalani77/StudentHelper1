"""
Course matching service.

This module handles matching courses to student preferences
and calculating match scores.
"""

from typing import Optional

from .models import ClassPreference, CourseResult, StudentEvaluation


class CourseMatcher:
    """Service for matching courses to student preferences."""

    def calculate_match_score(
        self,
        course: CourseResult,
        preference: ClassPreference,
        evaluation: Optional[StudentEvaluation] = None,
    ) -> float:
        """
        Calculate how well a course matches student preferences.

        Args:
            course: The course to evaluate
            preference: Student's preferences for this course
            evaluation: Optional student evaluation data

        Returns:
            Match score from 0 to 100
        """
        score = 0.0
        max_score = 0.0

        # Base score for subject match (required, always matches at this point)
        score += 25.0
        max_score += 25.0

        # Course number match
        max_score += 20.0
        if preference.course_number:
            if course.course_number == preference.course_number:
                score += 20.0
        else:
            # No specific course number preference, give partial credit
            score += 10.0

        # Time preference match
        max_score += 20.0
        if preference.preferred_time and course.time:
            time_score = self._calculate_time_match(
                course.time, preference.preferred_time
            )
            score += time_score * 20.0
        else:
            score += 10.0  # Neutral if no preference

        # Day preference match
        max_score += 15.0
        if preference.preferred_days and course.days:
            day_score = self._calculate_day_match(course.days, preference.preferred_days)
            score += day_score * 15.0
        else:
            score += 7.5  # Neutral if no preference

        # Professor rating match
        max_score += 20.0
        if preference.min_professor_rating and course.professor_info:
            if course.professor_info.rating:
                if course.professor_info.rating >= preference.min_professor_rating:
                    # Bonus for exceeding minimum
                    rating_bonus = min(
                        (course.professor_info.rating - preference.min_professor_rating)
                        / 2.0,
                        1.0,
                    )
                    score += 15.0 + (rating_bonus * 5.0)
                else:
                    # Below minimum, but still give some credit
                    score += (
                        course.professor_info.rating
                        / preference.min_professor_rating
                        * 10.0
                    )
        elif course.professor_info and course.professor_info.rating:
            # No minimum preference, but we have rating data
            score += (course.professor_info.rating / 5.0) * 15.0
        else:
            score += 10.0  # Neutral if no data

        # Normalize to 0-100 scale
        if max_score > 0:
            normalized_score = (score / max_score) * 100
        else:
            normalized_score = 50.0

        return round(normalized_score, 1)

    def _calculate_time_match(self, course_time: str, preferred_time: str) -> float:
        """
        Calculate time preference match score.

        Args:
            course_time: Course meeting time (e.g., '9:00 AM - 9:50 AM')
            preferred_time: Preferred time slot ('morning', 'afternoon', 'evening')

        Returns:
            Match score from 0.0 to 1.0
        """
        preferred = preferred_time.lower()
        time_lower = course_time.lower()

        # Determine what time of day the course is
        is_morning = any(
            x in time_lower for x in ["8:", "9:", "10:", "11:"]
        ) and "am" in time_lower
        is_afternoon = (
            "12:" in time_lower
            or ("1:" in time_lower and "pm" in time_lower)
            or ("2:" in time_lower and "pm" in time_lower)
            or ("3:" in time_lower and "pm" in time_lower)
            or ("4:" in time_lower and "pm" in time_lower)
        )
        is_evening = any(
            x in time_lower for x in ["5:", "6:", "7:", "8:", "9:"]
        ) and "pm" in time_lower

        if preferred == "morning" and is_morning:
            return 1.0
        elif preferred == "afternoon" and is_afternoon:
            return 1.0
        elif preferred == "evening" and is_evening:
            return 1.0
        elif preferred == "morning" and is_afternoon:
            return 0.5  # Close enough
        elif preferred == "afternoon" and (is_morning or is_evening):
            return 0.5
        else:
            return 0.25

    def _calculate_day_match(
        self, course_days: str, preferred_days: list[str]
    ) -> float:
        """
        Calculate day preference match score.

        Args:
            course_days: Course meeting days (e.g., 'MWF', 'TR')
            preferred_days: List of preferred days (e.g., ['M', 'W', 'F'])

        Returns:
            Match score from 0.0 to 1.0
        """
        course_days_upper = course_days.upper()
        preferred_set = set(d.upper() for d in preferred_days)

        # Check overlap
        course_day_set = set(course_days_upper)
        overlap = len(course_day_set.intersection(preferred_set))
        total_course_days = len(course_day_set)

        if total_course_days == 0:
            return 0.5

        return overlap / total_course_days

    def filter_by_prerequisites(
        self,
        courses: list[CourseResult],
        evaluation: Optional[StudentEvaluation],
    ) -> list[CourseResult]:
        """
        Filter courses based on completed prerequisites.

        Note: This is a simplified implementation. In production,
        this would check actual prerequisite chains.
        """
        if not evaluation or not evaluation.completed_courses:
            return courses

        # For demonstration, we just return all courses
        # In production, this would check prerequisite requirements
        return courses


# Create a singleton instance
course_matcher = CourseMatcher()
