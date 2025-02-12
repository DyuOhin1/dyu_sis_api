from typing import List

from icloud.personal.utils.icloud_utils import iCloudUtils
from sis.connection import Connection
from sis.student_information_system import StudentInformationSystem as SIS
from icloud.icloud import iCloud
from starlette import status

from src.config import settings
from src.models.api_response import APIResponse
from src.models.collection import Collection
from src.models.student import CourseInfo
from src.utils.cache import get_cache, set_cache
from src.utils.decorators import cache_data


class StudentService:
    @staticmethod
    @cache_data(Collection.STUDENT)
    async def get_student_info(sis_conn: Connection, refresh: bool = False) -> APIResponse:
        # 從 SIS 系統獲取學生資訊
        data = SIS.personal_info.privacy(sis_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch student information from SIS"
            )

        return APIResponse.success(data, "Student information fetched successfully")

    @staticmethod
    @cache_data(Collection.COURSE)
    async def get_course_timetable(
            icloud_conn: Connection,
            refresh: bool = False
    ) -> APIResponse:
        semester = iCloudUtils.student_semester(icloud_conn)
        first_semester = semester[0]

        # 從 SIS 系統獲取課程資訊
        data = iCloud.course_information.timetable(
            icloud_conn,
            first_semester["smye"],
            first_semester["smty"]
        )

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch course information"
            )

        return APIResponse.success(data, "Course information fetched successfully")