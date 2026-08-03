"""Flask 扩展实例化：单例模式避免循环引用"""
import os
import warnings
warnings.filterwarnings("ignore", message="No valid Redis instance provided")

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
import redis as redis_lib

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
server_session = Session()

redis_client: redis_lib.Redis = None


def init_extensions(app):
    """初始化所有扩展并测试 Redis 连接"""
    global redis_client

    db.init_app(app)
    migrate.init_app(app, db)

    # CORS 配置：用正则支持任意 IP / 端口（开发期方便手机/局域网访问）
    cors.init_app(
        app,
        resources={r"/api/*": {
            "origins": [
                r"http://localhost(:\d+)?",
                r"http://127\.0\.0\.1(:\d+)?",
                r"http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?",
                r"http://172\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?",
                r"http://10\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?",
                # 内网穿透隧道域名（frp / cpolar / ngrok 等）——支持 有无子域名 两种
                r"https?://([\w-]+\.)?frp-ski\.com(:\d+)?",
                r"https?://([\w-]+\.)?cpolar\.cn(:\d+)?",
                r"https?://([\w-]+\.)?cpolar\.io(:\d+)?",
                r"https?://([\w-]+\.)?frp\.com(:\d+)?",
                r"https?://([\w-]+\.)?natfrp\.com(:\d+)?",
                r"https?://([\w-]+\.)?ngrok-free\.app(:\d+)?",
                r"https?://([\w-]+\.)?ngrok\.io(:\d+)?",
                r"https?://([\w-]+\.)?vip\.cpolar\.cn(:\d+)?",
            ],
            "supports_credentials": True,
        }},
    )

    server_session.init_app(app)

    redis_client = redis_lib.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        password=app.config["REDIS_PASSWORD"],
        db=app.config["REDIS_DB"],
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
    )

    try:
        redis_client.ping()
        from loguru import logger
        logger.success(
            f"[Extensions] Redis 连接成功: {app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}"
        )
    except Exception as e:
        from loguru import logger
        logger.warning(f"[Extensions] Redis 连接失败: {e}（V0.1 不阻塞启动）")
