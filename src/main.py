from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import init_indexes   
from src.routes import auth, student, leave, pdf


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    應用程式生命週期管理
    
    Args:
        app: FastAPI 應用程式實例
    """
    # 啟動時執行
    await init_indexes()
    
    yield
    
    # 關閉時執行
    # 目前沒有需要清理的資源


app = FastAPI(
    title="DYU SIS API",
    description="大葉大學學生資訊系統 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

version = "v1"

# 路由註冊
app.include_router(auth.router, prefix=f"/api/{version}/auth", tags=["認證"])
app.include_router(student.router, prefix=f"/api/{version}/student", tags=["學生資訊"])
app.include_router(leave.router, prefix=f"/api/{version}/leave", tags=["課程請假"])
app.include_router(pdf.router, prefix=f"/api/{version}/pdf", tags=["PDF檔案資訊"])

@app.get("/")
async def root():
    return {"message": "DYU SIS API is running"} 