from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class LeaveRequest(BaseModel):
    leave_type: str
    start_date: datetime
    end_date: datetime
    reason: str
    document_ids: List[str] = []

class LeaveResponse(BaseModel):
    leave_id: str
    student_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    leave_request: LeaveRequest 