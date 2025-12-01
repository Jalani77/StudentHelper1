# StudentHelper1 - YiriAi Agent

A Python FastAPI agent that helps GSU (Georgia State University) students find and select courses based on their preferences and evaluations.

## Overview

**YiriAi** is a course selection assistant that:
- Accepts student evaluations and class preferences
- Scrapes GSU PAWS class schedule for open courses
- Pulls professor information from RateMyProfessors
- Outputs matching courses with CRNs for easy registration

**Important**: YiriAi only automates course *selection*, not registration. Students log into PAWS themselves and paste the CRNs to register. No password handling by YiriAi means no credential risk.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn yiriai_agent.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- `GET /` - Root health check
- `GET /health` - Health status

### Course Search
- `POST /api/v1/search` - Search for courses matching preferences
- `POST /api/v1/quick-search` - Quick search by subject
- `GET /api/v1/subjects` - List available subjects

## Usage Example

### Search for Courses

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": [
      {
        "subject": "CSC",
        "course_number": "1301",
        "preferred_time": "morning",
        "min_professor_rating": 4.0
      }
    ],
    "evaluation": {
      "completed_courses": ["MATH1113"],
      "gpa": 3.5,
      "major": "Computer Science"
    },
    "term": "Spring 2025"
  }'
```

### Quick Search

```bash
curl -X POST "http://localhost:8000/api/v1/quick-search?subject=CSC&term=Spring%202025"
```

## Response Format

The API returns a `CourseSearchResponse` containing:
- `success`: Whether the search was successful
- `message`: Response message
- `term`: Academic term searched
- `courses`: List of matched courses with:
  - CRN (Course Registration Number)
  - Course details (subject, number, title, credits)
  - Schedule (days, time, location)
  - Professor info (name, rating, difficulty)
  - Match score (0-100)
- `crn_list`: Comma-separated CRNs for easy copy/paste
- `paws_registration_url`: Direct link to PAWS

## How to Register

1. Run YiriAi to get your recommended courses
2. Copy the CRN list from the response
3. Go to [PAWS](https://paws.gsu.edu/)
4. Log in with your GSU credentials
5. Navigate to Registration
6. Paste the CRNs and submit

## API Documentation

When the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
yiriai_agent/
├── __init__.py          # Package initialization
├── main.py              # FastAPI application
├── models.py            # Pydantic data models
├── scraper.py           # GSU PAWS schedule scraper
├── professor_service.py # RateMyProfessors integration
└── matcher.py           # Course matching logic
```

## License

MIT License