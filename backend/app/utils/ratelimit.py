"""Redis 滑动窗口限流"""
from app.extensions import redis_client


def check_rate_limit(key: str, max_requests: int, window_seconds: int = 60) -> bool:
    """检查是否超限，返回 True=允许请求，False=限流"""
    current = redis_client.get(key)
    if current is not None and int(current) >= max_requests:
        return False
    pipe = redis_client.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, window_seconds)
    pipe.execute()
    return True


def get_remain_count(key: str, max_requests: int) -> int:
    """获取剩余可用次数"""
    current = redis_client.get(key)
    if current is None:
        return max_requests
    return max(0, max_requests - int(current))
