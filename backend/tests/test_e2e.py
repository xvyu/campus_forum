"""E2E 集成测试：单函数顺序执行，保持 Session"""
import os

os.environ["FLASK_ENV"] = "testing"
os.environ["AES_KEY_BASE64"] = "bYC2PMEfG3xdlnu1voXnyc1UkeLGPK6PuN7EvIslHng="
os.environ["SMTP_ACCOUNTS"] = ""

import json
from app import create_app


def test_e2e_flow():
    """完整用户旅程：注册→登录→发帖→评论→楼中楼→点赞→删除"""
    app = create_app("testing")

    with app.test_client() as c:
        # 1. 健康检查
        r = c.get("/api/health")
        assert r.status_code == 200

        # 2. 板块列表
        r = c.get("/api/boards")
        d = json.loads(r.data)
        assert d["code"] == 0
        assert len(d["data"]) >= 8

        # 3. 图形验证码
        r = c.get("/api/auth/captcha")
        d = json.loads(r.data)
        assert d["code"] == 0
        assert d["data"]["uuid"]
        assert d["data"]["image"].startswith("data:image/png")

        # 4. 注册：无效邮箱拒绝
        r = c.post("/api/auth/register", json={
            "student_id": "TEST001", "email": "test@gmail.com",
            "password": "Test1234", "captcha_uuid": "x", "captcha_answer": "x", "email_code": "000000",
        })
        assert json.loads(r.data)["code"] == 1001

        # 5. 登录：不存在账号
        r = c.post("/api/auth/login", json={"student_id": "NONEXIST", "password": "Test1234"})
        assert json.loads(r.data)["code"] == 1002

        # 6. 登录成功
        r = c.post("/api/auth/login", json={"student_id": "202301", "password": "Test1234"})
        d = json.loads(r.data)
        assert d["code"] == 0, f"登录失败: {d['message']}"

        # 7. 当前用户
        r = c.get("/api/auth/me")
        d = json.loads(r.data)
        assert d["code"] == 0
        assert d["data"]["user_id"] > 0
        assert d["data"]["role"] >= 1

        # 8. 个人中心
        r = c.get("/api/users/me")
        d = json.loads(r.data)
        assert d["code"] == 0
        assert d["data"]["nickname"]
        assert d["data"]["anonymous_name"]

        # 9. 修改昵称
        r = c.put("/api/users/me/nickname", json={"nickname": "E2E测试"})
        assert json.loads(r.data)["code"] == 0
        r = c.get("/api/auth/me")
        assert json.loads(r.data)["data"]["nickname"] == "E2E测试"

        # 10. 刷新马甲
        r = c.get("/api/users/me")
        old_name = json.loads(r.data)["data"]["anonymous_name"]
        r = c.post("/api/users/me/refresh-masquerade")
        d = json.loads(r.data)
        assert d["code"] == 0
        assert d["data"]["anonymous_name"] != old_name
        new_name = d["data"]["anonymous_name"]

        # 11. 发帖
        r = c.post("/api/posts", json={"title": "E2E测试帖", "content": "E2E内容", "board_id": 1})
        d = json.loads(r.data)
        assert d["code"] == 0, f"发帖失败: {d['message']}"
        post_id = d["data"]["post_id"]

        # 12. 帖子列表
        r = c.get("/api/posts")
        d = json.loads(r.data)
        assert d["code"] == 0
        assert len(d["data"]["list"]) > 0

        # 13. 帖子详情
        r = c.get(f"/api/posts/{post_id}")
        d = json.loads(r.data)
        assert d["code"] == 0
        assert "comments" in d["data"]
        assert d["data"]["is_author"] is True
        assert d["data"]["is_admin"] in (True, False)

        # 14. 点赞帖子
        r = c.post(f"/api/posts/{post_id}/like", json={"action": "like"})
        assert json.loads(r.data)["code"] == 0
        r = c.get(f"/api/posts/{post_id}")
        assert json.loads(r.data)["data"]["like_count"] >= 1

        # 15. 评论
        r = c.post("/api/comments", json={"post_id": post_id, "content": "E2E评论"})
        d = json.loads(r.data)
        assert d["code"] == 0, f"评论失败: {d['message']}"
        cid = d["data"]["comment_id"]

        # 16. 点赞评论
        r = c.post(f"/api/comments/{cid}/like", json={"action": "like"})
        assert json.loads(r.data)["code"] == 0

        # 17. 2 楼回复
        r = c.post("/api/comments", json={"post_id": post_id, "content": "2楼测试", "parent_id": cid})
        d = json.loads(r.data)
        assert d["code"] == 0
        rid = d["data"]["comment_id"]

        # 18. 3 楼回复
        r = c.post("/api/comments", json={"post_id": post_id, "content": "3楼测试", "parent_id": rid})
        assert json.loads(r.data)["code"] == 0

        # 19. comment_count = 实际总评论数
        r = c.get(f"/api/posts/{post_id}")
        d = json.loads(r.data)
        total = 0
        def count_nodes(cs):
            nonlocal total
            for c in cs:
                total += 1
                if c.get("replies"): count_nodes(c["replies"])
        count_nodes(d["data"]["comments"])
        assert d["data"]["comment_count"] == total, f"{d['data']['comment_count']} != {total}"

        # 20. 楼中楼应包含 reply_to_name
        r = c.get(f"/api/posts/{post_id}")
        d = json.loads(r.data)
        found = False
        def find_reply_to(cs):
            nonlocal found
            for c in cs:
                if c.get("reply_to_name"): found = True
                if c.get("replies"): find_reply_to(c["replies"])
        find_reply_to(d["data"]["comments"])
        assert found, "楼中楼缺少 reply_to_name"

        # 21. 删除评论
        r = c.delete(f"/api/comments/{cid}")
        assert json.loads(r.data)["code"] == 0

        # 22. 作者删帖
        r = c.delete(f"/api/posts/{post_id}")
        assert json.loads(r.data)["code"] == 0, f"删帖失败"
        r = c.get(f"/api/posts/{post_id}")
        assert json.loads(r.data)["code"] == 1002

        # 23. 登出
        r = c.post("/api/auth/logout")
        assert json.loads(r.data)["code"] == 0
        r = c.get("/api/auth/me")
        assert json.loads(r.data)["code"] == 2001

        print("🎉 E2E 全部 23 步通过")
