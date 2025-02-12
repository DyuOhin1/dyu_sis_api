from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query
from typing import List
from ..models.leave import LeaveRequest, LeaveResponse
from ..services.leave_service import LeaveService
from ..utils.auth import verify_jwt_token

router = APIRouter()

@router.post("", response_model=LeaveResponse)
async def create_leave(
    leave_request: LeaveRequest,
    token: dict = Depends(verify_jwt_token)
):
    student_id = token["s_id"]
    return await LeaveService.create_leave(student_id, leave_request)

@router.get("", response_model=List[LeaveResponse])
async def get_leave_history(token: dict = Depends(verify_jwt_token)):
    student_id = token["s_id"]
    return await LeaveService.get_leave_history(student_id)

@router.delete("/{leave_id}")
async def cancel_leave(
    leave_id: str,
    token: dict = Depends(verify_jwt_token)
):
    student_id = token["s_id"]
    success = await LeaveService.cancel_leave(student_id, leave_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="銷假失敗"
        )
    return {"message": "銷假成功"}

@router.post("/document")
async def upload_leave_document(
    file: UploadFile = File(...),
    token: dict = Depends(verify_jwt_token)
):
    student_id = token["s_id"]
    content = await file.read()
    doc_id = await LeaveService.upload_document(
        student_id,
        content,
        file.filename
    )
    return {"document_id": doc_id} 