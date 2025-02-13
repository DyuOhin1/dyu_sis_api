from enum import Enum
from typing import Optional, Dict

from fastapi import APIRouter, Depends, Query

from ..services.student_service import StudentService
from ..utils.auth import verify_jwt_token
from ..utils.connect_parser import ConnectionParser

router = APIRouter(prefix="")

@router.get("/graduation")
async def get_graduation_overview_pdf(
    token: dict = Depends(verify_jwt_token)
):
    pass

@router.get("/course")
async def get_course_list_pdf(
    year: Optional[str] = Query(None, description="學年 (例如: 112)"),
    semester: Optional[str] = Query(None, description="學期 (1 或 2)"),
    token: dict = Depends(verify_jwt_token)
):
    pass

@router.get("/enrollment")
async def get_proof_or_enrollment_pdf(
    year: Optional[str] = Query(None, description="學年 (例如: 112)"),
    semester: Optional[str] = Query(None, description="學期 (1 或 2)"),
    token: dict = Depends(verify_jwt_token)
):
    pass