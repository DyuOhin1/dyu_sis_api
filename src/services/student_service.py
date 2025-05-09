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

        return data

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
        data = [d.__dict__ for d in data]

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
            return data
        else:
            for i in data:
                year = i['year']
                sem = i['sem']
                del i['sem']
                del i['year']
                i['t'] = {
                    "smye": year,
                    "smty": sem
                }

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
            return data
        else:
            for i in data:
                year = i['year']
                sem = i['sem']
                del i['sem']
                del i['year']
                i['t'] = {
                    "smye": year,
                    "smty": sem
                }

        await cache_manager.set_cache(
            Collection.MILITARY,
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
            return data
        else:
            for i in data:
                year = i['year']
                sem = i['sem']
                del i['sem']
                del i['year']
                i['t'] = {
                    "smye": year,
                    "smty": sem
                }

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
        data = iCloud.advisor_info(icloud_conn, advisor_id)
        if not data or len(data) == 0:
            raise NotFoundException("No advisor data found")

        data = data[0]

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

        if data:
            for i in data:
                year = i['year']
                sem = i['sem']
                del i['sem']
                del i['year']
                i['t'] = {
                    "smye": year,
                    "smty": sem
                }


        await cache_manager.set_cache(
            Collection.REWARDS_AND_PENALTIES,
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

        data = data['detail']
        if data:
            for i in data:
                year = i['smye']
                sem = i['smty']
                del i['smye']
                del i['smty']
                i['t'] = {
                    "smye": year,
                    "smty": int(sem)
                }

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

        if data:
            for i in data:
                year = i['year']
                sem = i['sem']
                del i['sem']
                del i['year']
                i['t'] = {
                    "smye": year,
                    "smty": sem
                }
                del i['ship_pay']

        await cache_manager.set_cache(
            Collection.SCHOLARSHIP,
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

        if data:
            for i in data:
                year = i['year']
                sem = i['sem']
                del i['sem']
                del i['year']
                i['t'] = {
                    "smye": year,
                    "smty": sem
                }
                del i['elec_mon']
                del i['dorm_elec_money']

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
        )

        if (year and semester) and len(cache_data):
            for data in cache_data:
                if str(data['t']['smye']) == year and str(data['t']['smty']) == semester:
                    return data

            raise NotFoundException(f"grade of year: {year} and semester: {semester} can not be found")

        if cache_data and not refresh:
            return cache_data

        data = iCloud.course_information.annual_grade(icloud_conn)

        def transform_entry(entry):
            """Helper function to transform year/sem into 't' and remove them"""
            entry["t"] = {"smye": int(entry.pop("year")), "smty": int(entry.pop("sem"))}

        if not year and not semester:
            data = data['score']
            for entry in data:  # Use .get() to avoid KeyError
                transform_entry(entry)
        else:
            transform_entry(data)

        await cache_manager.set_cache(
            Collection.ANNUAL_GRADE,
            icloud_conn.student_id,
            data,
        )

        return data

    @staticmethod
    async def get_course_attendance_info(
            icloud_conn : Connection,
            refresh : bool,
            year : str,
            semester : str
    ):
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

        return data