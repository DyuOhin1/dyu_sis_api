import secrets

from fastapi import APIRouter, Query
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from src.config import TERMS_COOKIE_NAME

router = APIRouter()

templates = Jinja2Templates(directory="templates")

# 接受條款的端點
@router.post(
    "/terms/consent",
    summary="同意使用者條款",
    description="同意使用者條款"
)
async def accept_terms(
        next: str = Query("/docs", description="重新導向路徑名稱"),
):
    response = RedirectResponse(url=next, status_code=303)

    token = secrets.token_hex(8)

    # 設置 cookie
    response.set_cookie(
        key=TERMS_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,  # 僅在 HTTPS 上發送
        samesite="lax"
    )

    return response

@router.get(
    "/terms",
    summary="取得使用者條款頁面",
    description="取得使用者條款頁面"
)
async def terms_page(
        request: Request,
):
    return templates.TemplateResponse(
        "terms.html",
        {"request": request}
    )


# 清除接受條款的 cookie（如需要）
@router.delete(
    "/terms/consent",
    summary="拒絕使用者條款",
    description="拒絕使用者條款"
)
async def reset_terms():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key=TERMS_COOKIE_NAME)
    return response