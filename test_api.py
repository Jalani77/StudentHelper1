"""
Test script for YiriAi
Run this to test the API locally
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_upload_preferences():
    """Test the main upload preferences endpoint"""
    print("Testing upload preferences...")
    
    # Prepare test data
    preferences = {
        "courses": [
            {"subject": "CSC", "course_number": "2510", "priority": 1},
            {"subject": "MATH", "course_number": "2211", "priority": 1}
        ],
        "subjects": ["CSC", "MATH"],
        "max_credits": 15
    }
    
    transcript = [
        {"subject": "CSC", "course_number": "1301", "grade": "A", "term": "202308"},
        {"subject": "MATH", "course_number": "1111", "grade": "B", "term": "202308"}
    ]
    
    # Create temporary files
    prefs_data = json.dumps(preferences).encode()
    eval_data = json.dumps(transcript).encode()
    
    files = {
        'prefs_file': ('preferences.json', prefs_data, 'application/json'),
        'eval_file': ('transcript.json', eval_data, 'application/json')
    }
    
    params = {
        'term': '202508',
        'include_ratings': True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/upload-preferences",
            files=files,
            params=params,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Matched {len(result['matched_courses'])} courses")
            print(f"Total credits: {result['total_credits']}")
            print(f"PAWS link: {result['paws_link']}")
            
            if result['matched_courses']:
                print("\nFirst matched course:")
                course = result['matched_courses'][0]
                print(f"  CRN: {course['crn']}")
                print(f"  Course: {course['subject']} {course['course_number']}")
                print(f"  Title: {course['title']}")
                print(f"  Professor: {course.get('professor', 'TBA')}")
                if course.get('professor_rating'):
                    print(f"  Rating: {course['professor_rating']}/5.0")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print()


def test_search_courses():
    """Test the course search endpoint"""
    print("Testing course search...")
    
    params = {
        'term': '202508',
        'subject': 'CSC'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/search-courses", params=params, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['count']} courses")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print()


def test_professor_rating():
    """Test the professor rating endpoint"""
    print("Testing professor rating...")
    
    professor_name = "John Smith"
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/professor-rating/{professor_name}",
            timeout=15
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Rating: {result.get('rating', 'N/A')}")
            print(f"Difficulty: {result.get('difficulty', 'N/A')}")
            print(f"Would take again: {result.get('would_take_again', 'N/A')}%")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print()


if __name__ == "__main__":
    print("=== YiriAi API Test Suite ===\n")
    
    # Check if server is running
    try:
        test_health_check()
        
        # Uncomment to test other endpoints
        # Note: These require actual GSU PAWS access and may take time
        # test_upload_preferences()
        # test_search_courses()
        # test_professor_rating()
        
        print("Test complete! Uncomment other tests to run full suite.")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Make sure the server is running: python main.py")
