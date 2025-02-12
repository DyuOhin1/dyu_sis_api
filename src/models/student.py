from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CourseInfo(BaseModel):
    course_id: str
    course_name: str
    credits: int
    teacher: str
    schedule: str

class StudentInfo(BaseModel):
    student_id: str
    name: str
    department: str
    grade: int
    class_name: str
    courses: List[CourseInfo] = [] 