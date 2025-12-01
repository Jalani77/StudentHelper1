"""Tests for the YiriAi Agent API."""

import pytest
from fastapi.testclient import TestClient

from yiriai_agent.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns healthy status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "YiriAi Agent"
        assert "version" in data

    def test_health_endpoint(self, client):
        """Test the health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestSubjectsEndpoint:
    """Tests for the subjects endpoint."""

    def test_get_subjects(self, client):
        """Test getting available subjects."""
        response = client.get("/api/v1/subjects")
        assert response.status_code == 200
        data = response.json()
        assert "subjects" in data
        assert len(data["subjects"]) > 0
        # Check that CSC is in the list
        codes = [s["code"] for s in data["subjects"]]
        assert "CSC" in codes
        assert "MATH" in codes


class TestCourseSearch:
    """Tests for course search functionality."""

    def test_search_courses_csc(self, client):
        """Test searching for CSC courses."""
        request_data = {
            "preferences": [{"subject": "CSC"}],
            "term": "Spring 2025",
        }
        response = client.post("/api/v1/search", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["term"] == "Spring 2025"
        assert len(data["courses"]) > 0
        assert data["paws_registration_url"] == "https://paws.gsu.edu/"

    def test_search_courses_with_number(self, client):
        """Test searching for a specific course number."""
        request_data = {
            "preferences": [{"subject": "CSC", "course_number": "1301"}],
            "term": "Spring 2025",
        }
        response = client.post("/api/v1/search", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        for course in data["courses"]:
            assert course["course_number"] == "1301"

    def test_search_courses_with_preferences(self, client):
        """Test searching with full preferences."""
        request_data = {
            "preferences": [
                {
                    "subject": "CSC",
                    "preferred_time": "morning",
                    "preferred_days": ["M", "W", "F"],
                    "min_professor_rating": 4.0,
                }
            ],
            "evaluation": {
                "completed_courses": ["MATH1113"],
                "gpa": 3.5,
                "major": "Computer Science",
            },
            "term": "Spring 2025",
        }
        response = client.post("/api/v1/search", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["courses"]) > 0
        # Check that courses have match scores
        for course in data["courses"]:
            assert "match_score" in course

    def test_search_courses_crn_list(self, client):
        """Test that CRN list is generated correctly."""
        request_data = {
            "preferences": [{"subject": "CSC"}],
            "term": "Spring 2025",
        }
        response = client.post("/api/v1/search", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "crn_list" in data
        # CRN list should contain comma-separated values
        if data["courses"]:
            crns = [c["crn"] for c in data["courses"]]
            for crn in crns:
                assert crn in data["crn_list"]

    def test_search_courses_empty_preferences(self, client):
        """Test that empty preferences returns error."""
        request_data = {"preferences": [], "term": "Spring 2025"}
        response = client.post("/api/v1/search", json=request_data)
        assert response.status_code == 400

    def test_search_multiple_subjects(self, client):
        """Test searching for multiple subjects."""
        request_data = {
            "preferences": [{"subject": "CSC"}, {"subject": "MATH"}],
            "term": "Spring 2025",
        }
        response = client.post("/api/v1/search", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should have courses from both subjects
        subjects = set(c["subject"] for c in data["courses"])
        assert "CSC" in subjects
        assert "MATH" in subjects


class TestQuickSearch:
    """Tests for quick search functionality."""

    def test_quick_search(self, client):
        """Test quick search by subject."""
        response = client.post("/api/v1/quick-search?subject=CSC&term=Spring%202025")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        for course in data["courses"]:
            assert course["subject"] == "CSC"

    def test_quick_search_with_course_number(self, client):
        """Test quick search with course number."""
        response = client.post(
            "/api/v1/quick-search?subject=CSC&course_number=1301&term=Spring%202025"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        for course in data["courses"]:
            assert course["course_number"] == "1301"


class TestProfessorInfo:
    """Tests for professor information integration."""

    def test_courses_have_professor_info(self, client):
        """Test that courses include professor information."""
        request_data = {
            "preferences": [{"subject": "CSC"}],
            "term": "Spring 2025",
        }
        response = client.post("/api/v1/search", json=request_data)
        assert response.status_code == 200
        data = response.json()
        # At least some courses should have professor info
        courses_with_prof_info = [
            c for c in data["courses"] if c.get("professor_info")
        ]
        assert len(courses_with_prof_info) > 0
        # Check professor info structure
        for course in courses_with_prof_info:
            prof_info = course["professor_info"]
            assert "name" in prof_info
            assert "rating" in prof_info
