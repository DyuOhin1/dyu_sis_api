import time
from typing import Any, Optional

from src.database import db
from src.models.collection import Collection


async def get_cache(
        collection: Collection,
        student_id: str,
        refresh: bool = False
) -> Optional[dict]:
    collection = db[collection.value]
    cache = await collection.find_one({"_id": student_id})
    
    if not cache or refresh:
        return None
        
    if (time.time() - cache["updated_timestamp"]) > cache["cache_duration"]:
        return None
        
    return cache["data"]

async def set_cache(collection: Collection, student_id: str, data: Any, duration: int) -> None:
    collection = db[collection.value]
    current_time = int(time.time())
    
    cache_doc = {
        "_id": student_id,
        "created_timestamp": current_time,
        "updated_timestamp": current_time,
        "cache_duration": duration,
        "data": data
    }
    
    await collection.update_one(
        {"_id": student_id},
        {"$set": cache_doc},
        upsert=True
    )

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
                connection = args[1]  # 第二個參數是 connection
                refresh = kwargs.get('refresh', False)

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