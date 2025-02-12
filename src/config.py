from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# 取得專案根目錄
BASE_DIR = Path(__file__).resolve().parent.parent

# 載入 .env 檔案
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    # MongoDB 設定
    MONGODB_URL: str
    DB_NAME: str
    
    # JWT 設定
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # 快取設定
    CACHE_DURATION: int
    
    class Config:
        env_file = str(BASE_DIR / ".env")

settings = Settings()