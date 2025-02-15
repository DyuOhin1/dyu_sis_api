from typing import Optional

from sis.connection import Connection
from sis.student_information_system import StudentInformationSystem as SIS
from icloud.icloud import iCloud

from src.models.api_response import APIResponse
from src.utils.semester_manager import SemesterManager


class PDFService:
    @staticmethod
    async def graduation(
            sis_conn: Connection
    ):
        return SIS.personal_info.graduation.pdf(
            sis_conn
        )

    @staticmethod
    async def course(
        sis_conn: Connection,
        icloud_conn: Connection,
        year: Optional[str] = None,
        seme : Optional[str] = None
    ):
        if not year and not seme:
            semester = await SemesterManager.get_current_semester(icloud_conn)
            return SIS.personal_info.personal_course_list_pdf(
                sis_conn.student_id,
                semester.year,
                semester.seme
            )

        return SIS.personal_info.personal_course_list_pdf(
                sis_conn.student_id,
                year,
                seme
            )

    @staticmethod
    async def enrollment(
            icloud_conn: Connection,
            year: Optional[str] = None,
            seme: Optional[str] = None
    ):
        if not year and not seme:
            semester = await SemesterManager.get_current_semester(icloud_conn)
            return iCloud.personal_information.proof_of_enrollment_pdf(
                icloud_conn,
                semester.year,
                semester.seme
            )

        return iCloud.personal_information.proof_of_enrollment_pdf(
            icloud_conn,
            year,
            seme
        )

    @staticmethod
    async def timetable(
            icloud_conn: Connection,
            year: Optional[str] = None,
            seme: Optional[str] = None
    ):
        if not year and not seme:
            semester = await SemesterManager.get_current_semester(icloud_conn)
            return iCloud.course_information.timetable_pdf(
                icloud_conn,
                semester.year,
                semester.seme
            )

        return iCloud.course_information.timetable_pdf(
                icloud_conn,
                year,
                seme
            )