from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, Query
from icloud.personal.constants.lang import Lang

from src.models.GraduationType import GraduationType
from src.services.graduation_service import GraduationService
from src.services.student_service import StudentService
from src.utils.auth import verify_jwt_token
from src.utils.connect_parser import ConnectionParser

router = APIRouter(prefix="")

@router.get("")
async def get_student_info(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):

    sis_conn = ConnectionParser.parse_connection(token, False)

    info = await StudentService.get_student_info(sis_conn, refresh)

    return info


@router.get("/semester")
async def get_student_semester(
        refresh: bool = Query(False, description="強制更新快取"),
        token: dict = Depends(verify_jwt_token)
):
    """
    sdsds

    Args:
        refresh: 是否強制更新快取
        token: JWT token
    """
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_student_semester(
        icloud_conn,
        refresh,
    )
    return data

@router.get("/course")
async def get_course_info(
    refresh: bool = Query(False, description="強制更新快取"),
    year: Optional[str] = Query(None, description="學年 (例如: 112)"),
    seme: Optional[str] = Query(None, description="學期 (1 或 2)"),
    token: dict = Depends(verify_jwt_token)
):
    """
    取得課程資訊
    
    Args:
        refresh: 是否強制更新快取
        year: 學年，例如：112
        seme: 學期，1 或 2
        token: JWT token
    """
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_course_timetable(
        icloud_conn,
        refresh,
        year=year,
        seme=seme
    )
    return data

@router.get("/graduation")
async def get_course_pdf(
    graduation_type: GraduationType,
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    sis_conn = ConnectionParser.parse_connection(token, False)
    data = await GraduationService.get_graduation(sis_conn, graduation_type, refresh)

    return data

@router.get("/course/warning")
async def get_course_warning(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    sis_conn = ConnectionParser.parse_connection(token, False)

    data = await StudentService.get_course_warning(
        sis_conn,
        refresh
    )

    return data

# 其他個人資訊路由
@router.get("/barcode")
async def get_barcode(
    token: dict = Depends(verify_jwt_token)
):
    sis_conn = ConnectionParser.parse_connection(token, False)
    data = await StudentService.get_barcode(sis_conn)
    return data


@router.get("/image")
async def get_image(
    token: dict = Depends(verify_jwt_token)
):
    sis_conn = ConnectionParser.parse_connection(token, False)
    data = await StudentService.get_personal_image(sis_conn)
    return data

@router.get("/injury")
async def get_injury(
        refresh: bool = Query(False, description="強制更新快取"),
        token: dict = Depends(verify_jwt_token)
):
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_injury(icloud_conn, refresh)
    return data

@router.get("/military")
async def get_military(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_military(icloud_conn, refresh)
    return data

@router.get("/advisors")
async def get_advisors(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_advisors(icloud_conn, refresh)
    return data

@router.get("/rewards-and-penalties")
async def get_rewards_and_penalties(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_rewards_and_penalties(icloud_conn, refresh)
    return data

@router.get("/enrollment")
async def get_enrollment(
    lang : Lang = Lang.ZH_TW,
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_enrollment(icloud_conn, lang, refresh)
    return data

@router.get("/scholarship")
async def get_scholarship(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_scholarship(icloud_conn, refresh)
    return data


@router.get("/printer-point")
async def get_printer_point(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_printer_point(icloud_conn, refresh)
    return data

@router.get("/dorm")
async def get_dorm(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    icloud_conn = ConnectionParser.parse_connection(token, True)
    data = await StudentService.get_dorm(icloud_conn, refresh)
    return data