"""AES-256-GCM 加密解密：用于学号/邮箱字段存储"""
import os
import base64
from flask import current_app
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key() -> bytes:
    """从配置获取 AES 密钥（32 字节 base64 解码）"""
    key_b64 = current_app.config.get("AES_KEY_BASE64", "")
    if not key_b64:
        raise ValueError("AES_KEY_BASE64 未配置")
    return base64.b64decode(key_b64)


def encrypt(plaintext: str) -> str:
    """AES-256-GCM 加密，返回 base64(nonce+ciphertext+tag)"""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt(cipher_b64: str) -> str:
    """解密 base64(nonce+ciphertext+tag) 为明文"""
    key = _get_key()
    data = base64.b64decode(cipher_b64)
    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
