"""统一错误处理：4 位错误码（1xxx 通用/2xxx 认证/3xxx 业务/4xxx 后台/5xxx 第三方）"""
from flask import jsonify
from loguru import logger
from werkzeug.exceptions import HTTPException


class BizException(Exception):
    """业务异常基类"""

    def __init__(self, code: int, message: str, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class ParamError(BizException):
    def __init__(self, message="参数错误", data=None):
        super().__init__(1001, message, data)


class NotFoundError(BizException):
    def __init__(self, message="资源不存在", data=None):
        super().__init__(1002, message, data)


class UnauthorizedError(BizException):
    def __init__(self, message="未登录或登录已过期", data=None):
        super().__init__(2001, message, data)


class TokenInvalidError(BizException):
    def __init__(self, message="Token 无效", data=None):
        super().__init__(2002, message, data)


class PermissionDeniedError(BizException):
    def __init__(self, message="权限不足", data=None):
        super().__init__(2003, message, data)


class SensitiveWordError(BizException):
    def __init__(self, message="内容包含敏感词", data=None):
        super().__init__(3001, message, data)


class ContentTooLongError(BizException):
    def __init__(self, message="内容超出长度限制", data=None):
        super().__init__(3002, message, data)


class RateLimitError(BizException):
    def __init__(self, message="操作过于频繁，请稍后再试", data=None):
        super().__init__(3003, message, data)


class DuplicateError(BizException):
    def __init__(self, message="重复操作", data=None):
        super().__init__(3004, message, data)


class AdminAuthError(BizException):
    def __init__(self, message="管理员认证失败", data=None):
        super().__init__(4001, message, data)


class EmailSendError(BizException):
    def __init__(self, message="邮件发送失败", data=None):
        super().__init__(5001, message, data)


class RedisError(BizException):
    def __init__(self, message="缓存服务异常", data=None):
        super().__init__(5002, message, data)


def success(data=None, message="ok"):
    """成功响应"""
    return jsonify({"code": 0, "message": message, "data": data})


def fail(code: int, message: str, data=None):
    """失败响应"""
    return jsonify({"code": code, "message": message, "data": data})


def register_error_handlers(app):
    """注册全局错误处理器"""

    @app.errorhandler(BizException)
    def handle_biz_exception(e: BizException):
        logger.warning(f"[BizException] code={e.code} message={e.message}")
        return fail(e.code, e.message, e.data)

    @app.errorhandler(404)
    def handle_404(e):
        return fail(1002, f"资源不存在: {e.description}", None)

    @app.errorhandler(405)
    def handle_405(e):
        return fail(1003, "请求方法不允许", None)

    @app.errorhandler(500)
    def handle_500(e):
        logger.exception(f"[500 Error] {e}")
        return fail(1500, "服务器内部错误", None)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        return fail(e.code, e.description or e.name, None)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e: Exception):
        logger.exception(f"[Unhandled Exception] {type(e).__name__}: {e}")
        return fail(1500, f"未处理异常: {type(e).__name__}", None)
