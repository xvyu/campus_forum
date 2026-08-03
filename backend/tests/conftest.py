"""pytest 公共配置：提供 Flask app / client / runner 三个 fixture"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """测试用 Flask app（testing 配置）"""
    os.environ["FLASK_ENV"] = "testing"
    from app import create_app

    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["DB_NAME"] = "campus_forum_test"
    return app


@pytest.fixture
def client(app):
    """Flask test_client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner"""
    return app.test_cli_runner()
