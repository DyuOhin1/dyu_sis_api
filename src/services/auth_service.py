from typing import Union

from fastapi import Response
from icloud.icloud import iCloud
from sis.connection import Connection as SISConn
from sis.student_information_system import StudentInformationSystem as SIS
from starlette import status

from src.config import settings
from src.models.api_response import APIResponse
from src.models.auth import LoginRequest, JWTPayload, Connection, LoginSuccessResponse
from src.utils.auth import create_jwt_token
from src.utils.time_unit import TimeUnit

from sis.exception import (
    EmptyInputException,
    InvalidStudentIDException,
    InvalidPasswordException,
    ConnectionException,
    RedirectException,
    AuthenticationException,
    HTTPRequestException,
    UnexpectedResponseException
)


class AuthService:
    @staticmethod
    async def login(
            login_data: LoginRequest,
    ) -> Union[LoginSuccessResponse, APIResponse]:
        try:
            # login to Sis
            sis_conn = SIS.login(login_data.username, login_data.password)

            # login to iCloud
            icloud_conn = iCloud.login(login_data.username, login_data.password)

            payload = JWTPayload(
                s_id=login_data.username,
                sis=Connection(
                    session_id=sis_conn.php_session_id,
                    login_timestamp=sis_conn.last_login_timestamp
                ),
                ic=Connection(
                    session_id=icloud_conn.php_session_id,
                    login_timestamp=icloud_conn.last_login_timestamp
                )
            )

            token = create_jwt_token(payload.model_dump())
            return LoginSuccessResponse(
                access_token=token,
                token_type="Bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * TimeUnit.MINUTE
            )

        except EmptyInputException:
            return APIResponse.error(msg="The username and password cannot be empty.", status_code=status.HTTP_400_BAD_REQUEST)
        except InvalidStudentIDException:
            return APIResponse.error(msg="Wrong username format.", status_code=status.HTTP_400_BAD_REQUEST)
        except InvalidPasswordException:
            return APIResponse.error(msg="Wrong password format.", status_code=status.HTTP_400_BAD_REQUEST)
        except HTTPRequestException:
            return APIResponse.error(msg="HTTP request failed.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        except ConnectionException:
            return APIResponse.error(msg="Disconnect from remote server.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        except RedirectException:
            return APIResponse.error(msg="Redirected to another page.", status_code=status.HTTP_302_FOUND)
        except UnexpectedResponseException:
            return APIResponse.error(msg="Unexpected response from remote server.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        except AuthenticationException:
            return APIResponse.error(msg="Wrong username or password.", status_code=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    async def logout(payload: dict) -> APIResponse:
        try:
            # 從 Sis 登出
            SIS.logout(
                SISConn(
                    student_id=payload["s_id"],
                    php_session_id=payload["sis"]["session_id"],
                    last_login_timestamp=payload["sis"]["login_timestamp"]
                )
            )
            
            # 從 iCloud 登出
            iCloud.logout(
                SISConn(
                    student_id=payload["s_id"],
                    php_session_id=payload["ic"]["session_id"],
                    last_login_timestamp=payload["ic"]["login_timestamp"]
                )
            )

            return APIResponse.success(msg="Logout successfully.", status_code=status.HTTP_200_OK)
        except Exception as e:
            APIResponse.error(msg=str(e), status_code=status.HTTP_503_SERVICE_UNAVAILABLE)