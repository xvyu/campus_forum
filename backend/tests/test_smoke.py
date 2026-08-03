"""烟雾测试：验证健康检查 + 蓝图注册 + 错误格式统一"""
import json


def test_health_check(client):
    """/api/health 返回 200 + MySQL/Redis 状态"""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["code"] == 0
    assert data["message"] == "服务运行正常"
    assert "version" in data["data"]
    assert "time" in data["data"]
    assert "mysql" in data["data"]
    assert "redis" in data["data"]


def test_version_info(client):
    """/api/version 返回 V0.1 信息"""
    response = client.get("/api/version")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["code"] == 0
    assert data["data"]["version"] == "0.1.0"
    assert data["data"]["stage"] == "V0.1 (MVP)"


def test_blueprints_registered(app):
    """7 个蓝图全部注册"""
    blueprint_names = set(app.blueprints.keys())
    expected = {
        "common",
        "auth",
        "post",
        "comment",
        "board",
        "user",
        "notification",
    }
    assert expected.issubset(blueprint_names), (
        f"缺少蓝图: {expected - blueprint_names}"
    )


def test_error_format_404(client):
    """404 错误返回统一格式 code=1002"""
    response = client.get("/api/nonexistent")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["code"] == 1002
    assert "message" in data
    assert "data" in data


def test_error_format_405(client):
    """405 错误返回统一格式 code=1003"""
    response = client.post("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["code"] == 1003


def test_all_blueprint_index_endpoints(client):
    """6 个业务蓝图根路径返回 ok"""
    blueprint_paths = [
        "/api/auth/",
        "/api/posts/",
        "/api/comments/",
        "/api/boards/",
        "/api/users/",
        "/api/notifications/",
    ]
    for path in blueprint_paths:
        response = client.get(path)
        assert response.status_code == 200, f"路径 {path} 失败"
        data = json.loads(response.data)
        assert data["code"] == 0, f"路径 {path} 返回 code={data['code']}"
        assert data["message"].endswith("ok"), f"路径 {path} message 不正确"
