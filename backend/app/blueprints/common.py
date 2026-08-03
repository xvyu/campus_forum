"""公共蓝图：健康检查、版本信息、字典"""
from datetime import datetime
from flask import Blueprint, current_app
from app.errors import success

common_bp = Blueprint("common", __name__)


@common_bp.route("/health", methods=["GET"])
def health_check():
    """健康检查：MySQL + Redis 状态"""
    from app.extensions import db, redis_client

    health = {
        "status": "healthy",
        "version": current_app.config.get("APP_VERSION", "0.1.0"),
        "env": current_app.config.get("ENV", "unknown"),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        db.session.execute(db.text("SELECT 1"))
        health["mysql"] = "ok"
    except Exception as e:
        health["mysql"] = f"error: {str(e)[:50]}"

    try:
        redis_client.ping()
        health["redis"] = "ok"
    except Exception as e:
        health["redis"] = f"error: {str(e)[:50]}"

    return success(data=health, message="服务运行正常")


@common_bp.route("/version", methods=["GET"])
def version_info():
    """版本信息"""
    return success(
        data={
            "app_name": current_app.config.get("APP_NAME", "Campus Forum"),
            "version": current_app.config.get("APP_VERSION", "0.1.0"),
            "stage": "V0.1 (MVP)",
        }
    )


@common_bp.route("/", methods=["GET"])
def index():
    """根路径"""
    return success(
        data={"message": "Campus Forum API 服务", "docs": "/api/version"},
        message="ok",
    )
