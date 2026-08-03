"""统一响应格式：{code, message, data} + 4 位错误码体系"""
from __future__ import annotations
from typing import Any, Optional


def success_response(data: Any = None, message: str = "ok") -> dict:
    """成功响应"""
    return {"code": 0, "message": message, "data": data}


def error_response(
    code: int,
    message: str,
    data: Optional[Any] = None,
    http_status: int = 200,
) -> tuple[dict, int]:
    """错误响应（业务错误也返回 200，HTTP 状态由 code 决定）"""
    return ({"code": code, "message": message, "data": data}, http_status)


def paginate_response(
    items: list,
    next_cursor: Optional[str] = None,
    has_more: bool = False,
    total: Optional[int] = None,
) -> dict:
    """游标分页响应"""
    data = {"list": items, "next_cursor": next_cursor, "has_more": has_more}
    if total is not None:
        data["total"] = total
    return success_response(data=data)


class ErrorCode:
    """错误码定义（4 位）"""

    SYSTEM_ERROR = 1000
    PARAM_ERROR = 1001
    NOT_FOUND = 1002
    UNAUTHORIZED = 1003
    FORBIDDEN = 1004
    RATE_LIMIT = 1005
    METHOD_NOT_ALLOWED = 1006
    INTERNAL_ERROR = 1500

    NOT_LOGIN = 2000
    ACCOUNT_NOT_EXIST = 2001
    PASSWORD_ERROR = 2002
    CAPTCHA_ERROR = 2003
    CAPTCHA_EXPIRED = 2004
    ACCOUNT_LOCKED = 2005
    EMAIL_UNVERIFIED = 2006

    STUDENT_ID_REGISTERED = 3000
    EMAIL_REGISTERED = 3001
    TITLE_TOO_LONG = 3002
    CONTENT_TOO_LONG = 3003
    SENSITIVE_WORD = 3004
    ANONYMOUS_NOT_BELONG = 3005
    COMMENT_DEPTH_LIMIT = 3006

    NOT_ADMIN = 4000
    NOT_AUDIT = 4001
    REPORT_NOT_EXIST = 4002
    USER_NOT_EXIST = 4003
    BAN_DURATION_INVALID = 4004

    EMAIL_SEND_FAILED = 5000
    REDIS_UNAVAILABLE = 5001
    OSS_UPLOAD_FAILED = 5002
