from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query, Form, Path
from starlette import status

from sis.course.leave.constant.departments import Department
from sis.course.leave.constant.leave_type import LeaveType
from src.services.leave_service import LeaveService
from src.utils.auth import verify_jwt_token
from src.utils.connect_parser import ConnectionParser
from src.utils.exception import UnsupportedFileTypeException, OutOfFileSizeException, InvalidFormatException

router = APIRouter()
@router.get(
    "/types",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "請假類型代碼"
                                        },
                                        "locale": {
                                            "type": "object",
                                            "properties": {
                                                "en": {
                                                    "type": "string",
                                                    "description": "英文假別名稱"
                                                },
                                                "zh_tw": {
                                                    "type": "string",
                                                    "description": "中文假別名稱"
                                                }
                                            },
                                            "required": ["en", "zh_tw"]
                                        }
                                    },
                                    "required": ["id", "locale"]
                                }
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="取得可使用請假假別",
    description="取得可使用請假假別，用於送出請假時使用。"
)
async def get_leave_types():
    try:
        data = await LeaveService.get_leave_types()

        return {
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/departments",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "單位或部門代碼"
                                        },
                                        "locale": {
                                            "type": "object",
                                            "properties": {
                                                "en": {
                                                    "type": "string",
                                                    "description": "英文名稱"
                                                },
                                                "zh_tw": {
                                                    "type": "string",
                                                    "description": "中文名稱"
                                                }
                                            },
                                            "required": ["en", "zh_tw"]
                                        }
                                    },
                                    "required": ["id", "locale"]
                                }
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="取得請假可使用公假派出單位",
    description="取得請假可使用公假派出單位，用於送出請假時使用。"
)
async def get_school_departments():
    try:
        data = await LeaveService.get_school_departments()

        return {
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/course/available",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "course_id": {
                                            "type": "string",
                                            "description": "課程編號"
                                        },
                                        "course_period": {
                                            "type": "integer",
                                            "description": "課程節次"
                                        },
                                        "course_name": {
                                            "type": "string",
                                            "description": "課程名稱"
                                        },
                                        "course_teacher": {
                                            "type": "object",
                                            "properties": {
                                                "teacher_id": {
                                                    "type": "string",
                                                    "description": "教師編號"
                                                },
                                                "teacher_name": {
                                                    "type": "string",
                                                    "description": "教師姓名"
                                                }
                                            },
                                            "required": ["teacher_id", "teacher_name"]
                                        },
                                        "location": {
                                            "type": ["string", "null"],
                                            "description": "上課地點"
                                        },
                                        "course_date": {
                                            "type": "string",
                                            "format": "date",
                                            "description": "上課日期"
                                        },
                                        "course_weekday": {
                                            "type": "integer",
                                            "description": "星期幾上課（1=星期一，2=星期二，依此類推）"
                                        },
                                        "course_pending": {
                                            "type": "boolean",
                                            "description": "是否已請過"
                                        }
                                    },
                                    "required": [
                                        "course_id",
                                        "course_period",
                                        "course_name",
                                        "course_teacher",
                                        "location",
                                        "course_date",
                                        "course_weekday",
                                        "course_pending"
                                    ]
                                }
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="取得指定日期內可請假之課程",
    description="取得指定日期內可請假之課程，若未指定起始以及結束查詢日期，則以當天的日期作為預設值。"
)
async def get_course_info(
    start_date: Optional[date] = Query(date.today(), description="查詢起始日期"),
    end_date: Optional[date] = Query(date.today(), description="查詢結束日期"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        student_id = ConnectionParser.parse_student_id(token)

        if end_date < start_date:
            raise ValueError("End date must be before start date")

        data = await LeaveService.get_course_info(
            student_id,
            start_date,
            end_date
        )

        return {
            "data": data
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/course",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "訊息內容"
                                }
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="送出課程請假請求",
    description="送出課程請假請求，course_info 請使用 GET /api/v1/leave/course/available 返回的課程資料，當作此處的參數，格式為 JSON Array；leave_type 請使用 GET /api/v1/leave/types 請假假別；from_dept 則使用 GET /api/v1/leave/departments 取得公假派出單位（假別為公假才曲要填寫此欄位）。"
)
async def create_leave(
    course_info: str = Form(..., description="欲請假課程(JSON Array)"),
    leave_type: LeaveType = Form(..., description="請假假別"),
    reason: str = Form(..., description="請假事由"),
    from_dept: Optional[Department] = Form(None, description="公假派出單位"),
    file: Optional[UploadFile] = File(None, description="請假證明"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        response_data = await LeaveService.create_leave(
            sis_conn,
            course_info,
            leave_type,
            reason,
            from_dept,
            file
        )
        return {"data": response_data}
    except UnsupportedFileTypeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except OutOfFileSizeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidFormatException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/history",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "請假編號"
                                        },
                                        "category": {
                                            "type": "string",
                                            "description": "請假分類"
                                        },
                                        "leave_type": {
                                            "type": "string",
                                            "description": "請假類型"
                                        },
                                        "reason": {
                                            "type": "string",
                                            "description": "請假原因"
                                        },
                                        "leave_status": {
                                            "type": "string",
                                            "description": "審核狀態"
                                        },
                                        "has_message": {
                                            "type": "boolean",
                                            "description": "是否有審核訊息"
                                        },
                                        "date": {
                                            "type": "string",
                                            "description": "請假日期，格式為 YYYY-MM-DD"
                                        },
                                        "document_link": {
                                            "type": ["string", "null"],
                                            "description": "相關證明文件連結"
                                        },
                                        "details": {
                                            "type": ["object", "null"],
                                            "description": "請假詳細資訊，若無為 null"
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="取得課程請假歷史紀錄",
    description="取得課程請假歷史紀錄"
)
async def get_leave_history(token: dict = Depends(verify_jwt_token)):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await LeaveService.get_leave_history(sis_conn)

        return {
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{leave_id}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "course_name": {
                                            "type": "string",
                                            "description": "課程名稱"
                                        },
                                        "status": {
                                            "type": "string",
                                            "description": "審核結果狀態（例如：准假、不准假）"
                                        },
                                        "status_description": {
                                            "type": "string",
                                            "description": "狀態說明（例如：完成、審核中、取消請假）"
                                        },
                                        "period": {
                                            "type": "string",
                                            "description": "課程節次"
                                        },
                                        "reviewer_name": {
                                            "type": "string",
                                            "description": "審核人姓名"
                                        },
                                        "reviewer_relationship": {
                                            "type": "string",
                                            "description": "審核人與學生的關係（例如：任課老師、導師）"
                                        },
                                        "message": {
                                            "type": ["string", "null"],
                                            "description": "審核回覆訊息，若無為 null"
                                        },
                                        "meeting_name": {
                                            "type": ["string", "null"],
                                            "description": "重大集會請假名稱，若無為 null"
                                        },
                                        "dorm_meeting_name": {
                                            "type": ["string", "null"],
                                            "description": "宿舍防災演練請假名稱，若無為 null"
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="取得課程請假詳細資訊",
    description="取得課程請假詳細資訊"
)
async def get_leave_details(
        leave_id: str = Path(..., description="請假編號"),
        get_message : bool = Query(False),
        token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await LeaveService.get_leave_details(sis_conn, leave_id, get_message)
        return {"data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete(
    "/{leave_id}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object",
                                "properties": {
                                    "success": {
                                        "type": "boolean",
                                        "description": "操作是否成功"
                                    },
                                    "message": {
                                        "type": "string",
                                        "description": "操作結果訊息"
                                    }
                                },
                                "required": ["success", "message"]
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="取消請假",
    description="取消請假"
)
async def cancel_leave(
    leave_id: str = Path(..., description="請假編號"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        data = await LeaveService.cancel_leave(sis_conn, leave_id)
        return {"data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch(
    "/{leave_id}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "object",
                                "properties": {
                                    "success": {
                                        "type": "boolean",
                                        "description": "操作是否成功"
                                    },
                                    "message": {
                                        "type": "string",
                                        "description": "操作結果訊息"
                                    }
                                },
                                "required": ["success", "message"]
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="補交請假證明文件",
    description="補交請假證明文件"
)
async def upload_document(
    leave_id: str = Path(..., description="請假編號"),
    file: UploadFile = File(..., description="補交證明文件"),
    token: dict = Depends(verify_jwt_token)
):
    try:
        sis_conn = ConnectionParser.parse_connection(token, False)
        response_data = await LeaveService.upload_document(
            sis_conn,
            leave_id,
            file,
        )

        return {"data": response_data}
    except UnsupportedFileTypeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except OutOfFileSizeException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidFormatException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )