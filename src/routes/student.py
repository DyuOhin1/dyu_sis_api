from pickle import FALSE
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from icloud.personal.constants.lang import Lang
from starlette import status

from src.models.GraduationType import GraduationType
from src.models.student import StudentInfo
from src.services.graduation_service import GraduationService
from src.services.student_service import StudentService
from src.utils.auth import verify_jwt_token
from src.utils.connect_parser import ConnectionParser
from src.utils.exception import StudentInfoNotFoundException, NotFoundException, InvalidFormatException

router = APIRouter(prefix="")

@router.get(
    "",
    summary="取得個人資訊",
    description="""
    從 [學生資訊系統](https://sis.dyu.edu.tw/) 取得。
    """,
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
                                    "student_id": {"type": "string", "description": "學號"},
                                    "name": {"type": "string", "description": "學生姓名"},
                                    "gender": {"type": "string", "description": "性別"},
                                    "id": {"type": "string", "description": "身分證字號"},
                                    "birth_date": {"type": "string", "description": "生日"},
                                    "economic_status": {"type": "string", "description": "經濟狀況"},
                                    "identity_type": {"type": "string", "description": "學生身分"},
                                    "marital_status": {"type": "string", "description": "婚姻狀況"},
                                    "spouse_name": {"type": "string", "description": "配偶姓名"},
                                    "religion": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string", "description": "宗教信仰"},
                                            "other": {"type": "string", "description": "其他宗教信仰說明"}
                                        }
                                    },
                                    "disabilities": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string", "description": "身心障礙狀況"},
                                            "other": {"type": "string", "description": "其他身心障礙說明"}
                                        }
                                    },
                                    "health_history": {
                                        "type": "object",
                                        "properties": {
                                            "disease": {"type": "string", "description": "健康狀況"},
                                            "other": {"type": "string", "description": "其他健康狀況說明"}
                                        }
                                    },
                                    "emergency_contact": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string", "description": "緊急聯絡人姓名"},
                                            "relation": {"type": "string", "description": "與學生關係"},
                                            "phone": {"type": "string", "description": "緊急聯絡人電話"}
                                        }
                                    },
                                    "education": {
                                        "type": "object",
                                        "properties": {
                                            "program": {"type": "string", "description": "就讀學制"},
                                            "department": {"type": "string", "description": "系所名稱"},
                                            "class": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "string", "description": "班級"},
                                                    "teacher": {"type": "string", "description": "班導師"}
                                                }
                                            },
                                            "mentor": {"type": "string", "description": "指導教授"},
                                            "previous_school": {"type": "string", "description": "畢業學校"},
                                            "graduation_date": {"type": "string", "description": "畢業日期"}
                                        }
                                    },
                                    "contact_info": {
                                        "type": "object",
                                        "properties": {
                                            "mailing_address": {"type": "string", "description": "通訊地址"},
                                            "permanent_address": {"type": "string", "description": "戶籍地址"},
                                            "telephone": {"type": "string", "description": "家庭電話"},
                                            "mobile": {"type": "string", "description": "手機"}
                                        }
                                    },
                                    "dormitory": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "description": "住宿狀況"},
                                            "room_number": {"type": "string", "description": "房間號碼"},
                                            "address": {"type": "string", "description": "住宿地址"}
                                        }
                                    },
                                    "email": {
                                        "type": "object",
                                        "properties": {
                                            "campus": {"type": "string", "description": "校園信箱"},
                                            "personal": {"type": "string", "description": "個人信箱"}
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["data"]
                    },
                    "example": {
                        "data": {
                            "student_id": "A0000000",
                            "name": "王小明",
                            "gender": "男",
                            "id": "A123456789",
                            "birth_date": "92年01月01日",
                            "economic_status": "普通",
                            "identity_type": "一般生",
                            "marital_status": "未婚",
                            "spouse_name": "",
                            "religion": {
                                "id": "無",
                                "other": ""
                            },
                            "disabilities": {
                                "id": "無",
                                "other": ""
                            },
                            "health_history": {
                                "disease": "無",
                                "other": ""
                            },
                            "emergency_contact": {
                                "name": "王大明",
                                "relation": "父",
                                "phone": "0900000000"
                            },
                            "disabilities_certificate": "",
                            "education": {
                                "program": "大學日間部",
                                "department": "資訊工程學系",
                                "class": {
                                    "id": "2年1班",
                                    "teacher": "李教授"
                                },
                                "mentor": "王教授",
                                "previous_school": "某高中",
                                "graduation_date": "111年06月"
                            },
                            "contact_info": {
                                "mailing_address": "100台北市中正區重慶南路一段1號",
                                "permanent_address": "100台北市中正區重慶南路一段1號",
                                "telephone": "0200000000",
                                "mobile": "0900000000"
                            },
                            "dormitory": {
                                "status": "學校宿舍",
                                "room_number": "0000-A",
                                "address": "彰化縣大村鄉學府路168號"
                            },
                            "email": {
                                "campus": "a0000000@nfku.edu.tw",
                                "personal": "example@example.com"
                            }
                        }
                    }
                }
            }
        }
    }
)
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


@router.get(
    "/semester",
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
                                        "smye": {
                                            "type": "integer",
                                            "description": "學年度"
                                        },
                                        "smty": {
                                            "type": "integer",
                                            "description": "學期 (1:上學期, 2:下學期)"
                                        }
                                    },
                                    "required": ["smye", "smty"]
                                },
                                "description": "學期列表"
                            }
                        },
                        "required": ["data"]
                    },
                    "example": {
                        "data": [
                            {"smye": 113, "smty": 2},
                            {"smye": 113, "smty": 1},
                            {"smye": 112, "smty": 2},
                            {"smye": 112, "smty": 1}
                        ]
                    }
                }
            }
        }
    },
    summary="取得個人在學學年資訊",
    description="""
    取 [iCloud](https://icloud.dyu.edu.tw) 取得個人在學學年度資訊。
    """
)
async def get_student_semester(
        refresh: bool = Query(False, description="強制更新快取"),
        token: dict = Depends(verify_jwt_token),
):

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

@router.get(
    "/course",
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
                                    "type": {
                                        "type": "integer",
                                        "description": "課表類型"
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "學生姓名"
                                    },
                                    "academicYear": {
                                        "type": "integer",
                                        "description": "學年度"
                                    },
                                    "semester": {
                                        "type": "string",
                                        "description": "學期"
                                    },
                                    "updateDate": {
                                        "type": "string",
                                        "description": "更新日期"
                                    },
                                    "departmentId": {
                                        "type": "string",
                                        "description": "系所編號"
                                    },
                                    "deptTitleShort": {
                                        "type": "string",
                                        "description": "系所簡稱"
                                    },
                                    "deptTitle": {
                                        "type": "string",
                                        "description": "系所全名"
                                    },
                                    "schoolSystemId": {
                                        "type": "string",
                                        "description": "學制代碼"
                                    },
                                    "schoolSystemTitle": {
                                        "type": "string",
                                        "description": "學制名稱"
                                    },
                                    "schedule": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "scheduleName": {
                                                    "type": "string",
                                                    "description": "課程名稱"
                                                },
                                                "abbScheduleName": {
                                                    "type": "string",
                                                    "description": "課程簡稱"
                                                },
                                                "courseId": {
                                                    "type": "string",
                                                    "description": "課程ID"
                                                },
                                                "courseCode": {
                                                    "type": "string",
                                                    "description": "課程代碼"
                                                },
                                                "week": {
                                                    "type": "integer",
                                                    "description": "星期幾 (1-7)"
                                                },
                                                "period": {
                                                    "type": "integer",
                                                    "description": "第幾節課"
                                                },
                                                "classroom": {
                                                    "type": "string",
                                                    "description": "教室"
                                                },
                                                "teacher": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "id": {
                                                                "type": "string",
                                                                "description": "教師ID"
                                                            },
                                                            "name": {
                                                                "type": "string",
                                                                "description": "教師姓名"
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }},
    summary="取得指定學期課表",
    description="""
    取得指定學期課表，若未指定，預設則為取得當學期課表。
    """
)
async def get_course_info(
    refresh: bool = Query(False, description="強制更新快取"),
    year: Optional[str] = Query(None, description="學年"),
    semester: Optional[str] = Query(None, description="學期"),
    token: dict = Depends(verify_jwt_token)
):
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

@router.get(
    "/course/attendance",
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
                                    "year": {
                                        "type": "string",
                                        "description": "學年度"
                                    },
                                    "sem": {
                                        "type": "string",
                                        "description": "學期"
                                    },
                                    "all_data": {
                                        "type": "object",
                                        "properties": {
                                            "total": {
                                                "type": "object",
                                                "properties": {
                                                    "attend": {"type": "integer", "description": "出席次數"},
                                                    "late": {"type": "integer", "description": "遲到次數"},
                                                    "leave_early": {"type": "integer", "description": "早退次數"},
                                                    "absent": {"type": "integer", "description": "缺席次數"},
                                                    "take_leave": {"type": "integer", "description": "請假次數"},
                                                    "attendence": {"type": "integer", "description": "出席率百分比"}
                                                }
                                            },
                                            "course_list": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "subject_code": {"type": "string", "description": "課程代碼"},
                                                        "subject_name": {"type": "string", "description": "課程名稱"},
                                                        "attend": {"type": "integer", "description": "出席次數"},
                                                        "late": {"type": "integer", "description": "遲到次數"},
                                                        "leave_early": {"type": "integer", "description": "早退次數"},
                                                        "absent": {"type": "integer", "description": "缺席次數"},
                                                        "take_leave": {"type": "integer", "description": "請假次數"},
                                                        "attendence": {"type": "integer",
                                                                       "description": "出席率百分比"},
                                                        "detail": {
                                                            "type": "object",
                                                            "properties": {
                                                                "sum_roll_call": {"type": "integer",
                                                                                  "description": "點名總次數"},
                                                                "data": {
                                                                    "type": "array",
                                                                    "items": {
                                                                        "type": "object",
                                                                        "properties": {
                                                                            "date": {"type": "string",
                                                                                     "description": "日期"},
                                                                            "day": {"type": "integer",
                                                                                    "description": "星期幾"},
                                                                            "period": {"type": "integer",
                                                                                       "description": "節次"},
                                                                            "attend_state": {"type": "integer",
                                                                                             "description": "出席狀態碼"}
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
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
    summary="取得指定學期課程出席率",
    description="取得指定學期課程出席率，若為指定，預設則為取得當前學年度課程出席率。"
)
async def get_course_attendance_info(
        refresh: bool = Query(False, description="強制更新快取"),
        year: Optional[str] = Query(None, description="學年"),
        semester: Optional[str] = Query(None, description="學期"),
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

@router.get(
    "/course/warning",
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
                                        "course_id": {"type": "string", "description": "課程代碼"},
                                        "course_name": {"type": "string", "description": "課程名稱"},
                                        "is_required": {"type": "boolean", "description": "是否必修"},
                                        "teacher_name": {"type": "string", "description": "授課教師"},
                                        "is_warning": {"type": "boolean", "description": "是否有警告"},
                                        "warning_message": {"type": "string", "description": "警告訊息"},
                                        "credit": {"type": "integer", "description": "學分數"},
                                        "comment": {"type": "string", "description": "評論"}
                                    },
                                    "required": ["course_id", "course_name", "is_required", "teacher_name", "is_warning", "warning_message", "credit", "comment"]
                                }
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="取得課程預警",
    description="""
    取得課程預警，因來源資料只能取得當前學年度資料，因此無法指定取得其他學年度資料。
    """
)
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

@router.get(
    "/course/grade",
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
                                        "course": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "title": {"type": "string", "description": "課程名稱"},
                                                    "enTitle": {"type": "string", "description": "英文課程名稱"},
                                                    "codeNum": {"type": "string", "description": "課號"},
                                                    "cla": {"type": "string", "description": "課程代碼"},
                                                    "compulsory": {"type": "string", "description": "必/選修"},
                                                    "credit": {"type": "integer", "description": "學分數"},
                                                    "score": {"type": "string", "description": "成績"},
                                                    "note": {"type": "string", "description": "備註"}
                                                }
                                            }
                                        },
                                        "complex": {
                                            "type": "object",
                                            "properties": {
                                                "totalAverage": {"type": "number", "description": "總平均"},
                                                "conductGrade": {"type": "integer", "description": "操行成績"},
                                                "earnCredit": {"type": "integer", "description": "實得學分"},
                                                "credit": {"type": "integer", "description": "修課學分"},
                                                "classRank": {"type": "integer", "description": "班排名"},
                                                "classPeopleNum": {"type": "integer", "description": "班級人數"},
                                                "semRank": {"type": "integer", "description": "系排名"},
                                                "semPeopleNum": {"type": "integer", "description": "系人數"}
                                            }
                                        },
                                        "t": {
                                            "type": "object",
                                            "properties": {
                                                "smye": {"type": "integer", "description": "學年"},
                                                "smty": {"type": "integer", "description": "學期"}
                                            }
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
    summary="取得指定學年度課程成績",
    description="取得指定學期課程成績，若為指定則將取得上一學期課程成績。"
)
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
@router.get(
    "/barcode",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "string",
                                "description": "Base64編碼的圖片資料",
                                "format": "byte"
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="取得個人學生證證件學號條碼照片",
    description="取得個人學生證證件學號條碼照片，以 Base64 編碼呈現。"
)
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


@router.get(
    "/image",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "string",
                                "description": "Base64編碼的圖片資料",
                                "format": "byte"
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        }
    },
    summary="取得個人學生證證件個人大頭照照片",
    description="取得個人學生證證件個人大頭照照片，以 Base64 編碼呈現。"
)
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

@router.get(
    "/injury",
    responses={
        200: {
            "description": "成功獲取學生健康紀錄資料",
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
                                        "heal_time": {
                                            "type": "string",
                                            "description": "就醫時間"
                                        },
                                        "heal_campus": {
                                            "type": "string",
                                            "description": "就醫地點類型"
                                        },
                                        "heal_name": {
                                            "type": "string",
                                            "description": "傷病名稱"
                                        },
                                        "heal_place": {
                                            "type": "string",
                                            "description": "受傷地點"
                                        },
                                        "heal_wound": {
                                            "type": "string",
                                            "description": "受傷部位"
                                        },
                                        "heal_process": {
                                            "type": "string",
                                            "description": "處理過程"
                                        },
                                        "t": {
                                            "type": "object",
                                            "properties": {
                                                "smye": {
                                                    "type": "integer",
                                                    "description": "學年"
                                                },
                                                "smty": {
                                                    "type": "integer",
                                                    "description": "學期"
                                                }
                                            }
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
    summary="取得個人在校受傷紀錄",
    description="取得個人在校受傷紀錄"
)
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

@router.get(
    "/military",
    responses={
        200: {
            "description": "成功獲取學生兵役資料",
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
                                        "mil_status": {
                                            "type": "string",
                                            "description": "兵役狀態"
                                        },
                                        "grad_date": {
                                            "type": "string",
                                            "description": "預計畢業日期"
                                        },
                                        "t": {
                                            "type": "object",
                                            "properties": {
                                                "smye": {
                                                    "type": "integer",
                                                    "description": "學年"
                                                },
                                                "smty": {
                                                    "type": "integer",
                                                    "description": "學期"
                                                }
                                            }
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
    summary="取得個人兵役紀錄",
    description="取得個人兵役紀錄"
)
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

@router.get(
    "/advisor",
    responses={
        200: {
            "description": "成功獲取學生導師資料",
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
                                        "teno": {
                                            "type": "string",
                                            "description": "教師編號"
                                        },
                                        "epno": {
                                            "type": "string",
                                            "description": "教師代碼"
                                        },
                                        "tutor_status": {
                                            "type": "string",
                                            "description": "導師狀態碼"
                                        },
                                        "t": {
                                            "type": "object",
                                            "properties": {
                                                "smye": {
                                                    "type": "integer",
                                                    "description": "學年"
                                                },
                                                "smty": {
                                                    "type": "integer",
                                                    "description": "學期"
                                                }
                                            }
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
    summary="取得個人導師列表",
    description="取得個人導師列表，其中 teno 可用於取得該導師相關聯絡訊息。tutor_status 有三狀態：A 師徒導師、B 系主任、0 班級導師。"
)
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