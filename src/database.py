from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

from src.config import settings
from src.models.collection import Collection
from src.utils.cache import CacheManager

try:
    # 建立 MongoDB 連線
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # 選擇資料庫
    db = client[settings.DB_NAME]

    cache_collections = {collection: db[collection.value] for collection in Collection}

    cache_manager = CacheManager(db)

    # 建立索引
    async def init_indexes():
        for collection_name, collection in cache_collections.items():
            await collection.insert_one({"init": True})
            await collection.delete_one({"init": True})

except ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    raise 