"""用户与匿名身份模型"""
from app.extensions import db


class School(db.Model):
    __tablename__ = "pf_schools"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    code = db.Column(db.String(32), nullable=False, default="")
    name = db.Column(db.String(64), nullable=False, default="")
    email_suffix = db.Column(db.String(64), nullable=False, default="")
    status = db.Column(db.Integer, nullable=False, default=1)


class User(db.Model):
    __tablename__ = "pf_users"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    school_id = db.Column(db.BigInteger, nullable=False, default=1)
    student_id = db.Column(db.String(128), nullable=False, default="")
    email = db.Column(db.String(255), nullable=False, default="")
    password_hash = db.Column(db.String(255), nullable=False, default="")
    nickname = db.Column(db.String(64), nullable=False, default="")
    role = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Integer, nullable=False, default=1)
    # 用户维度评论数（持久化字段），由 comment.py 在 create/delete 时维护
    comment_count = db.Column(db.Integer, nullable=False, default=0)
    # 收到的点赞（按对象拆开记录）：被点赞的帖子数 / 被点赞的评论数
    # 由 post.py / comment.py 在 like / cancel 时维护
    liked_post_count = db.Column(db.Integer, nullable=False, default=0)
    liked_comment_count = db.Column(db.Integer, nullable=False, default=0)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())


class AnonymousIdMapping(db.Model):
    __tablename__ = "pf_anonymous_id_mapping"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    school_id = db.Column(db.BigInteger, nullable=False, default=1)
    anonymous_name = db.Column(db.String(64), nullable=False, default="")
    is_default = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())

class Favorite(db.Model):
    __tablename__ = "pf_favorites"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False, index=True)
    school_id = db.Column(db.BigInteger, nullable=False, default=1)
    post_id = db.Column(db.BigInteger, nullable=False, index=True)
    folder_id = db.Column(db.BigInteger, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())
