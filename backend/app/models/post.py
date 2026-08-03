"""帖子、评论、板块、点赞模型"""
from datetime import datetime
from app.extensions import db


class Board(db.Model):
    __tablename__ = "pf_boards"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    school_id = db.Column(db.BigInteger, nullable=False, default=1)
    slug = db.Column(db.String(32), nullable=False, default="")
    name = db.Column(db.String(32), nullable=False, default="")
    description = db.Column(db.String(255), nullable=False, default="")
    icon = db.Column(db.String(255), nullable=False, default="")
    post_count = db.Column(db.Integer, nullable=False, default=0)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())


class Post(db.Model):
    __tablename__ = "pf_posts"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    school_id = db.Column(db.BigInteger, nullable=False, default=1)
    user_id = db.Column(db.BigInteger, nullable=False)
    board_id = db.Column(db.BigInteger, nullable=False)
    anonymous_id = db.Column(db.BigInteger, nullable=False)
    title = db.Column(db.String(100), nullable=False, default="")
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text, nullable=False, default="")
    view_count = db.Column(db.BigInteger, nullable=False, default=0)
    like_count = db.Column(db.BigInteger, nullable=False, default=0)
    dislike_count = db.Column(db.BigInteger, nullable=False, default=0)
    comment_count = db.Column(db.BigInteger, nullable=False, default=0)
    favorite_count = db.Column(db.BigInteger, nullable=False, default=0)
    report_count = db.Column(db.BigInteger, nullable=False, default=0)
    status = db.Column(db.Integer, nullable=False, default=1)
    is_top = db.Column(db.Integer, nullable=False, default=0)
    is_essence = db.Column(db.Integer, nullable=False, default=0)
    ip = db.Column(db.String(45), nullable=False, default="")
    ip_location = db.Column(db.String(32), nullable=False, default="")
    last_comment_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())


class Comment(db.Model):
    __tablename__ = "pf_comments"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    school_id = db.Column(db.BigInteger, nullable=False, default=1)
    post_id = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.BigInteger, nullable=False)
    anonymous_id = db.Column(db.BigInteger, nullable=False)
    parent_id = db.Column(db.BigInteger, nullable=True)
    reply_to_user_id = db.Column(db.BigInteger, nullable=True)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text, nullable=False, default="")
    like_count = db.Column(db.Integer, nullable=False, default=0)
    reply_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Integer, nullable=False, default=1)
    ip = db.Column(db.String(45), nullable=False, default="")
    ip_location = db.Column(db.String(32), nullable=False, default="")
    is_deleted = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())


class PostDeleteSnapshot(db.Model):
    """帖子删除前快照：记录帖子最后一次更新时的完整状态 + 全部评论"""
    __tablename__ = "pf_post_delete_snapshots"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    post_id = db.Column(db.BigInteger, nullable=False, index=True)
    snapshot_data = db.Column(db.Text, nullable=False)  # JSON 字符串：帖子元数据 + 全量评论
    deleted_by = db.Column(db.BigInteger, nullable=True)  # 哪个用户/admin 删的
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
