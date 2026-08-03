"""收藏功能 blueprint"""
from flask import Blueprint, request, session
from sqlalchemy import func

from app.extensions import db
from app.errors import success, ParamError, NotFoundError, UnauthorizedError
from app.models.post import Post
from app.models.user import User, AnonymousIdMapping, Favorite

favorite_bp = Blueprint("favorite", __name__, url_prefix="/api/favorites")


def _login_required() -> int:
    user_id = session.get("user_id")
    if not user_id:
        raise UnauthorizedError()
    return user_id


@favorite_bp.route("/posts/<int:post_id>", methods=["POST"])
def toggle_favorite(post_id: int):
    """收藏/取消收藏帖子"""
    user_id = _login_required()
    post = Post.query.get(post_id)
    if not post or post.is_deleted:
        raise NotFoundError("帖子不存在")

    existing = Favorite.query.filter_by(
        user_id=user_id, post_id=post_id
    ).first()

    if existing:
        db.session.delete(existing)
        post.favorite_count = max(0, (post.favorite_count or 0) - 1)
        db.session.commit()
        return success(data={"favorited": False, "favorite_count": post.favorite_count}, message="取消收藏")
    else:
        favorite = Favorite(
            user_id=user_id, school_id=1, post_id=post_id,
        )
        db.session.add(favorite)
        post.favorite_count = (post.favorite_count or 0) + 1
        db.session.commit()
        return success(data={"favorited": True, "favorite_count": post.favorite_count}, message="收藏成功")


@favorite_bp.route("/posts/<int:post_id>/status", methods=["GET"])
def favorite_status(post_id: int):
    """查询当前用户对某帖子的收藏状态"""
    user_id = session.get("user_id")
    if not user_id:
        return success(data={"favorited": False, "favorite_count": 0})

    post = Post.query.get(post_id)
    if not post:
        return success(data={"favorited": False, "favorite_count": 0})

    existing = Favorite.query.filter_by(user_id=user_id, post_id=post_id).first()
    return success(data={
        "favorited": bool(existing),
        "favorite_count": post.favorite_count or 0,
    })


@favorite_bp.route("/my", methods=["GET"])
def my_favorites():
    """我收藏的帖子列表"""
    user_id = _login_required()
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 50)

    query = (
        db.session.query(Favorite, Post)
        .join(Post, Favorite.post_id == Post.id)
        .filter(Favorite.user_id == user_id, Post.is_deleted == 0, Post.status == 1)
        .order_by(Favorite.created_at.desc())
    )
    total = query.count()
    rows = query.offset((page - 1) * limit).limit(limit).all()

    items = []
    for fav, p in rows:
        anon = AnonymousIdMapping.query.get(p.anonymous_id)
        items.append({
            "favorite_id": fav.id,
            "favorited_at": fav.created_at.strftime("%Y-%m-%d %H:%M") if fav.created_at else None,
            "id": p.id,
            "title": p.title,
            "board_id": p.board_id,
            "anonymous_name": anon.anonymous_name if anon else "匿名",
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "view_count": p.view_count,
            "favorite_count": p.favorite_count,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    return success(data={
        "list": items,
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": page * limit < total,
    })
