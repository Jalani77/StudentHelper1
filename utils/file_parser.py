"""
File Parser
Parses student evaluation and preference files
"""
import json
import pandas as pd
from typing import List, Optional, Dict, Any
import logging
from io import BytesIO

from models import CoursePreferences, CoursePreference, CompletedCourse, TimeSlot

logger = logging.getLogger(__name__)


class FileParser:
    """Parses uploaded student files"""
    
    def parse_evaluation(self, content: bytes, filename: str) -> List[CompletedCourse]:
        """
        Parse student evaluation/transcript file
        
        Supported formats: CSV, Excel, JSON, TXT
        
        Args:
            content: File content as bytes
            filename: Original filename
            
        Returns:
            List of CompletedCourse objects
        """
        try:
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext in ['xlsx', 'xls']:
                return self._parse_excel_evaluation(content)
            elif file_ext == 'csv':
                return self._parse_csv_evaluation(content)
            elif file_ext == 'json':
                return self._parse_json_evaluation(content)
            elif file_ext == 'txt':
                return self._parse_text_evaluation(content)
            else:
                logger.warning(f"Unsupported evaluation file format: {file_ext}")
                return []
                
        except Exception as e:
            logger.error(f"Error parsing evaluation file: {str(e)}")
            return []
    
    def parse_preferences(self, content: bytes, filename: str) -> CoursePreferences:
        """
        Parse course preferences file
        
        Supported formats: JSON, CSV, Excel
        
        Args:
            content: File content as bytes
            filename: Original filename
            
        Returns:
            CoursePreferences object
        """
        try:
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext in ['xlsx', 'xls']:
                return self._parse_excel_preferences(content)
            elif file_ext == 'csv':
                return self._parse_csv_preferences(content)
            elif file_ext == 'json':
                return self._parse_json_preferences(content)
            else:
                logger.warning(f"Unsupported preferences file format: {file_ext}")
                return self._default_preferences()
                
        except Exception as e:
            logger.error(f"Error parsing preferences file: {str(e)}")
            return self._default_preferences()
    
    def _parse_excel_evaluation(self, content: bytes) -> List[CompletedCourse]:
        """Parse Excel evaluation file"""
        df = pd.read_excel(BytesIO(content))
        courses = []
        
        # Expected columns: Subject, Course Number, Grade, Term
        # Try common column name variations
        col_map = self._map_columns(df.columns, {
            'subject': ['subject', 'subj', 'dept', 'department'],
            'course_number': ['course number', 'course', 'number', 'course_num'],
            'grade': ['grade', 'final grade', 'letter grade'],
            'term': ['term', 'semester', 'period']
        })
        
        for _, row in df.iterrows():
            try:
                course = CompletedCourse(
                    subject=str(row[col_map['subject']]).strip().upper(),
                    course_number=str(row[col_map['course_number']]).strip(),
                    grade=str(row[col_map['grade']]).strip().upper(),
                    term=str(row[col_map['term']]).strip()
                )
                courses.append(course)
            except Exception as e:
                logger.warning(f"Error parsing row: {e}")
                continue
        
        return courses
    
    def _parse_csv_evaluation(self, content: bytes) -> List[CompletedCourse]:
        """Parse CSV evaluation file"""
        df = pd.read_csv(BytesIO(content))
        return self._parse_excel_evaluation(content)  # Reuse Excel parser
    
    def _parse_json_evaluation(self, content: bytes) -> List[CompletedCourse]:
        """Parse JSON evaluation file"""
        data = json.loads(content.decode('utf-8'))
        courses = []
        
        # Expect array of course objects
        if isinstance(data, list):
            for item in data:
                try:
                    course = CompletedCourse(**item)
                    courses.append(course)
                except Exception as e:
                    logger.warning(f"Error parsing course: {e}")
                    continue
        
        return courses
    
    def _parse_text_evaluation(self, content: bytes) -> List[CompletedCourse]:
        """Parse plain text evaluation file"""
        # Simple parser for text transcripts
        # Expected format: "SUBJECT COURSE_NUM GRADE TERM" per line
        text = content.decode('utf-8')
        courses = []
        
        for line in text.split('\n'):
            parts = line.strip().split()
            if len(parts) >= 4:
                try:
                    course = CompletedCourse(
                        subject=parts[0].upper(),
                        course_number=parts[1],
                        grade=parts[2].upper(),
                        term=parts[3]
                    )
                    courses.append(course)
                except Exception:
                    continue
        
        return courses
    
    def _parse_excel_preferences(self, content: bytes) -> CoursePreferences:
        """Parse Excel preferences file"""
        df = pd.read_excel(BytesIO(content))
        
        courses = []
        subjects = set()
        
        # Expected columns: Subject, Course Number (optional), Priority, Online Only, etc.
        col_map = self._map_columns(df.columns, {
            'subject': ['subject', 'subj', 'dept'],
            'course_number': ['course number', 'course', 'number'],
            'priority': ['priority', 'pref', 'preference'],
            'online_only': ['online only', 'online', 'online_only']
        })
        
        for _, row in df.iterrows():
            try:
                subject = str(row[col_map['subject']]).strip().upper()
                subjects.add(subject)
                
                course_num = None
                if 'course_number' in col_map and pd.notna(row.get(col_map['course_number'])):
                    course_num = str(row[col_map['course_number']]).strip()
                
                priority = 1
                if 'priority' in col_map and pd.notna(row.get(col_map['priority'])):
                    priority = int(row[col_map['priority']])
                
                online_only = False
                if 'online_only' in col_map and pd.notna(row.get(col_map['online_only'])):
                    online_only = bool(row[col_map['online_only']])
                
                pref = CoursePreference(
                    subject=subject,
                    course_number=course_num,
                    priority=priority,
                    online_only=online_only
                )
                courses.append(pref)
            except Exception as e:
                logger.warning(f"Error parsing preference row: {e}")
                continue
        
        return CoursePreferences(
            courses=courses,
            subjects=list(subjects)
        )
    
    def _parse_csv_preferences(self, content: bytes) -> CoursePreferences:
        """Parse CSV preferences file"""
        df = pd.read_csv(BytesIO(content))
        # Convert to bytes for Excel parser reuse
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return self._parse_excel_preferences(buffer.getvalue())
    
    def _parse_json_preferences(self, content: bytes) -> CoursePreferences:
        """Parse JSON preferences file"""
        data = json.loads(content.decode('utf-8'))
        
        # Support direct CoursePreferences format or array of courses
        if isinstance(data, dict) and 'courses' in data:
            return CoursePreferences(**data)
        elif isinstance(data, list):
            # Array of course preferences
            courses = []
            subjects = set()
            for item in data:
                try:
                    pref = CoursePreference(**item)
                    courses.append(pref)
                    subjects.add(pref.subject)
                except Exception as e:
                    logger.warning(f"Error parsing preference: {e}")
                    continue
            
            return CoursePreferences(
                courses=courses,
                subjects=list(subjects)
            )
        
        return self._default_preferences()
    
    def _map_columns(self, columns: List[str], mapping: Dict[str, List[str]]) -> Dict[str, str]:
        """Map actual column names to expected names"""
        result = {}
        columns_lower = [c.lower() for c in columns]
        
        for key, variations in mapping.items():
            for variation in variations:
                if variation.lower() in columns_lower:
                    idx = columns_lower.index(variation.lower())
                    result[key] = columns[idx]
                    break
        
        return result
    
    def _default_preferences(self) -> CoursePreferences:
        """Return default empty preferences"""
        return CoursePreferences(courses=[], subjects=[])
