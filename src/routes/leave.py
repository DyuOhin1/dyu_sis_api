import json
import uuid
from datetime import date
from pathlib import Path

import aiofiles
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query, Form
from typing import List, Optional, Union

from pydantic import ValidationError, BaseModel
from sis.course.leave.constant.departments import Department
from sis.course.leave.constant.leave_type import LeaveType
from sis.course.leave.course_leave import CourseLeave
from sis.course.leave.modals.leave_data import LeaveData
from sis.course.leave.modals.leave_form_data.course_leave_form_data import CourseLeaveFormData
from sis.modals.course import CourseWithDate
from sis.modals.teacher import Teacher

from src.models.leave import LeaveRequest, CourseInfo, CourseLeaveData
from src.services.leave_service import LeaveService
from src.utils.auth import verify_jwt_token
from src.utils.connect_parser import ConnectionParser

from sis.student_information_system import StudentInformationSystem as SIS

router = APIRouter()


@router.get("/course/info")
async def get_course_info(
    start_date: Optional[date] = date.today(),
    end_date: Optional[date] = date.today(),
    token: dict = Depends(verify_jwt_token)
):
    student_id = ConnectionParser.parse_student_id(token)

    data = SIS.course_leave.info(start_date, end_date, student_id)
    return {
        "data": data
    }

@router.get("/types")
async def get_leave_types():
    return (
        {
            "id" : leave_type.value,
            "en": leave_type.name,
            "zh": leave_type.description
        }
    for leave_type in LeaveType
    )

@router.get("/department")
async def get_leave_types():
    return (
        {
            "id" : department.value,
            "en": department.name,
            "zh": department.description
        }
    for department in Department
    )

@router.post("/course")
async def create_leave(
    course_info: str = Form(...),  # ✅ 以 JSON string 形式傳遞
    leave_type: LeaveType = Form(...),
    reason: str = Form(...),
    from_dept: Optional[Department] = Form(None),
    file: Optional[UploadFile] = File(None),  # 📌 檔案上傳
    token: dict = Depends(verify_jwt_token)
):
    # 解析 JWT 取得 SIS 連線資訊
    sis_conn = ConnectionParser.parse_connection(token, False)

    if file:
        # 檔案限制 2MB 以下，並且只允許 .jpg, .jpeg, .png, .pdf .docx
        if file.content_type not in ["image/jpeg", "image/png", "application/pdf", "application/msword"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .jpg, .jpeg, .png, .pdf, .docx are allowed."
            )

        # 檢查檔案大小
        if file.content_length > 2097152:
            raise HTTPException(
                status_code=400,
                detail="File size must be less than 2MB."
            )

    # 解析 JSON 並驗證格式
    try:
        parsed_courses = json.loads(course_info)

        if not isinstance(parsed_courses, list):
            raise HTTPException(
                status_code=400,
                detail="Course info must be a list e.g. [{\"id\": \"C12345678\", \"date\": \"2021-09-01\", \"period\": 1}]"
            )

        data = [
            CourseWithDate(
                course_id=course["id"],
                course_date=date.fromisoformat(course["date"]),
                course_period=course["period"]
            )
            for course in parsed_courses
        ]
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid course info format: {str(e)}"
        )

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    TEMP_DIR = BASE_DIR / "temp"
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # 📌 如果有上傳檔案，存入 TEMP 目錄
    temp_file_path = None
    if file:
        # 產生臨時檔案名稱，且副檔名相同
        temp_file_path = TEMP_DIR / f"{uuid.uuid4()}{Path(file.filename).suffix}"
        async with aiofiles.open(temp_file_path, "wb") as f:
            await f.write(await file.read())

    # 準備請假表單
    form = CourseLeaveFormData(
        course=data,
        leave_type=leave_type,
        reason=reason,
        from_dept=from_dept,
        file=open(temp_file_path, "rb") if file else None  # ✅ 確保檔案存在才開啟
    )

    # 呼叫 SIS API
    response_data = SIS.course_leave.send(sis_conn, form)

    # ✅ 清理上傳的臨時檔案，避免長期占用空間
    if file and temp_file_path.exists():
        temp_file_path.unlink()

    return {"data": response_data}

@router.get("/{leave_id}")
async def get_leave_details(
        leave_id: str,
        get_message : bool = Query(False),
        token: dict = Depends(verify_jwt_token)
):
    sis_conn = ConnectionParser.parse_connection(token, False)
    data = SIS.course_leave.detail(sis_conn, leave_id, get_message)
    return {"data": data}

@router.get("")
async def get_leave_history(token: dict = Depends(verify_jwt_token)):
    sis_conn = ConnectionParser.parse_connection(token, False)
    data = SIS.course_leave.list(sis_conn)
    return {"data": data}

@router.delete("/{leave_id}")
async def cancel_leave(
    leave_id: str,
    token: dict = Depends(verify_jwt_token)
):
    sis_conn = ConnectionParser.parse_connection(token, False)
    data = SIS.course_leave.cancel(sis_conn, leave_id)
    return {"data": data}

@router.patch("/{leave_id}")
async def upload_leave_document(
    leave_id: str,
    file: UploadFile = File(...),
    token: dict = Depends(verify_jwt_token)
):
    sis_conn = ConnectionParser.parse_connection(token, False)
    if file:
        # 檔案限制 2MB 以下，並且只允許 .jpg, .jpeg, .png, .pdf .docx
        if file.content_type not in ["image/jpeg", "image/png", "application/pdf", "application/msword"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .jpg, .jpeg, .png, .pdf, .docx are allowed."
            )


    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    TEMP_DIR = BASE_DIR / "temp"
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # 📌 如果有上傳檔案，存入 TEMP 目錄
    temp_file_path = None
    if file:
        # 產生臨時檔案名稱，且副檔名相同
        temp_file_path = TEMP_DIR / f"{uuid.uuid4()}{Path(file.filename).suffix}"
        async with aiofiles.open(temp_file_path, "wb") as f:
            await f.write(await file.read())
    # 呼叫 SIS API
    response_data = SIS.course_leave.submit_document(sis_conn, leave_id, open(temp_file_path, "rb"))

    # ✅ 清理上傳的臨時檔案，避免長期占用空間
    if file and temp_file_path.exists():
        temp_file_path.unlink()

    return {"data": response_data}