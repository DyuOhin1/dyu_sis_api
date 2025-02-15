import json
import time
from typing import Optional, Any, Dict

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.models.collection import Collection


class CacheManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.default_cache_duration = 259200  # 3天的秒數

    async def get_cache(
        self, 
        collection: Collection,
        student_id: str,
        semester: Optional[Dict[str, str]] = None,
        refresh: bool = False
    ) -> Optional[Dict]:
        """
        獲取快取資料
        
        Args:
            collection: 集合
            student_id: 學生學號
            semester: 學年學期資訊 {"year": "112", "semester": "1"}
            refresh: 是否強制更新快取
        """
        collection = self.db[collection.value]

        # 建構查詢條件
        query = {"student_id": student_id}
        if semester:
            query.update({
                "year": semester["year"],
                "semester": semester["semester"]
            })

        try:
            # 查詢快取
            cache_data = await collection.find_one(query)
        except Exception as e:
            raise RuntimeError(f"Error querying cache: {e}")

        if not cache_data:
            return None

        current_time = int(time.time())

        # 檢查快取是否過期
        if not refresh and cache_data.get("updated_timestamp"):
            cache_duration = cache_data.get("cache_duration", self.default_cache_duration)
            if current_time - cache_data["updated_timestamp"] < cache_duration:
                return cache_data["data"]

        return None

    async def set_cache(
        self,
        collection: Collection,
        student_id: str,
        data: Dict[str, Any],
        semester: Optional[Dict[str, str]] = None,
        cache_duration: int = None
    ) -> None:
        """
        設置快取資料
        
        Args:
            collection: 集合
            student_id: 學生學號
            data: 要快取的資料
            semester: 學年學期資訊 {"year": "112", "semester": "1"}
            cache_duration: 快取持續時間(秒)
        """
        collection = self.db[collection.value]
        current_time = int(time.time())

        data = json.loads(json.dumps(data))

        # 建構快取文件
        cache_document = {
            "student_id": student_id,
            "created_timestamp": current_time,
            "updated_timestamp": current_time,
            "cache_duration": cache_duration or self.default_cache_duration,
            "data": data
        }

        # 根據是否有學期資訊決定 _id
        if semester:
            cache_document.update({
                "year": semester["year"],
                "semester": semester["semester"]
            })
            # 使用學號、年度、學期作為查詢條件
            query = {
                "student_id": student_id,
                "year": semester["year"],
                "semester": semester["semester"]
            }
        else:
            cache_document["_id"] = student_id
            query = {"_id": student_id}

        try:
            # 使用 upsert 更新或插入快取
            await collection.update_one(
                query,
                {"$set": cache_document},
                upsert=True
            )
        except Exception as e:
            raise RuntimeError(f"Error setting cache: {e}")

    async def delete_cache(
        self,
        collection: Collection,
        student_id: str,
        semester: Optional[Dict[str, str]] = None
    ) -> None:
        """
        刪除快取資料
        
        Args:
            collection: 集合
            student_id: 學生學號
            semester: 學年學期資訊 {"year": "112", "semester": "1"}
        """
        collection = self.db[collection.value]
        
        query = {"student_id": student_id}
        if semester:
            query.update({
                "year": semester["year"],
                "semester": semester["semester"]
            })
            
        await collection.delete_one(query)

    async def clear_expired_cache(self, collection: Collection) -> None:
        """
        清理過期的快取資料
        
        Args:
            collection: 集合
        """
        collection = self.db[collection.value]
        current_time = int(time.time())
        
        # 刪除所有過期的快取
        await collection.delete_many({
            "updated_timestamp": {
                "$lt": current_time - self.default_cache_duration
            }
        })