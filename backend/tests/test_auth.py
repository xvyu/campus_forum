"""auth 蓝图集成测试（T06-T08）"""
import os

os.environ["FLASK_ENV"] = "testing"
os.environ["AES_KEY_BASE64"] = "bYC2PMEfG3xdlnu1voXnyc1UkeLGPK6PuN7EvIslHng="

import json
import pytest
from app import create_app

# 测试用的图形验证码 uuid 和答案（手动构造）
TEST_CAPTCHA_UUID = "test_captcha_001"
TEST_CAPTCHA_ANSWER = "ABCD"


@pytest.fixture(scope="module")
def app():
    return create_app("testing")


@pytest.fixture(autouse=True)
def setup_captcha(app):
    """每个测试前注入测试验证码"""
    with app.app_context():
        from app.extensions import redis_client
        redis_client.setex(f"captcha:{TEST_CAPTCHA_UUID}", 180, TEST_CAPTCHA_ANSWER)
    yield
    with app.app_context():
        from app.extensions import redis_client
        redis_client.delete(f"captcha:{TEST_CAPTCHA_UUID}")


class TestCaptcha:
    """T06: 图形验证码"""

    def test_get_captcha_returns_image(self, client):
        resp = client.get("/api/auth/captcha")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["code"] == 0
        assert "uuid" in data["data"]
        assert "image" in data["data"]
        assert data["data"]["image"].startswith("data:image/png")

    def test_send_code_missing_email(self, client):
        resp = client.post("/api/auth/send-code", json={})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["code"] == 1001


class TestRegister:
    """T07: 注册"""

    def test_register_missing_params(self, client):
        resp = client.post("/api/auth/register", json={})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["code"] == 1001

    def test_register_invalid_email(self, client):
        resp = client.post("/api/auth/register", json={
            "student_id": "20260001",
            "email": "test@gmail.com",
            "password": "Test123!",
            "captcha_uuid": TEST_CAPTCHA_UUID,
            "captcha_answer": TEST_CAPTCHA_ANSWER,
            "email_code": "654321",
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["code"] == 1001


class TestLogin:
    """T08: 登录"""

    def test_login_missing_params(self, client):
        resp = client.post("/api/auth/login", json={})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["code"] == 1001

    def test_logout_without_login(self, client):
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["code"] == 0

    def test_me_without_login(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["code"] == 2001
