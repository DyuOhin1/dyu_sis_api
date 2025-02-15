from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, BinaryIO

from sis.course.leave.constant.departments import Department
from sis.course.leave.constant.leave_type import LeaveType
from sis.course.leave.modals.leave_form_data.course_leave_form_data import CourseLeaveFormData
from sis.modals.course import Course

from src.models.student import CourseInfo


class LeaveRequest(BaseModel):
    leave_type: LeaveType
    course: List[CourseInfo]
    reason: str
    from_dept: Optional[Department] = None

class CourseLeaveData(BaseModel):
    id : str
    date : date
    period : int