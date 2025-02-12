from typing import Optional, Any
from pydantic import BaseModel

class APIResponse(BaseModel):
    """API 標準回應格式"""
    status: bool = True
    status_code : int = 200
    msg: Optional[str] = None
    data: Optional[Any] = None

    @staticmethod
    def error(msg: str, status_code : int = 400) -> 'APIResponse':
        """建立錯誤回應"""
        return APIResponse(
            status=False,
            msg=msg,
            status_code = status_code
        )

    @staticmethod
    def success(data: Any = None, msg: Optional[str] = None, status_code : int = 200) -> 'APIResponse':
        """建立成功回應"""
        return APIResponse(
            status=True,
            status_code=status_code,
            msg=msg,
            data=data
        )
