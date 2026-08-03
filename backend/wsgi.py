"""WSGI 入口：生产环境用 Gunicorn 启动
用法：gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""
import os
from app import create_app

app = create_app(config_name=os.getenv("FLASK_ENV", "production"))
