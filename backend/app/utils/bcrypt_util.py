"""bcrypt 密码哈希与验证（cost=12）"""
import bcrypt

COST = 12


def hash_password(password: str) -> str:
    """返回密码哈希字符串"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=COST)).decode("ascii")


def check_password(password: str, password_hash: str) -> bool:
    """验证密码是否匹配"""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
