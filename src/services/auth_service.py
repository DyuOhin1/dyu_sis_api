from typing import Union

from icloud.icloud import iCloud
from sis.connection import Connection as SISConn
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
from sis.student_information_system import StudentInformationSystem as SIS
from starlette import status

from src.config import settings
from src.models.api_response import APIResponse
from src.models.auth import LoginRequest, JWTPayload, Connection, LoginSuccessResponse
from src.utils.auth import create_jwt_token
from src.utils.connect_parser import ConnectionParser
from src.utils.time_unit import TimeUnit


class AuthService:
    @staticmethod
    async def login(
            login_data: LoginRequest,
    ) -> Union[LoginSuccessResponse, APIResponse]:
        # login to Sis
        sis_conn = SIS.login(login_data.username, login_data.password)

        # login to iCloud
        icloud_conn = iCloud.login(login_data.username, login_data.password)

        payload = JWTPayload(
            s_id=login_data.username.upper(),
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

    @staticmethod
    async def logout(payload: dict):
        # 從 Sis 登出
        SIS.logout(
            ConnectionParser.parse_connection(payload, False)
        )

        # 從 iCloud 登出
        iCloud.logout(
            ConnectionParser.parse_connection(payload, True)
        )

    @staticmethod
    async def test_login_status(
            payload: dict
    ) -> dict:
        sis_conn = ConnectionParser.parse_connection(payload, False)
        icloud_conn = ConnectionParser.parse_connection(payload, True)

        return {
            "sis" : SIS.is_logged_in(sis_conn),
            "ic" : iCloud.is_logged_in(icloud_conn)
        }