from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse

from ..services.graduation_service import GraduationService
from ..utils.auth import verify_jwt_token

router = APIRouter()

@router.get("")
async def get_graduation_requirements(
    refresh: bool = Query(False, description="強制更新快取"),
    token: dict = Depends(verify_jwt_token)
):
    student_id = token["s_id"]
    requirements = await GraduationService.get_graduation_requirements(
        student_id,
        refresh
    )
    if not requirements:
        raise HTTPException(
            status_code=404,
            detail="找不到畢業資訊"
        )
    return requirements

@router.get("/pdf")
async def get_graduation_pdf(token: dict = Depends(verify_jwt_token)):
    student_id = token["s_id"]
    pdf_content = await GraduationService.get_graduation_pdf(student_id)
    if not pdf_content:
        raise HTTPException(
            status_code=404,
            detail="找不到畢業審查表"
        )
    return FileResponse(
        pdf_content,
        media_type="application/pdf",
        filename=f"{student_id}_graduation_check.pdf"
    ) 