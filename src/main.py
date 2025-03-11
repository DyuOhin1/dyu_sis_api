from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.database import init_indexes
from src.routes import auth, student, leave, pdf

class CharsetMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # 只在 `application/json` 時加上 `charset=utf-8`
        if response.headers.get("content-type") == "application/json":
            response.headers["Content-Type"] = "application/json; charset=utf-8"

        return response
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
    title="Ohin1 OpenAPI",
    description="Ohin1 OpenAPI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CharsetMiddleware)

version = "v1"

# 路由註冊
app.include_router(auth.router, prefix=f"/api/{version}/auth", tags=["Authentication"])
app.include_router(student.router, prefix=f"/api/{version}/student", tags=["Personal Information"])
app.include_router(leave.router, prefix=f"/api/{version}/leave", tags=["Leave Management"])
app.include_router(pdf.router, prefix=f"/api/{version}/pdf", tags=["PDF file generation"])

@app.get("/")
async def root():
    return {"message": "Ohin1 OpenAPI is running..."}