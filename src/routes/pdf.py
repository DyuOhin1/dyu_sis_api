from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from ..services.pdf_service import PDFService
from ..utils.auth import verify_jwt_token
from ..utils.connect_parser import ConnectionParser
from ..utils.exception import StudentInfoNotFoundException

router = APIRouter(prefix="")

@router.get("/graduation")
async def get_graduation_overview_pdf(
    token: dict = Depends(verify_jwt_token)
):
    try:

        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await PDFService.graduation(sis_conn)
        return {"data" : data}
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

@router.get("/course")
async def get_course_list_pdf(
    year: Optional[str] = Query(None, description="學年 (例如: 112)"),
    semester: Optional[str] = Query(None, description="學期 (1 或 2)"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        data = await PDFService.course(
            ConnectionParser.parse_connection(token, False),
            ConnectionParser.parse_connection(token, True),
            year,
            semester
        )

        return {
            "data": data
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

@router.get("/enrollment")
async def get_proof_or_enrollment_pdf(
    year: Optional[str] = Query(None, description="學年 (例如: 112)"),
    semester: Optional[str] = Query(None, description="學期 (1 或 2)"),
    token: dict = Depends(verify_jwt_token)
):
    try:

        data = await PDFService.enrollment(
            ConnectionParser.parse_connection(token, True),
            year,
            semester
        )

        return {
            "data": data
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

@router.get("/timetable")
async def get_course_timetable(
    year: Optional[str] = Query(None, description="學年 (例如: 112)"),
    semester: Optional[str] = Query(None, description="學期 (1 或 2)"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        data = await PDFService.timetable(
            ConnectionParser.parse_connection(token, True),
            year,
            semester
        )

        return {
            "data": data
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