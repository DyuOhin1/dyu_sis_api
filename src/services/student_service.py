import json

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


class StudentService:
    @staticmethod
    async def get_student_info(sis_conn: Connection, refresh: bool = False) -> APIResponse:
        cache_data = await cache_manager.get_cache(
            Collection.STUDENT_PROFILE,
            sis_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return APIResponse.success(cache_data, "Student information fetched successfully")

        # 從 SIS 系統獲取學生資訊
        data = SIS.personal_info.privacy(sis_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch student information from SIS"
            )

        await cache_manager.set_cache(
            Collection.STUDENT_PROFILE,
            sis_conn.student_id,
            data
        )

        return APIResponse.success(data, "Student information fetched successfully")

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
            return APIResponse.success(cache_data, "Student semester information fetched successfully")

        # 從 iCloud 系統獲取學期資訊
        data = iCloudUtils.student_semester(icloud_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch student semester information from iCloud"
            )

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
            try:
                # TODO: 學年學期應該由資料庫直接取得快取。
                semester = iCloudUtils.student_semester(icloud_conn)
            except json.JSONDecodeError:
                return APIResponse.error(
                    status_code=status.HTTP_404_NOT_FOUND,
                    msg="Failed to fetch student semester information"
                )
            first_semester = semester[0]
            year = first_semester["smye"]
            seme = first_semester["smty"]
            cache_data = await cache_manager.get_cache(
                Collection.COURSE_TIMETABLE,
                icloud_conn.student_id,
                semester={
                    "year": year,
                    "semester": semester
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
            return APIResponse.success(cache_data, "Course information fetched successfully")

        # 從 SIS 系統獲取課程資訊
        try:
            data = iCloud.course_information.timetable(
                icloud_conn,
                year,
                seme
            )
        except Exception:
            # TODO: Add proper exception handling
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch course information"
            )

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch course information"
            )

        await cache_manager.set_cache(
            Collection.COURSE_TIMETABLE,
            icloud_conn.student_id,
            data,
            semester={
                "year": year,
                "semester": seme
            }
        )

        return APIResponse.success(data, "Course information fetched successfully")

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
            return APIResponse.success(cache_data, "Course warning information fetched successfully")

        # 從 SIS 系統獲取課程警告資訊
        data = SIS.personal_info.course_warning(sis_conn)
        data = json.dumps([obj.__dict__ for obj in data])

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch course warning information from SIS"
            )

        await cache_manager.set_cache(
            Collection.COURSE_WARNING,
            sis_conn.student_id,
            data
        )

        return APIResponse.success(data, "Course warning information fetched successfully")

    @staticmethod
    async def get_barcode(
            sis_conn: Connection,
    ):
        # 從 SIS 系統獲取條碼資訊
        data = SIS.personal_info.personal_barcode(sis_conn.student_id)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch barcode information from SIS"
            )

        return APIResponse.success(data, "Barcode information fetched successfully")

    @staticmethod
    async def get_personal_image(
            sis_conn: Connection,
    ):
        # 從 SIS 系統獲取條碼資訊
        data = SIS.personal_info.personal_image(sis_conn.student_id)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch barcode information from SIS"
            )

        return APIResponse.success(data, "Barcode information fetched successfully")

    @staticmethod
    async def get_injury(
            sis_conn: Connection,
            refresh: bool = False
    ):
        cache_data = await cache_manager.get_cache(
            Collection.INJURY,
            sis_conn.student_id,
            refresh=refresh
        )

        if cache_data and not refresh:
            return APIResponse.success(cache_data, "Injury information fetched successfully")

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.injury_record(sis_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch injury information from iCloud"
            )

        await cache_manager.set_cache(
            Collection.INJURY,
            sis_conn.student_id,
            data
        )

        return APIResponse.success(data, "Injury information fetched successfully")

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
            return APIResponse.success(cache_data, "Military information fetched successfully")

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.military_record(icloud_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch military information from iCloud"
            )

        await cache_manager.set_cache(
            Collection.INJURY,
            icloud_conn.student_id,
            data
        )

        return APIResponse.success(data, "Military information fetched successfully")

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
            return APIResponse.success(cache_data, "Advisors information fetched successfully")

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.advisors(icloud_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch advisors information from iCloud"
            )

        await cache_manager.set_cache(
            Collection.ADVISORS,
            icloud_conn.student_id,
            data
        )

        return APIResponse.success(data, "Advisors information fetched successfully")

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
            return APIResponse.success(cache_data, "Rewards and penalties information fetched successfully")

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.rewards_and_penalties_record(icloud_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch rewards and penalties information from iCloud"
            )

        await cache_manager.set_cache(
            Collection.INJURY,
            icloud_conn.student_id,
            data
        )

        return APIResponse.success(data, "Rewards and penalties information fetched successfully")

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
            return APIResponse.success(cache_data, "Enrollment information fetched successfully")

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.proof_of_enrollment(icloud_conn, lang=lang)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch enrollment information from iCloud"
            )

        await cache_manager.set_cache(
            Collection.PROOF_OF_ENROLLMENT,
            icloud_conn.student_id,
            data
        )

        return APIResponse.success(data, "Enrollment information fetched successfully")

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
            return APIResponse.success(cache_data, "Scholarship information fetched successfully")

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.scholarship_record(icloud_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch scholarship information from iCloud"
            )

        await cache_manager.set_cache(
            Collection.PROOF_OF_ENROLLMENT,
            icloud_conn.student_id,
            data
        )

        return APIResponse.success(data, "Scholarship information fetched successfully")

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
            return APIResponse.success(cache_data, "Printer point information fetched successfully")

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.printer_point(icloud_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch printer point information from iCloud"
            )

        await cache_manager.set_cache(
            Collection.PRINTER_POINTS,
            icloud_conn.student_id,
            {"point" : data}
        )

        return APIResponse.success({"point" : data}, "Printer point information fetched successfully")

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
            return APIResponse.success(cache_data, "Dorm information fetched successfully")

        # 從 SIS 系統獲取課程警告資訊
        data = iCloud.personal_information.dorm_record(icloud_conn)

        if not data:
            return APIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Failed to fetch dorm information from iCloud"
            )

        await cache_manager.set_cache(
            Collection.DORM,
            icloud_conn.student_id,
            data
        )

        return APIResponse.success(data, "Dorm information fetched successfully")