from typing import Union

from fastapi import APIRouter, Response, Depends, HTTPException, Form
from sis.exception import EmptyInputException, InvalidStudentIDException, InvalidPasswordException, \
    HTTPRequestException, ConnectionException, RedirectException, UnexpectedResponseException, AuthenticationException
from starlette import status

from src.models.api_response import APIResponse
from src.models.auth import LoginRequest, LoginSuccessResponse
from src.models.response_data import ResponseData
from src.services.auth_service import AuthService
from src.utils.auth import verify_jwt_token

router = APIRouter()

@router.post(
    "/login",
    response_model=LoginSuccessResponse,
)
async def login(
        login_data: LoginRequest = Form(...)
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
    response_model= ResponseData,
)
async def logout(token: dict = Depends(verify_jwt_token)):
    try:
        await AuthService.logout(token)

        return ResponseData(data=None)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    response_model=ResponseData,
)
async def logged_status(token: dict = Depends(verify_jwt_token)):
    try:
        is_logged = await AuthService.test_login_status(token)
        return ResponseData(data=is_logged)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
