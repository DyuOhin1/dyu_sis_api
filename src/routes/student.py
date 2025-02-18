from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from icloud.personal.constants.lang import Lang
from starlette import status

from src.models.GraduationType import GraduationType
from src.services.graduation_service import GraduationService
from src.services.student_service import StudentService
from src.utils.auth import verify_jwt_token
from src.utils.connect_parser import ConnectionParser
from src.utils.exception import StudentInfoNotFoundException, NotFoundException, InvalidFormatException

router = APIRouter(prefix="")

@router.get("")
async def get_student_info(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)

        info = await StudentService.get_student_info(sis_conn, refresh)

        return {
            "data": info
        }
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except StudentInfoNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/semester")
async def get_student_semester(
        refresh: bool = Query(False, description="強制更新快取"),
        token: dict = Depends(verify_jwt_token)
):
    """
    sdsds

    Args:
        refresh: 是否強制更新快取
        token: JWT token
    """

    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)

        data = await StudentService.get_student_semester(
            icloud_conn,
            refresh,
        )

        return {
            "data": data
        }

    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/course")
async def get_course_info(
    refresh: bool = Query(False, description="強制更新快取"),
    year: Optional[str] = Query(None, description="學年 (例如: 112)"),
    semester: Optional[str] = Query(None, description="學期 (1 或 2)"),
    token: dict = Depends(verify_jwt_token)
):
    """
    取得課程資訊
    
    Args:
        refresh: 是否強制更新快取
        year: 學年，例如：112
        semester: 學期，1 或 2
        token: JWT token
    """
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_course_timetable(
            icloud_conn,
            refresh,
            year=year,
            seme=semester
        )
        return {
            "data" : data
        }
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/course/attendance")
async def get_course_attendance_info(
        refresh: bool = Query(False, description="強制更新快取"),
        year: Optional[str] = Query(None, description="學年 (例如: 112)"),
        semester: Optional[str] = Query(None, description="學期 (1 或 2)"),
        token: dict = Depends(verify_jwt_token)
):
        try:
            icloud_conn = ConnectionParser.parse_connection(token, True)
            data = await StudentService.get_course_attendance_info(
                icloud_conn,
                refresh,
                year=year,
                semester=semester
            )
            return {
                "data": data
            }
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

@router.get("/course/warning")
async def get_course_warning(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)

        data = await StudentService.get_course_warning(
            sis_conn,
            refresh
        )

        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/course/grade")
async def get_grade(
    year: Optional[str] = Query(None, description="學年 (例如: 112)"),
    semester: Optional[str] = Query(None, description="學期 (1 或 2)"),
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_annual_grade(icloud_conn, year, semester, refresh)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# 其他個人資訊路由
@router.get("/barcode")
async def get_barcode(
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await StudentService.get_barcode(sis_conn)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/image")
async def get_image(
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await StudentService.get_personal_image(sis_conn)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/injury")
async def get_injury(
        refresh: bool = Query(False, description="強制更新快取"),
        token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_injury(icloud_conn, refresh)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/military")
async def get_military(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_military(icloud_conn, refresh)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/advisors")
async def get_advisors(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_advisors(icloud_conn, refresh)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/advisor/{advisor_id}")
async def get_advisor_info(
    advisor_id: str,
    token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_advisor_info(icloud_conn, advisor_id)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/rewards-and-penalties")
async def get_rewards_and_penalties(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_rewards_and_penalties(icloud_conn, refresh)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/enrollment")
async def get_enrollment(
    lang : Lang = Lang.ZH_TW,
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_enrollment(icloud_conn, lang, refresh)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/scholarship")
async def get_scholarship(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_scholarship(icloud_conn, refresh)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/printer-point")
async def get_printer_point(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_printer_point(icloud_conn, refresh)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/graduation")
async def get_graduation_info(
    graduation_type: GraduationType,
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await GraduationService.get_graduation(sis_conn, graduation_type, refresh)

        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except InvalidFormatException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/dorm")
async def get_dorm(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        icloud_conn = ConnectionParser.parse_connection(token, True)
        data = await StudentService.get_dorm(icloud_conn, refresh)
        return {"data" : data}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str("remote server session error. check: " + str(e))
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )