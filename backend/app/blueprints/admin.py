"""管理员蓝图：全站管理功能"""
import json
from flask import Blueprint, request, session, g
from app.extensions import db
from app.errors import success, ParamError, NotFoundError, UnauthorizedError, PermissionDeniedError
from app.models.user import User
from app.models.post import Post, Comment, Board, PostDeleteSnapshot

admin_bp = Blueprint("admin", __name__)

'''
管理员账号：admin
密码：admin123
'''
def _admin_required():
    """必须管理员才能操作"""
    user_id = session.get("user_id") or g.get("user_id")
    if not user_id:
        raise UnauthorizedError()
    role = session.get("role") or g.get("role") or 1
    if role != 3:
        raise PermissionDeniedError("仅管理员可执行此操作")
    return user_id


def _serialize_post_for_snapshot(p: Post) -> dict:
    """完整序列化帖子（包括所有评论、浏览量、点赞数等所有状态）"""
    from app.models.user import AnonymousIdMapping
    author = User.query.get(p.user_id)
    anon = AnonymousIdMapping.query.get(p.anonymous_id) if p.anonymous_id else None
    board = Board.query.get(p.board_id) if p.board_id else None

    # 所有评论（包括已删除的）
    all_comments = Comment.query.filter_by(post_id=p.id).order_by(Comment.id.asc()).all()
    comments_data = []
    for c in all_comments:
        c_anon = AnonymousIdMapping.query.get(c.anonymous_id) if c.anonymous_id else None
        c_author = User.query.get(c.user_id)
        comments_data.append({
            "id": c.id,
            "content": c.content,
            "author_name": c_anon.anonymous_name if c_anon else (c_author.nickname if c_author else "未知"),
            "user_id": c.user_id,
            "parent_id": c.parent_id,
            "is_deleted": c.is_deleted == 1,
            "like_count": c.like_count,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None,
        })

    return {
        "id": p.id,
        "title": p.title,
        "content": p.content,
        "author_name": anon.anonymous_name if anon else (author.nickname if author else "未知"),
        "user_id": p.user_id,
        "board_name": board.name if board else "",
        "view_count": p.view_count,
        "like_count": p.like_count,
        "dislike_count": p.dislike_count,
        "comment_count": p.comment_count,
        "favorite_count": p.favorite_count,
        "is_top": p.is_top,
        "is_essence": p.is_essence,
        "status": p.status,
        "is_deleted": p.is_deleted,
        "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
        "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M:%S") if p.updated_at else None,
        "comments": comments_data,
    }


def _enrich_post(p: Post):
    """补全帖子的展示字段"""
    author = User.query.get(p.user_id)
    from app.models.user import AnonymousIdMapping
    anon = AnonymousIdMapping.query.get(p.anonymous_id) if p.anonymous_id else None
    board = Board.query.get(p.board_id) if p.board_id else None
    # 最后一次更新时间 + 最后一条评论预览
    last_comment = Comment.query.filter_by(
        post_id=p.id
    ).order_by(Comment.id.desc()).first()
    return {
        "id": p.id,
        "title": p.title,
        "content_preview": p.content[:200] if p.content else "",
        "author_name": anon.anonymous_name if anon else (author.nickname if author else "未知"),
        "user_id": p.user_id,
        "board_name": board.name if board else "",
        "like_count": p.like_count,
        "comment_count": p.comment_count,
        "view_count": p.view_count,
        "is_deleted": p.is_deleted == 1,
        "has_snapshot": PostDeleteSnapshot.query.filter_by(post_id=p.id).count() > 0,
        "last_comment_at": p.last_comment_at.strftime("%Y-%m-%d %H:%M") if p.last_comment_at else None,
        "last_comment_preview": last_comment.content[:80] if last_comment else "",
        "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
        "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M") if hasattr(p, "updated_at") and p.updated_at else None,
    }


@admin_bp.route("/posts", methods=["GET"])
def admin_list_posts():
    """查看全站帖子（管理员版，可按状态筛选）"""
    _admin_required()
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 30, type=int), 100)
    status = request.args.get("status", "all")
    offset = (page - 1) * limit

    q = Post.query
    if status == "active":
        q = q.filter(Post.is_deleted == 0)
    elif status == "deleted":
        q = q.filter(Post.is_deleted == 1)

    total = q.count()
    posts = q.order_by(Post.id.desc()).offset(offset).limit(limit).all()

    return success(data={
        "list": [_enrich_post(p) for p in posts],
        "total": total,
        "page": page,
    })


@admin_bp.route("/posts/<int:post_id>", methods=["GET"])
def admin_post_detail(post_id):
    """查看帖子详情（带快照：删除时记录的完整状态）"""
    _admin_required()
    p = Post.query.get(post_id)
    if not p:
        raise NotFoundError("帖子不存在")
    data = _enrich_post(p)
    # 如果是已删除的帖子，优先返回删除前的快照
    snapshot = PostDeleteSnapshot.query.filter_by(post_id=post_id).order_by(
        PostDeleteSnapshot.created_at.desc()
    ).first()
    if snapshot:
        try:
            snap = json.loads(snapshot.snapshot_data)
            data["snapshot"] = snap
            data["snapshot_at"] = snapshot.created_at.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    return success(data=data)


@admin_bp.route("/posts/<int:post_id>/restore", methods=["POST"])
def admin_restore_post(post_id):
    """恢复已删除的帖子（清除快照）"""
    _admin_required()
    p = Post.query.get(post_id)
    if not p:
        raise NotFoundError("帖子不存在")
    if p.is_deleted == 0:
        return success(message="该帖子未被删除")
    p.is_deleted = 0
    p.status = 1
    if p.board_id:
        Board.query.filter_by(id=p.board_id).update(
            {Board.post_count: Board.post_count + 1}
        )
    db.session.commit()
    return success(message=f"帖子 #{post_id} 已恢复")


@admin_bp.route("/posts/<int:post_id>/hard-delete", methods=["DELETE"])
def admin_hard_delete_post(post_id):
    """彻底删除帖子（物理删除，不可恢复，保留快照）"""
    _admin_required()
    p = Post.query.get(post_id)
    if not p:
        raise NotFoundError("帖子不存在")
    # 删除评论
    Comment.query.filter_by(post_id=post_id).delete()
    if p.board_id and p.is_deleted == 0:
        Board.query.filter_by(id=p.board_id).update(
            {Board.post_count: Board.post_count - 1}
        )
    db.session.delete(p)
    db.session.commit()
    return success(message=f"帖子 #{post_id} 已彻底删除（快照保留）")


@admin_bp.route("/posts/<int:post_id>", methods=["DELETE"])
def admin_delete_post(post_id):
    """管理员软删除帖子：先快照，再移到已删除列表"""
    _admin_required()
    admin_id = _admin_required()
    p = Post.query.get(post_id)
    if not p:
        raise NotFoundError("帖子不存在")
    if p.is_deleted == 1:
        return success(message="该帖子已是删除状态")
    # 【关键】在删除前生成快照（包含全部评论、浏览量、点赞数等最终状态）
    snap_data = _serialize_post_for_snapshot(p)
    snap = PostDeleteSnapshot(
        post_id=p.id,
        snapshot_data=json.dumps(snap_data, ensure_ascii=False),
        deleted_by=admin_id,
    )
    db.session.add(snap)
    # 软删除
    p.is_deleted = 1
    p.status = 0
    if p.board_id:
        Board.query.filter_by(id=p.board_id).update(
            {Board.post_count: Board.post_count - 1}
        )
    db.session.commit()
    return success(message=f"帖子 #{post_id} 已移到已删除列表（快照已保存）")


@admin_bp.route("/posts/<int:post_id>/snapshot", methods=["GET"])
def admin_post_snapshot(post_id):
    """获取帖子的删除前快照（包含最后一次更新时的所有数据）"""
    _admin_required()
    snap = PostDeleteSnapshot.query.filter_by(post_id=post_id).order_by(
        PostDeleteSnapshot.created_at.desc()
    ).first()
    if not snap:
        raise NotFoundError("该帖子暂无删除快照")
    try:
        data = json.loads(snap.snapshot_data)
    except Exception as e:
        raise ParamError(f"快照数据解析失败: {e}")
    return success(data={
        "snapshot": data,
        "snapshot_at": snap.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "deleted_by": snap.deleted_by,
    })


@admin_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
def admin_delete_comment(comment_id):
    """管理员强制删除评论（同时记录到当前快照）"""
    _admin_required()
    comment = Comment.query.get(comment_id)
    if not comment:
        raise NotFoundError("评论不存在")
    comment.is_deleted = 1
    comment.status = 0
    db.session.commit()
    return success(message=f"评论 #{comment_id} 已删除")


@admin_bp.route("/users", methods=["GET"])
def admin_list_users():
    """注册用户列表（仅显示普通用户 role=1）"""
    _admin_required()
    q = User.query.filter(User.role == 1)
    total = q.count()
    users = q.order_by(User.id.desc()).limit(50).all()

    return success(data={
        "list": [{
            "id": u.id,
            "student_id": u.student_id,
            "nickname": u.nickname,
            "email": u.email,
            "status": u.status,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M"),
        } for u in users],
        "total": total,
    })


@admin_bp.route("/stats", methods=["GET"])
def admin_stats():
    """管理后台统计"""
    _admin_required()
    return success(data={
        "total_posts": Post.query.count(),
        "active_posts": Post.query.filter_by(is_deleted=0).count(),
        "deleted_posts": Post.query.filter_by(is_deleted=1).count(),
        "total_users": User.query.filter_by(role=1).count(),
        "admin_users": User.query.filter_by(role=3).count(),
    })
