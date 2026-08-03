"""通知蓝图：站内信 + 5s 轮询 + WebSocket（V0.3 启用）"""
from flask import Blueprint
from app.errors import success

notification_bp = Blueprint("notification", __name__)


@notification_bp.route("/", methods=["GET"])
def index():
    return success(
        data={"module": "notification", "available": False},
        message="notification blueprint ok",
    )
