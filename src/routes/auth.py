from typing import Union

from fastapi import APIRouter, Response, Depends
from starlette import status

from src.models.api_response import APIResponse
from src.models.auth import LoginRequest, LoginSuccessResponse
from src.services.auth_service import AuthService
from src.utils.auth import verify_jwt_token

router = APIRouter()

@router.post(
    "/login",
    response_model=Union[LoginSuccessResponse, APIResponse],
)
async def login(login_data: LoginRequest, response: Response):
    result = await AuthService.login(login_data)
    
    if isinstance(result, APIResponse):
        response.status_code = result.status_code

    return result

@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, token: dict = Depends(verify_jwt_token)):
    result = await AuthService.logout(token)

    response.status_code = result.status_code
    return result