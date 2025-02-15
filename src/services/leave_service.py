from datetime import datetime
from pathlib import Path
from typing import List

from src.models.leave import LeaveRequest

from sis.student_information_system import StudentInformationSystem as SIS

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMP_FILE_DIR = BASE_DIR / "temp"
TEMP_FILE_DIR.mkdir(parents=True, exist_ok=True)

class LeaveService:
    @staticmethod
    async def create_leave(student_id: str, leave_request: LeaveRequest):
        # TODO: 實作請假申請邏輯
        

        
        pass

    @staticmethod
    async def get_leave_history(student_id: str):
        # TODO: 實作獲取請假紀錄邏輯
        return []

    @staticmethod
    async def cancel_leave(student_id: str, leave_id: str) -> bool:
        # TODO: 實作銷假邏輯
        return True

    @staticmethod
    async def upload_document(student_id: str, file_content: bytes, file_name: str) -> str:
        # TODO: 實作上傳請假證明文件邏輯
        return f"DOC_{datetime.utcnow().timestamp()}" 