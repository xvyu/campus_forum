"""蓝图包初始化：注册 7 个业务蓝图"""
from __future__ import annotations
from flask import Flask, make_response, request


def register_blueprints(app: Flask) -> None:
    """延迟导入避免循环引用"""
    from .common import common_bp
    from .auth import auth_bp
    from .post import post_bp
    from .comment import comment_bp
    from .board import board_bp
    from .user import user_bp
    from .notification import notification_bp
    from .admin import admin_bp
    from .favorite import favorite_bp

    blueprints = [
        (common_bp, "/api"),
        (auth_bp, "/api/auth"),
        (user_bp, "/api/users"),
        (post_bp, "/api/posts"),
        (comment_bp, "/api/comments"),
        (board_bp, "/api/boards"),
        (notification_bp, "/api/notifications"),
        (admin_bp, "/api/admin"),
        (favorite_bp, "/api/favorites"),
    ]

    for bp, url_prefix in blueprints:
        app.register_blueprint(bp, url_prefix=url_prefix)
        app.logger.info(f"   ├─ Blueprint registered: {bp.name} -> {url_prefix}")

    # CORS 预检兜底：所有 OPTIONS 都直接 204 通过
    # 关键：必须支持 credentials，且 origin 必须回显
    @app.route("/api/<path:path>", methods=["OPTIONS"], provide_automatic_options=False)
    def cors_preflight(path):
        origin = request.headers.get("Origin", "*")
        resp = make_response("", 204)
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Max-Age"] = "86400"
        resp.headers["Vary"] = "Origin"
        return resp

    app.logger.info(f"OK {len(blueprints)} blueprints registered + CORS preflight handler")
