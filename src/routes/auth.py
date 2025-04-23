from fastapi import APIRouter, Response, Depends, HTTPException, Form
from sis.exception import EmptyInputException, InvalidStudentIDException, InvalidPasswordException, \
    HTTPRequestException, ConnectionException, RedirectException, UnexpectedResponseException, AuthenticationException
from starlette import status

from src.models.auth import LoginRequest, LoginSuccessResponse
from src.models.response_data import ResponseData
from src.services.auth_service import AuthService
from src.utils.auth import verify_jwt_token

router = APIRouter()

@router.post(
    "/login",
    responses={
        200: {
            "description": "請將 access_token 在請求本服務其他資源路徑時，置於 Header 處使用 Authorization: Bearer <access_token> 進行驗證。",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "access_token": {
                                "type": "string",
                                "description": "JWT Token"
                            },
                            "token_type": {
                                "type": "string",
                                "description": "JWT Token 類型"
                            },
                            "expires_in": {
                                "type": "integer",
                                "description": "JWT Token 過期時間"
                            }
                        },
                        "required": ["access_token", "token_type", "expires_in"]
                    },
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "Bearer",
                        "expires_in": 3600
                    }
                }
            }
        },
    },
    summary="登入系統，並獲得 JWT Token",
    description="""
    登入[學生資訊系統](https://sis.dyu.edu.tw/)以及[iCloud](https://icloud.dyu.edu.tw/)，請使用與校園系統相同的帳號密碼。
    """
)
async def login(
        login_data: LoginRequest = Form(...),
):
    try:
        result = await AuthService.login(login_data)
        return result
    except UnexpectedResponseException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unexpected response from remote server."
        )
    except AuthenticationException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong username or password."
        )
    except EmptyInputException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The username and password cannot be empty."
        )
    except InvalidStudentIDException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong username format."
        )
    except InvalidPasswordException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong password format."
        )
    except HTTPRequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HTTP request failed."
        )
    except ConnectionException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Disconnect from remote server."
        )
    except RedirectException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login redirect exception."
        )

@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object",
                                "properties": {
                                    "success": {
                                        "type": "boolean",
                                        "description": "登出是否成功"
                                    }
                                },
                                "required": ["success"]
                            }
                        },
                        "required": ["data"]
                    },
                    "example": {
                        "data": {
                            "success": True
                        }
                    }
                }
            }
        }
    },
    summary="""
    登出校園資訊系統系統，清除 Session 狀態
    """,
    description="""
    將從[學生資訊系統](https://sis.dyu.edu.tw/)以及[iCloud](https://icloud.dyu.edu.tw/)登出，將無法再使用此 token 訪問上述兩個系統，但此 token 在 API 過期前皆有效，可訪問本 API 快取資料。
    """,
)
async def logout(token: dict = Depends(verify_jwt_token)):
    try:
        await AuthService.logout(token)
        return {
            "data": {
                "success": True,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "sis 為 [學生資訊系統](https://sis.dyu.edu.tw/)登入狀態，ic 為 [iCloud](https://icloud.dyu.edu.tw/) 登入狀態。",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object",
                                "properties": {
                                    "sis": {
                                        "type": "boolean",
                                        "description": "學生資訊系統登入狀態"
                                    },
                                    "ic": {
                                        "type": "boolean",
                                        "description": "iCloud 登入狀態"
                                    }
                                },
                                "required": ["sis", "ic"],
                            }
                        },
                        "required": ["data"]
                    },
                    "example": {
                        "data": {
                            "sis": True,
                            "ic": False
                        }
                    }
                }
            }
        }
    },
    summary="取得 sis 與 iCloud 登入狀態",
    description="""
    取得[學生資訊系統](https://sis.dyu.edu.tw/)以及[iCloud](https://icloud.dyu.edu.tw/)的登入狀態，若有一項為登出，請使用本系統登入，核發新的 JWT Token。
    若其一系統為登出狀態，則表示無法再使用該系統之互動以及更新快取查詢服務。
    """
)
async def logged_status(token: dict = Depends(verify_jwt_token)):
    try:
        is_logged = await AuthService.test_login_status(token)
        return ResponseData(data=is_logged)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
