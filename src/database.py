from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

from src.config import settings
from src.models.collection import Collection

try:
    # 建立 MongoDB 連線
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # 選擇資料庫
    db = client[settings.DB_NAME]
    
    # 建立集合（collections）
    cache_collections = {
        Collection.STUDENT: db[str(Collection.STUDENT)],
        Collection.COURSE: db[str(Collection.COURSE)],
        Collection.GRADUATION: db[str(Collection.GRADUATION)],
    }
    
    # 建立索引
    async def init_indexes():
        # 學生資訊集合索引
        await cache_collections[Collection.STUDENT].create_index(
            [("student_id", 1)],
            unique=True
        )
        
        # 課程資訊集合索引
        await cache_collections[Collection.COURSE].create_index(
            [("student_id", 1)],
            unique=True
        )
        
        # 畢業審查集合索引
        await cache_collections[Collection.GRADUATION].create_index(
            [("student_id", 1)],
            unique=True
        )
        
        # 所有集合加上過期時間索引
        for collection in cache_collections.values():
            await collection.create_index(
                [("updated_timestamp", 1)],
                expireAfterSeconds=settings.CACHE_DURATION
            )

except ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    raise 