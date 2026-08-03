"""评论蓝图：评论 + 楼中楼（3 层）+ 点赞 + 删除"""
from flask import Blueprint, request, session, g
from app.extensions import db, redis_client
from app.errors import success, ParamError, NotFoundError, UnauthorizedError, PermissionDeniedError
from app.models.post import Post, Comment
from app.models.user import User, AnonymousIdMapping
from app.utils import sensitive

comment_bp = Blueprint("comment", __name__)


def _login_required():
    user_id = session.get("user_id") or g.get("user_id")
    if not user_id:
        raise UnauthorizedError()
    return user_id


def _build_comments_tree(post_id: int, comment_user: AnonymousIdMapping, is_post_author: bool, viewer_id: int, viewer_role: int) -> list:
    """构建评论树（无限层级）"""
    # 加载所有该帖评论（不只顶层）
    all_post_comments = Comment.query.filter_by(
        post_id=post_id, is_deleted=0
    ).order_by(Comment.id.asc()).all()

    def to_dict(c: Comment) -> dict:
        author = comment_user.query.get(c.anonymous_id)
        return {
            "id": c.id,
            "content": c.content,
            "anonymous_name": author.anonymous_name if author else "匿名",
            "user_id": c.user_id,
            "like_count": c.like_count,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
            "is_author": c.user_id == viewer_id,
            "is_admin": viewer_role == 3,
            "is_post_author": c.user_id == is_post_author,
            "reply_to_name": getattr(c, "_reply_to_name", None),
            "reply_to_id": c.reply_to_user_id,
            "parent_id": c.parent_id,
            "replies": [],
        }

    def _preload_reply_to_names(all_comments: list) -> None:
        """预计算每条评论的 _reply_to_name：取父评论当时用的马甲（不是当前默认马甲）"""
        comment_map = {c.id: c for c in all_comments}
        for c in all_comments:
            if c.parent_id and c.reply_to_user_id:
                parent = comment_map.get(c.parent_id)
                if parent:
                    # 父评论记录里 anonymous_id 就是该用户当时用的马甲
                    parent_anon = comment_user.query.get(parent.anonymous_id)
                    c._reply_to_name = parent_anon.anonymous_name if parent_anon else None
                else:
                    c._reply_to_name = None
            else:
                c._reply_to_name = None

    # 2. 预计算 reply_to_name（用父评论当时用的马甲）
    _preload_reply_to_names(all_post_comments)

    # 3. 顶层评论 + 递归构造子树
    def to_dict_with_reply(c: Comment) -> dict:
        d = to_dict(c)
        d["reply_to_name"] = getattr(c, "_reply_to_name", None)
        return d

    def attach_all(node_data: dict) -> None:
        """把直接子评论全部附加（不区分父评论层级，所有子评论都列在主评论下）"""
        for child in all_post_comments:
            if child.parent_id == node_data["id"]:
                if any(r['id'] == child.id for r in node_data.get('replies', [])):
                    continue
                d = to_dict_with_reply(child)
                d["replies"] = []
                node_data["replies"].append(d)
                # 递归附加子评论的子评论
                attach_all(d)

    result = []
    for top in all_post_comments:
        if top.parent_id is None:
            d = to_dict_with_reply(top)
            d["replies"] = []
            result.append(d)
            attach_all(d)

    return result


@comment_bp.route("/", methods=["GET"])
def index():
    return success(data={"module": "comment", "status": "ok"}, message="comment blueprint ok")


@comment_bp.route("", methods=["POST"])
def create_comment():
    """发表评论/回复"""
    user_id = _login_required()
    data = request.get_json(silent=True) or {}
    post_id = data.get("post_id")
    content = (data.get("content") or "").strip()
    parent_id = data.get("parent_id")
    reply_to_user_id = data.get("reply_to_user_id")

    if not all([post_id, content]):
        raise ParamError("缺少参数（post_id/content）")
    if len(content) > 1000:
        raise ParamError("评论不超过 1000 字")

    post = Post.query.filter_by(id=post_id, is_deleted=0).first()
    if not post:
        raise NotFoundError("帖子不存在")

    # 不限制评论层数：任意楼层都能继续回复
    if parent_id:
        parent = Comment.query.get(parent_id)
        if not parent or parent.is_deleted:
            raise NotFoundError("父评论不存在")
        # 自动取父评论的作者作为 reply_to_user_id
        if not reply_to_user_id:
            reply_to_user_id = parent.user_id

    sensitive.check_or_raise(content)

    anon = AnonymousIdMapping.query.filter_by(
        user_id=user_id, is_default=1, is_active=1
    ).first()
    if not anon:
        raise ParamError("无可用匿名身份")

    comment = Comment(
        school_id=1, post_id=post_id, user_id=user_id,
        anonymous_id=anon.id, parent_id=parent_id,
        reply_to_user_id=reply_to_user_id,
        content=content, ip=request.remote_addr or "",
    )
    db.session.add(comment)
    # 所有评论（含楼中楼）都计入帖子的 comment_count
    Post.query.filter_by(id=post_id).update({
        Post.comment_count: Post.comment_count + 1,
        Post.last_comment_at: db.func.current_timestamp(),
    })
    # 同步维护用户维度的评论数（持久化字段，避免每次实时 count）
    User.query.filter_by(id=user_id).update({
        User.comment_count: User.comment_count + 1,
    })
    if parent_id:
        Comment.query.filter_by(id=parent_id).update({Comment.reply_count: Comment.reply_count + 1})
    db.session.commit()

    return success(data={
        "comment_id": comment.id,
        "user_id": user_id,
        "anonymous_name": anon.anonymous_name,
        "parent_id": parent_id,
        "reply_to_user_id": reply_to_user_id,
        "reply_to_name": AnonymousIdMapping.query.get(
            Comment.query.get(parent_id).anonymous_id
        ).anonymous_name if parent_id and Comment.query.get(parent_id) else None,
        "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
    }, message="评论成功")


@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    """删除评论：评论作者 + 帖子作者 + 管理员"""
    user_id = _login_required()
    role = session.get("role", 1)

    comment = Comment.query.get(comment_id)
    if not comment or comment.is_deleted:
        raise NotFoundError("评论不存在")

    post = Post.query.filter_by(id=comment.post_id).first()
    post_author_id = post.user_id if post else 0

    is_comment_author = comment.user_id == user_id
    is_post_author = post_author_id == user_id
    is_admin = role == 3
    if not (is_comment_author or is_post_author or is_admin):
        raise PermissionDeniedError("无权删除该评论")

    # 级联删除所有未删除的子评论（孤儿清理 + 计数修正）
    # 收集整个子树
    to_delete_ids = [comment_id]
    queue = [comment_id]
    while queue:
        parent = queue.pop()
        children = Comment.query.filter_by(
            post_id=comment.post_id, parent_id=parent, is_deleted=0
        ).all()
        for child in children:
            to_delete_ids.append(child.id)
            queue.append(child.id)

    # 软删除整条子树
    db.session.query(Comment).filter(Comment.id.in_(to_delete_ids)).update(
        {Comment.is_deleted: 1, Comment.status: 0}, synchronize_session=False
    )
    # 帖子评论数 = 子树节点总数
    Post.query.filter_by(id=comment.post_id).update(
        {Post.comment_count: Post.comment_count - len(to_delete_ids)}
    )
    # 用户维度评论数（按 user_id 分组减 1）
    affected_user_ids = db.session.query(Comment.user_id).filter(
        Comment.id.in_(to_delete_ids)
    ).distinct().all()
    for (uid,) in affected_user_ids:
        User.query.filter_by(id=uid).update({User.comment_count: User.comment_count - 1})

    if comment.parent_id:
        Comment.query.filter_by(id=comment.parent_id).update({Comment.reply_count: Comment.reply_count - 1})
    db.session.commit()
    return success(message=f"评论已删除（连带删除 {len(to_delete_ids) - 1} 条子评论）")


@comment_bp.route("/<int:comment_id>/like", methods=["POST"])
def like_comment(comment_id):
    """评论点赞 / 取消"""
    user_id = _login_required()
    data = request.get_json(silent=True) or {}
    action = data.get("action", "like")  # like / cancel

    comment = Comment.query.filter_by(id=comment_id, is_deleted=0).first()
    if not comment:
        raise NotFoundError("评论不存在")

    key = f"comment_like:{user_id}:{comment_id}"
    current = redis_client.get(key)

    if action == "cancel":
        if current == "1":
            Comment.query.filter_by(id=comment_id).update({Comment.like_count: Comment.like_count - 1})
            # 取消到 0 才 -1
            if comment.like_count - 1 == 0:
                User.query.filter_by(id=comment.user_id).update({User.liked_comment_count: User.liked_comment_count - 1})
        redis_client.delete(key)
    else:  # like
        if current != "1":
            Comment.query.filter_by(id=comment_id).update({Comment.like_count: Comment.like_count + 1})
            # 从 0 变为 1：+1
            if comment.like_count == 0:
                User.query.filter_by(id=comment.user_id).update({User.liked_comment_count: User.liked_comment_count + 1})
        redis_client.setex(key, 86400, "1")
    db.session.commit()
    return success(message="已点赞" if action == "like" else "已取消点赞")
