import json

from fastapi import HTTPException
from icloud.icloud import iCloud
from icloud.personal.constants.lang import Lang
from icloud.personal.utils.icloud_utils import iCloudUtils
from sis.connection import Connection
from sis.student_information_system import StudentInformationSystem as SIS
from starlette import status
from typing import Optional

from src.models.api_response import APIResponse
from src.models.collection import Collection
from src.database import cache_manager
from src.utils.exception import StudentInfoNotFoundException, NotFoundException
from src.utils.semester_manager import SemesterManager


class StudentService:
    @staticmethod
    async def get_student_info(sis_conn: Connection, refresh: bool = False) -> APIResponse:
        cache_data = await cache_manager.get_cache(
            Collection.STUDENT_PROFILE,
            sis_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取學生資訊
        data = SIS.personal_info.privacy(sis_conn)

        if not data:
            raise StudentInfoNotFoundException("Failed to fetch student information")

        await cache_manager.set_cache(
            Collection.STUDENT_PROFILE,
            sis_conn.student_id,
            data
        )

        return data


    @staticmethod
    async def get_student_semester(
            icloud_conn: Connection,
            refresh: bool = False,
    ) -> APIResponse:
        cache_data = await cache_manager.get_cache(
            Collection.STUDENT_SEMESTER,
            icloud_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 iCloud 系統獲取學期資訊
        data = iCloudUtils.student_semester(icloud_conn)

        if not data:
            raise NotFoundException("Failed to fetch student semester information")

        await cache_manager.set_cache(
            Collection.STUDENT_SEMESTER,
            icloud_conn.student_id,
            data
        )

        return APIResponse.success(data, "Student semester information fetched successfully")

    @staticmethod
    async def get_course_timetable(
            icloud_conn: Connection,
            refresh: bool = False,
            year: Optional[str] = None,
            seme: Optional[str] = None
    ) -> APIResponse:
        """
        取得課程資訊
        :param icloud_conn:
        :param refresh:
        :param seme: 學年
        :param year:  學期
        :return:
        """

        # 如果沒有提供學年學期，則取得當前學期
        if not seme or not year:
            semester = await SemesterManager.get_current_semester(icloud_conn)
            year = semester.year
            seme = semester.seme
            cache_data = await cache_manager.get_cache(
                Collection.COURSE_TIMETABLE,
                icloud_conn.student_id,
                semester={
                    "year": semester.year,
                    "semester": semester.seme
                }
            )
        else:
            cache_data = await cache_manager.get_cache(
                Collection.COURSE_TIMETABLE,
                icloud_conn.student_id,
                semester={
                    "year": year,
                    "semester": seme
                }
            )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取課程資訊

        data = iCloud.course_information.timetable(
            icloud_conn,
            year,
            seme
        )

        if not data:
            raise NotFoundException("Failed to fetch course information")

        await cache_manager.set_cache(
            Collection.COURSE_TIMETABLE,
            icloud_conn.student_id,
            data,
            semester={
                "year": year,
                "semester": seme
            }
        )

        return data

    @staticmethod
    async def get_course_warning(
            sis_conn: Connection,
            refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.COURSE_WARNING,
            sis_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取課程警告資訊
        data = SIS.personal_info.course_warning(sis_conn)
        data = json.dumps([obj.__dict__ for obj in data])

        if not data:
            raise NotFoundException("Failed to fetch course warning information")

        await cache_manager.set_cache(
            Collection.COURSE_WARNING,
            sis_conn.student_id,
            data
        )

        return data

    @staticmethod
    async def get_barcode(
            sis_conn: Connection,
    ):
        # 從 SIS 系統獲取條碼資訊
        data = SIS.personal_info.personal_barcode(sis_conn.student_id)

        if not data:
            raise NotFoundException("Failed to fetch barcode information")

        return data

    @staticmethod
    async def get_personal_image(
            sis_conn: Connection,
    ):
        # 從 SIS 系統獲取條碼資訊
        data = SIS.personal_info.personal_image(sis_conn.student_id)

        if not data:
            raise NotFoundException("Failed to fetch personal image")

        return data

    @staticmethod
    async def get_injury(
            icloud_conn: Connection,
            refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.INJURY,
            icloud_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.injury_record(icloud_conn)

        if not data:
            raise NotFoundException("Failed to fetch injury information")

        await cache_manager.set_cache(
            Collection.INJURY,
            icloud_conn.student_id,
            data
        )

        return data

    @staticmethod
    async def get_military(
            icloud_conn: Connection,
            refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.MILITARY,
            icloud_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.military_record(icloud_conn)

        if not data:
            raise NotFoundException("Failed to fetch military information")

        await cache_manager.set_cache(
            Collection.INJURY,
            icloud_conn.student_id,
            data
        )

        return data

    @staticmethod
    async def get_advisors(
            icloud_conn: Connection,
            refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.ADVISORS,
            icloud_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.advisors(icloud_conn)

        if not data:
            raise NotFoundException("Failed to fetch advisors information")

        await cache_manager.set_cache(
            Collection.ADVISORS,
            icloud_conn.student_id,
            data
        )

        return data

    @staticmethod
    async def get_advisor_info(
            icloud_conn: Connection,
            advisor_id: str,
    ):
        # 從 SIS 系統獲取課程警告資訊
        try:
            data = iCloud.advisor_info(icloud_conn, advisor_id)
            if not data or len(data) == 0:
                raise ValueError("No advisor data found")

            data = data[0]
        except Exception:
            raise NotFoundException("Failed to fetch advisor information")

        if not data:
            raise NotFoundException("Failed to fetch advisor information")

        return data


    @staticmethod
    async def get_rewards_and_penalties(
            icloud_conn: Connection,
            refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.REWARDS_AND_PENALTIES,
            icloud_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.rewards_and_penalties_record(icloud_conn)

        if not data:
            raise NotFoundException("Failed to fetch rewards and penalties information")
        await cache_manager.set_cache(
            Collection.INJURY,
            icloud_conn.student_id,
            data
        )

        return data

    @staticmethod
    async def get_enrollment(
            icloud_conn: Connection,
            lang: Lang = Lang.ZH_TW,
            refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.PROOF_OF_ENROLLMENT,
            icloud_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
           return cache_data

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.proof_of_enrollment(icloud_conn, lang=lang)

        if not data:
            raise NotFoundException("Failed to fetch enrollment information")

        await cache_manager.set_cache(
            Collection.PROOF_OF_ENROLLMENT,
            icloud_conn.student_id,
            data
        )

        return data

    @staticmethod
    async def get_scholarship(
            icloud_conn: Connection,
            refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.SCHOLARSHIP,
            icloud_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.scholarship_record(icloud_conn)

        if not data:
            raise NotFoundException("Failed to fetch scholarship information")

        await cache_manager.set_cache(
            Collection.PROOF_OF_ENROLLMENT,
            icloud_conn.student_id,
            data
        )

        return data

    @staticmethod
    # printer point
    async def get_printer_point(
        icloud_conn: Connection,
        refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.PRINTER_POINTS,
            icloud_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.printer_point(icloud_conn)

        if not data:
            raise NotFoundException("Failed to fetch printer point information")

        await cache_manager.set_cache(
            Collection.PRINTER_POINTS,
            icloud_conn.student_id,
            {"point" : data}
        )

        return {"point" : data}

    @staticmethod
    async def get_dorm(
        icloud_conn: Connection,
        refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.DORM,
            icloud_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return cache_data

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.dorm_record(icloud_conn)

        if not data:
            raise NotFoundException("Failed to fetch dorm information")

        await cache_manager.set_cache(
            Collection.DORM,
            icloud_conn.student_id,
            data
        )

        return data

    @staticmethod
    async def get_annual_grade(
        icloud_conn: Connection,
        year: Optional[str] = None,
        semester: Optional[str] = None,
        refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.ANNUAL_GRADE,
            icloud_conn.student_id,
            refresh=refresh,
            semester={
                "year": year,
                "semester": semester
            }
        )

        if cache_data and not refresh:
            return cache_data

        try:
            if not year or not semester:
                data = iCloud.course_information.annual_grade(icloud_conn)
            else:
                data = iCloud.course_information.grade(icloud_conn, year, semester)
        except Exception:
            raise NotFoundException("Failed to fetch annual grade information from iCloud")

        if not data:
            raise NotFoundException("Failed to fetch annual grade information")

        await cache_manager.set_cache(
            Collection.ANNUAL_GRADE,
            icloud_conn.student_id,
            data,
            semester={
                "year": year,
                "semester": semester
            }
        )

        return data

    @staticmethod
    async def get_course_attendance_info(
            icloud_conn : Connection,
            refresh : bool,
            year : str,
            semester : str
    ):
        cache_data = await cache_manager.get_cache(
            Collection.COURSE_ATTENDANCE,
            icloud_conn.student_id,
            refresh=refresh,
            semester={
                "year": year,
                "semester": semester
            }
        )

        if cache_data and not refresh:
            return cache_data

        data = iCloud.course_information.attendance(icloud_conn)

        if not data or len(data) == 0:
            raise NotFoundException("Failed to fetch course attendance information")

        if not year or not semester:
            data = data[0]
        else:
            found = False
            for d in data:
                if str(d["year"]) == year and str(d["sem"]) == semester:
                    data = d
                    found = True
                    break

            if not found:
                raise NotFoundException("Failed to fetch course attendance information")

        await cache_manager.set_cache(
            Collection.COURSE_ATTENDANCE,
            icloud_conn.student_id,
            data,
            semester={
                "year": year,
                "semester": semester
            }
        )

        return data