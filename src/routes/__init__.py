from .auth import router as auth_router
from .student import router as student_router
from .leave import router as leave_router
from .graduation import router as graduation_router

__all__ = ["auth_router", "student_router", "leave_router", "graduation_router"] 