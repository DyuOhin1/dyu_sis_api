from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from src.config import settings
from src.utils.time_unit import TimeUnit


class Connection(BaseModel):
    session_id: str
    login_timestamp: float

class LoginRequest(BaseModel):
    username: str
    password: str

class JWTPayload(BaseModel):
    s_id: str
    sis: Connection
    ic: Connection

class LoginSuccessResponse(BaseModel):
    access_token: str = "jwt_token"
    token_type: str = "Bearer"
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * TimeUnit.MINUTE