"""工具层单元测试"""
import os

os.environ["FLASK_ENV"] = "testing"
os.environ["AES_KEY_BASE64"] = "bYC2PMEfG3xdlnu1voXnyc1UkeLGPK6PuN7EvIslHng="

import pytest
from app import create_app
from app.utils import crypto, bcrypt_util, sensitive


@pytest.fixture(scope="module")
def app():
    return create_app("testing")


class TestCrypto:
    def test_encrypt_decrypt(self, app):
        with app.app_context():
            plain = "20250001"
            encrypted = crypto.encrypt(plain)
            assert encrypted != plain
            decrypted = crypto.decrypt(encrypted)
            assert decrypted == plain

    def test_different_cipher_each_time(self, app):
        with app.app_context():
            plain = "test@bjtu.edu.cn"
            e1 = crypto.encrypt(plain)
            e2 = crypto.encrypt(plain)
            assert e1 != e2


class TestBcrypt:
    def test_hash_and_check(self):
        pwd = "Admin123!"
        h = bcrypt_util.hash_password(pwd)
        assert h != pwd
        assert bcrypt_util.check_password(pwd, h)

    def test_wrong_password(self):
        h = bcrypt_util.hash_password("correct")
        assert not bcrypt_util.check_password("wrong", h)


class TestSensitive:
    def test_build_and_check(self):
        sensitive.build_trie(["法轮功", "色情", "毒品"])
        assert sensitive.check("这是一个法轮功组织")
