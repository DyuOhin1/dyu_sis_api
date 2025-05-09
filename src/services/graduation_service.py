from typing import Optional

from sis.connection import Connection

from src.database import cache_manager
from src.models.api_response import APIResponse
from src.models.collection import Collection
from src.routes.student import GraduationType

from sis.student_information_system import StudentInformationSystem as SIS

from src.utils.exception import InvalidFormatException


class GraduationService:
    @staticmethod
    def __get_collection_by_type(graduation_type: GraduationType) -> Collection:
        """ 使用字典映射來選擇 Collection """
        collection_mapping = {
            GraduationType.CHINESE: Collection.GRADUATION_CHINESE,
            GraduationType.ENGLISH: Collection.GRADUATION_ENGLISH,
            GraduationType.COMPUTER: Collection.GRADUATION_COMPUTER,
            GraduationType.WORKPLACE_EXP: Collection.GRADUATION_WORKPLACE,
            GraduationType.OVERVIEW: Collection.GRADUATION
        }
        return collection_mapping.get(graduation_type, None) or ValueError("Invalid graduation type")

    @staticmethod
    async def get_graduation(
            sis_conn: Connection,
            graduation_type: GraduationType,
            refresh: bool = False
    ):

        collection = GraduationService.__get_collection_by_type(graduation_type)

        # 嘗試從快取獲取資料
        cache_data = await cache_manager.get_cache(collection, sis_conn.student_id, refresh=refresh)

        if cache_data and not refresh:
            return cache_data

        # 使用字典映射來選擇對應的函數
        graduation_fetch_functions = {
            Collection.GRADUATION_CHINESE: SIS.personal_info.graduation.chinese,
            Collection.GRADUATION_ENGLISH: SIS.personal_info.graduation.english,
            Collection.GRADUATION_COMPUTER: SIS.personal_info.graduation.computer,
            Collection.GRADUATION_WORKPLACE: SIS.personal_info.graduation.workplace_exp,
            Collection.GRADUATION: SIS.personal_info.graduation.info
        }

        fetch_function = graduation_fetch_functions.get(collection, None)
        if not fetch_function:
            raise InvalidFormatException("Invalid graduation type")


        data = fetch_function(sis_conn)
        if data and ( graduation_type == GraduationType.COMPUTER
                      or graduation_type == GraduationType.CHINESE
        or graduation_type == GraduationType.ENGLISH):
            for i in data['data']:
                year = i['year']
                sem = i['semester']
                del i['year']
                del i['semester']
                i['t'] = {
                    "smye": int(year),
                    "smty": int(sem)
                }


        # 更新快取
        await cache_manager.set_cache(collection, sis_conn.student_id, data)

        return data