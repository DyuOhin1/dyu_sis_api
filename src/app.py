from contextlib import asynccontextmanager

import fastapi.openapi.utils as fu
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.staticfiles import StaticFiles

from src.config import TERMS_COOKIE_NAME
from src.database import init_indexes
from src.routes import auth, student, leave, pdf, terms


class CharsetAndAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, terms_cookie_name: str = "terms_accepted"):
        super().__init__(app)
        self.terms_cookie_name = terms_cookie_name

    async def dispatch(self, request: Request, call_next):
        # 首先檢查是否訪問文檔頁面且未接受條款
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            # 檢查是否已接受條款
            terms_cookie = request.cookies.get(self.terms_cookie_name)
            if not terms_cookie:
                # 如果沒有接受條款，重定向到條款頁面
                return RedirectResponse(url=f"/terms")

        # 正常處理請求
        response: Response = await call_next(request)

        # 處理字符集
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

version = "v1"
des = """
**此 API 會儲存您的個人資料**，此用之前應先詳閱[使用者條款](https://dyuohin1.github.io/terms/)，若使用此服務即表示同意。
"""

app = FastAPI(
    title="Ohin1 OpenAPI",
    description=des,
    version=version,
    lifespan=lifespan,
    terms_of_service="https://dyuohin1.github.io/terms/",
)

fu.validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
    "properties": {
        "detail": {"title": "Message", "type": "string"},
    },
}

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CharsetAndAuthMiddleware, terms_cookie_name=TERMS_COOKIE_NAME)

# 路由註冊
app.include_router(auth.router, prefix=f"/api/{version}/auth", tags=["Authentication"])
app.include_router(student.router, prefix=f"/api/{version}/student", tags=["Personal Information"])
app.include_router(leave.router, prefix=f"/api/{version}/leave", tags=["Leave Management"])
app.include_router(pdf.router, prefix=f"/api/{version}/pdf", tags=["PDF file generation"])
app.include_router(terms.router, tags=["Terms"])

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get(
    "/",
    summary="Hello World",
    description="say \"Hello World\" and redirect to documentation",
)
async def root():
    return RedirectResponse(url="docs")

