"""Flask 应用工厂：支持多配置切换 + 7 个 Blueprint 模块化注册 + 统一错误处理"""
import os
from flask import Flask, g, request
from loguru import logger

from app.config import get_config
from app.extensions import init_extensions
from app.errors import register_error_handlers
from app.blueprints import register_blueprints
from app.utils.auth_token import parse_auth_header


def create_app(config_name: str = None) -> Flask:
    """创建 Flask 应用实例"""
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
    )

    config_class = get_config(config_name)
    app.config.from_object(config_class)
    logger.info(f"[App] 配置加载完成: {config_class.__name__}")

    init_extensions(app)
    logger.info("[App] 扩展初始化完成")

    register_blueprints(app)
    logger.info("[App] 蓝图注册完成")

    register_error_handlers(app)
    logger.info("[App] 统一错误处理注册完成")

    _register_request_hooks(app)

    logger.success(f"[App] Flask 应用创建完成 - env={app.config.get('ENV', 'unknown')}")
    return app


def _register_request_hooks(app: Flask) -> None:
    """请求前后钩子：记录耗时 + Token 鉴权"""
    from flask import request, g
    import time

    @app.before_request
    def _before_request():
        g.start_time = time.time()
        logger.debug(f"[Request] {request.method} {request.path}")

        # 从 Authorization 头中解析 token
        g.user_id = None
        g.role = None
        auth_info = parse_auth_header(request.headers.get("Authorization"))
        if auth_info:
            g.user_id = auth_info["user_id"]
            g.role = auth_info["role"]

    @app.after_request
    def _after_request(response):
        if hasattr(g, "start_time"):
            elapsed = (time.time() - g.start_time) * 1000
            logger.debug(
                f"[Response] {request.method} {request.path} "
                f"status={response.status_code} cost={elapsed:.2f}ms"
            )
        response.headers["X-Powered-By"] = "campus-forum/0.1.0"
        return response
