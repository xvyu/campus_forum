"""Token 认证工具：生成/验证/吊销 token，代替 session-cookie"""
import secrets
from app.extensions import redis_client as _default_redis_client

TOKEN_PREFIX = "auth_token:"
TOKEN_TTL = 7 * 86400  # 7 天


def _redis():
    """延迟获取 redis_client（避免模块导入时还没初始化）"""
    from app.extensions import redis_client
    return redis_client


def generate_token(user_id: int, role: int = 1) -> str:
    """生成随机 token 并存入 Redis"""
    token = secrets.token_urlsafe(48)
    key = f"{TOKEN_PREFIX}{token}"
    r = _redis()
    r.hset(key, mapping={
        "user_id": str(user_id),
        "role": str(role),
    })
    r.expire(key, TOKEN_TTL)
    return token


def verify_token(token: str) -> dict | None:
    """验证 token，返回 {user_id, role} 或 None"""
    key = f"{TOKEN_PREFIX}{token}"
    data = _redis().hgetall(key)
    if not data:
        return None
    return {
        "user_id": int(data.get("user_id", 0)),
        "role": int(data.get("role", 1)),
    }


def revoke_token(token: str) -> None:
    """吊销 token"""
    key = f"{TOKEN_PREFIX}{token}"
    _redis().delete(key)


def parse_auth_header(auth_header) -> dict | None:
    """从 Authorization: Bearer <token> 中提取并验证"""
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    return verify_token(token)
