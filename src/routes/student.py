from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from sis.connection import Connection

from ..services.student_service import StudentService
from ..utils.auth import verify_jwt_token
from ..utils.connect_parser import ConnectionParser

router = APIRouter()

@router.get("/course")
async def get_course_info(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    icloud_conn =  ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_course_timetable(icloud_conn, refresh)
    return data

@router.get("")
async def get_student_info(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):

    sis_conn = ConnectionParser.parse_connection(token, False)

    info = await StudentService.get_student_info(sis_conn, refresh)

    return info 