import contextlib
import json
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Any, Coroutine

import aiofiles
from fastapi import UploadFile
from pydantic import ValidationError
from sis.connection import Connection
from sis.course.leave.constant.departments import Department
from sis.course.leave.constant.leave_type import LeaveType
from sis.course.leave.modals.leave_form_data.course_leave_form_data import CourseLeaveFormData
from sis.modals.course import CourseWithDate

from src.models.leave import LeaveRequest

from sis.student_information_system import StudentInformationSystem as SIS

from src.utils.connect_parser import ConnectionParser
from src.utils.exception import UnsupportedFileTypeException, OutOfFileSizeException, InvalidFormatException

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMP_FILE_DIR = BASE_DIR / "temp"
TEMP_FILE_DIR.mkdir(parents=True, exist_ok=True)

class LeaveService:
    @staticmethod
    async def get_course_info(
        student_id : str,
        start_date: date,
        end_date: date,
    ) -> List[CourseWithDate]:
        return SIS.course_leave.info(start_date, end_date, student_id)

    @staticmethod
    async def get_leave_types():
        return (
            {
                "id": leave_type.value,
                "locale" : {
                    "en": leave_type.name,
                    "zh_tw": leave_type.description
                }
            }
            for leave_type in LeaveType
        )

    @staticmethod
    async def get_school_departments():
        return (
            {
                "id": department.value,
                "locale" : {
                    "en": department.name,
                    "zh_tw": department.description
                }
            }
            for department in Department
        )

    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    ALLOWED_FILE_TYPES = {"image/jpeg", "image/png", "application/pdf", "application/msword", "application/octet-stream"}
    TEMP_DIR = Path(__file__).resolve().parent.parent.parent / "temp"
    TEMP_DIR.mkdir(parents=True, exist_ok=True)  # 確保 TEMP 目錄存在

    @staticmethod
    async def checking_and_get_contents(file : UploadFile) -> bytes | None:
        if file.content_type not in LeaveService.ALLOWED_FILE_TYPES:
            raise UnsupportedFileTypeException(
                f"Invalid file type: {file.content_type}. Allowed types: {', '.join(LeaveService.ALLOWED_FILE_TYPES)}"
            )

        contents = await file.read()
        if len(contents) > LeaveService.MAX_FILE_SIZE:
            raise OutOfFileSizeException("File size must be less than 2MB.")

        return contents

    @staticmethod
    async def save_contents_and_get_path(filename : str, contents : bytes) -> Path:
        temp_file_path = LeaveService.TEMP_DIR / f"{uuid.uuid4()}{Path(filename).suffix}"

        # 使用 `aiofiles` 非同步存檔
        async with aiofiles.open(temp_file_path, "wb") as f:
            await f.write(contents)

        return temp_file_path

    @staticmethod
    async def create_leave(
            sis_conn: Connection,
            course_info: str,
            leave_type: LeaveType,
            reason: str,
            from_dept: Optional[Department],
            file: Optional[UploadFile],
    ):
        temp_file_path = None

        if file:
            contents = await LeaveService.checking_and_get_contents(file)

            # save file to local
            temp_file_path = await LeaveService.save_contents_and_get_path(
                file.filename,
                contents
            )

        # 解析 `course_info` JSON
        try:
            parsed_courses = json.loads(course_info)

            if not isinstance(parsed_courses, list):
                raise ValueError("Course info must be a list of objects.")

            courses = [
                CourseWithDate(
                    course_id=course["course_id"],
                    course_date=date.fromisoformat(course["course_date"]),
                    course_period=course["course_period"]
                )
                for course in parsed_courses
            ]
        except (json.JSONDecodeError, ValidationError, KeyError, ValueError) as e:
            raise InvalidFormatException(f"Invalid course info format: {str(e)}")

        # 準備請假表單
        with contextlib.ExitStack() as stack:
            file_obj = stack.enter_context(open(temp_file_path, "rb")) if temp_file_path else None

            form = CourseLeaveFormData(
                course=courses,
                leave_type=leave_type,
                reason=reason,
                from_dept=from_dept,
                file=file_obj  # 只有當檔案存在時才打開
            )

            # 呼叫 SIS API
            response_data = SIS.course_leave.send(sis_conn, form)

        # 清理臨時檔案
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()

        return response_data

    @staticmethod
    async def get_leave_history(
            sis_conn: Connection,
    ):
        return SIS.course_leave.list(sis_conn)

    @staticmethod
    async def get_leave_details(
            sis_conn: Connection,
            leave_id: str,
            get_message: bool,
    ):
        return SIS.course_leave.detail(sis_conn, leave_id, get_message)

    @staticmethod
    async def cancel_leave(
            sis_conn : Connection,
            leave_id: str
    ):
        return SIS.course_leave.cancel(sis_conn, leave_id)

    @staticmethod
    async def upload_document(
            sis_conn : Connection,
            leave_id: str,
            file: UploadFile,
    ):
        contents = await LeaveService.checking_and_get_contents(file)

        # save file to local
        temp_file_path = await LeaveService.save_contents_and_get_path(
            file.filename,
            contents
        )

        if not temp_file_path:
            raise FileNotFoundError(f"File not found: {file.filename}")

        with contextlib.ExitStack() as stack:
            file_obj = stack.enter_context(open(temp_file_path, "rb"))

            response_data = SIS.course_leave.submit_document(sis_conn, leave_id, file_obj)

        # 清理臨時檔案
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()

        return response_data