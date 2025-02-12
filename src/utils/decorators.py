from functools import wraps
from typing import Any, Callable, Optional

from src.models.api_response import APIResponse
from src.models.collection import Collection
from src.utils.cache import get_cache, set_cache
from src.config import settings


def cache_data(collection: Collection):
    """
    快取裝飾器

    Args:
        collection: MongoDB 集合
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> APIResponse:
            # 取得學生ID和refresh參數
            connection = args[0]  # 第二個參數是 connection
            refresh = args[1] if len(args) > 1 else False

            # 嘗試從快取取得資料
            cache_data = await get_cache(collection, connection.student_id, refresh)
            if cache_data and not refresh:
                return APIResponse.success(
                    data=cache_data,
                    msg=f"{collection.value} information cache fetched successfully."
                )

            # 執行原始函數
            result = await func(*args, **kwargs)

            # 如果執行成功且有資料，更新快取
            if result.status and result.data:
                await set_cache(
                    collection,
                    connection.student_id,
                    result.data,
                    settings.CACHE_DURATION
                )

            return result

        return wrapper
    return decorator