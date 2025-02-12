from pydantic import BaseModel
from typing import Optional, List

class GraduationRequirement(BaseModel):
    student_id: str
    english_qualified: bool
    chinese_qualified: bool
    computer_qualified: bool
    workplace_exp_qualified: bool
    total_credits: int
    required_credits: int
    elective_credits: int
    is_qualified: bool 