import json

from icloud.personal.utils.icloud_utils import iCloudUtils
from sis.connection import Connection

from src.database import cache_manager
from src.models.collection import Collection
from src.utils.exception import NotFoundException


class Semester:
    def __init__(self, year: str, seme: str):
        self.year = year
        self.seme = seme


class SemesterManager:
    cache_manager = cache_manager

    @staticmethod
    async def get_current_semester(icloud_conn : Connection) -> Semester:
        """
        獲取當前學期
        """

        try:
            semester_cache_data = await cache_manager.get_cache(
                Collection.STUDENT_SEMESTER,
                icloud_conn.student_id,
            )

            if not semester_cache_data:
                semester = iCloudUtils.student_semester(icloud_conn)
                await cache_manager.set_cache(
                    Collection.STUDENT_SEMESTER,
                    icloud_conn.student_id,
                    semester
                )
            else:
                semester = semester_cache_data
        except json.JSONDecodeError:
            raise NotFoundException("Failed to fetch student semester information")

        first_semester = semester[0]
        year = first_semester["smye"]
        seme = first_semester["smty"]

        return Semester(str(year), str(seme))
