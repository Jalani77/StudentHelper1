"""
Additional API endpoints for YiriAi frontend
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from models import (
    UserCreate, UserLogin, Token, User,
    CoursePreferencesInput, ScheduleResult, 
    SaveScheduleRequest, SearchCoursesRequest
)

router = APIRouter(prefix="/api", tags=["api"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings (move to config later)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Mock user database (replace with real DB)
fake_users_db = {}


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Get current user from token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if user_id not in fake_users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        return fake_users_db[user_id]
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")


@router.post("/auth/register", response_model=Token)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    for existing_user in fake_users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = str(len(fake_users_db) + 1)
    hashed_password = hash_password(user.password)
    
    user_data = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "created_at": datetime.now()
    }
    
    fake_users_db[user_id] = user_data
    
    # Create access token
    access_token = create_access_token({"sub": user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user.name,
            "email": user.email
        }
    }


@router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user"""
    # Find user by email
    user = None
    for uid, u in fake_users_db.items():
        if u["email"] == credentials.email:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token({"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }


@router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "created_at": current_user["created_at"]
    }


@router.post("/upload-eval")
async def upload_eval(
    file_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and parse degree evaluation
    
    TODO: Implement actual file parsing
    """
    # Mock parsed data for now
    return {
        "success": True,
        "parsed_eval": {
            "remaining_credits": 45,
            "courses": [
                {"code": "CSC 1301", "title": "Principles of Computer Science I", "credits": 3},
                {"code": "MATH 2211", "title": "Calculus I", "credits": 4},
                {"code": "ENGL 1102", "title": "English Composition II", "credits": 3},
                {"code": "HIST 2110", "title": "Survey of United States History I", "credits": 3},
            ]
        }
    }


@router.post("/generate-schedule", response_model=ScheduleResult)
async def generate_schedule(
    preferences: CoursePreferencesInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate schedule based on preferences
    
    TODO: Connect to real PAWS scraper and course matcher
    """
    # Mock schedule for now
    return {
        "fit_score": 92,
        "total_credits": 15,
        "courses": [
            {
                "crn": "12345",
                "code": "CSC 1301",
                "title": "Principles of Computer Science I",
                "credits": 3,
                "section": "001",
                "days": "MWF",
                "time": "10:00 AM - 10:50 AM",
                "location": "Classroom South 301",
                "campus": "Atlanta",
                "instructor": "Dr. Sarah Johnson",
                "seats_available": 5,
                "seats_total": 30,
                "modality": "In-Person",
                "professor_rating": {
                    "rating": 4.5,
                    "num_ratings": 42,
                    "difficulty": 3.2
                },
                "match_reasons": [
                    "Matches your preferred days (MWF)",
                    "Within your time range (9 AM - 5 PM)",
                    "Highly rated professor"
                ],
                "match_score": 92.0
            },
            {
                "crn": "23456",
                "code": "MATH 2211",
                "title": "Calculus I",
                "credits": 4,
                "section": "002",
                "days": "TR",
                "time": "2:00 PM - 3:15 PM",
                "location": "Langdale Hall 415",
                "campus": "Atlanta",
                "instructor": "Prof. Michael Chen",
                "seats_available": 12,
                "seats_total": 35,
                "modality": "In-Person",
                "professor_rating": {
                    "rating": 4.2,
                    "num_ratings": 38,
                    "difficulty": 3.8
                },
                "match_reasons": [
                    "Within your time range",
                    "No schedule conflicts"
                ],
                "match_score": 85.0
            }
        ]
    }


@router.post("/schedules/save")
async def save_schedule(
    request: SaveScheduleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Save a schedule for later"""
    # TODO: Save to database
    return {
        "success": True,
        "schedule_id": 1,
        "message": "Schedule saved successfully"
    }


@router.get("/schedules")
async def get_schedules(current_user: dict = Depends(get_current_user)):
    """Get all saved schedules for current user"""
    # TODO: Get from database
    return {
        "schedules": [
            {
                "id": 1,
                "name": "Spring 2025 - Preferred",
                "created_at": "2025-01-15T10:30:00",
                "fit_score": 92,
                "total_credits": 15,
                "course_count": 4,
                "courses": [
                    {"code": "CSC 1301", "credits": 3, "crn": "12345"},
                    {"code": "MATH 2211", "credits": 4, "crn": "23456"},
                    {"code": "ENGL 1102", "credits": 3, "crn": "34567"},
                    {"code": "HIST 2110", "credits": 3, "crn": "45678"}
                ]
            }
        ]
    }


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a saved schedule"""
    # TODO: Delete from database
    return {"success": True, "message": "Schedule deleted"}


@router.post("/search-courses")
async def search_courses(
    request: SearchCoursesRequest,
    current_user: dict = Depends(get_current_user)
):
    """Search for courses"""
    # TODO: Connect to PAWS scraper
    return {
        "courses": [],
        "total": 0,
        "message": "Search not yet implemented"
    }


@router.get("/professor-rating/{name}")
async def get_professor_rating(
    name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get professor rating from RateMyProfessors"""
    # TODO: Connect to RMP scraper
    return {
        "name": name,
        "rating": 4.5,
        "num_ratings": 42,
        "difficulty": 3.2,
        "would_take_again": 85
    }
