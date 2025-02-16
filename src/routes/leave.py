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
from starlette import status

from src.models.leave import LeaveRequest, CourseInfo, CourseLeaveData
from src.services.leave_service import LeaveService
from src.utils.auth import verify_jwt_token
from src.utils.connect_parser import ConnectionParser

from sis.student_information_system import StudentInformationSystem as SIS

from src.utils.exception import UnsupportedFileTypeException, OutOfFileSizeException, InvalidFormatException

router = APIRouter()
@router.get("/types")
async def get_leave_types():
    try:
        data = await LeaveService.get_leave_types()

        return {
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/departments")
async def get_school_departments():
    try:
        data = await LeaveService.get_school_departments()

        return {
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/course/available")
async def get_course_info(
    start_date: Optional[date] = date.today(),
    end_date: Optional[date] = date.today(),
    token: dict = Depends(verify_jwt_token)
):
    try:
        student_id = ConnectionParser.parse_student_id(token)

        if end_date < start_date:
            raise ValueError("End date must be before start date")

        data = await LeaveService.get_course_info(
            student_id,
            start_date,
            end_date
        )

        return {
            "data": data
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        response_data = await LeaveService.create_leave(
            sis_conn,
            course_info,
            leave_type,
            reason,
            from_dept,
            file
        )
        return {"data": response_data}
    except UnsupportedFileTypeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except OutOfFileSizeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidFormatException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history")
async def get_leave_history(token: dict = Depends(verify_jwt_token)):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await LeaveService.get_leave_history(sis_conn)

        return {
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{leave_id}")
async def get_leave_details(
        leave_id: str,
        get_message : bool = Query(False),
        token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await LeaveService.get_leave_details(sis_conn, leave_id, get_message)
        return {"data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{leave_id}")
async def cancel_leave(
    leave_id: str,
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await LeaveService.cancel_leave(sis_conn, leave_id)
        return {"data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch("/{leave_id}")
async def upload_document(
    leave_id: str,
    file: UploadFile = File(...),
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        response_data = await LeaveService.upload_document(
            sis_conn,
            leave_id,
            file,
        )

        return {"data": response_data}
    except UnsupportedFileTypeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except OutOfFileSizeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidFormatException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )