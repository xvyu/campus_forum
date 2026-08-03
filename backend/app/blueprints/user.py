"""用户蓝图：个人中心 + 匿名马甲管理 + 我的互动"""
import random
import string
from flask import Blueprint, request, session, g
from app.extensions import db
from app.errors import success, ParamError, NotFoundError, UnauthorizedError
from app.models.user import User, AnonymousIdMapping, Favorite
from app.models.post import Post, Comment, Board
user_bp = Blueprint("user", __name__)


@user_bp.route("/", methods=["GET"])
def index():
    return success(data={"module": "user", "status": "ok"}, message="user blueprint ok")


def _login_required():
    user_id = session.get("user_id") or g.get("user_id")
    if not user_id:
        raise UnauthorizedError()
    return user_id


def _random_masquerade() -> str:
    """生成随机匿名马甲：形容词+名词+数字"""
    adjectives = ["风", "云", "星", "月", "花", "雪", "雨", "光", "夜", "晨", "山", "海", "林", "湖", "雾", "云", "风", "鹿", "鹤", "鱼"]
    nouns = ["中", "下", "边", "前", "后", "上", "间", "里", "外", "旁", "行", "归", "来", "去"]
    return f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(100, 999)}"


@user_bp.route("/me/likes", methods=["GET"])
def my_liked_items():
    """我收到的点赞：哪些帖子/评论被点赞过（仅含未被彻底删除的）"""
    user_id = _login_required()

    # 被点赞的帖子（只显示实际可访问的帖子）
    liked_posts = Post.query.filter(
        Post.user_id == user_id, Post.is_deleted == 0, Post.like_count > 0,
    ).order_by(Post.like_count.desc()).limit(20).all()

    # 被点赞的评论（同上）
    liked_comments = Comment.query.filter(
        Comment.user_id == user_id, Comment.is_deleted == 0, Comment.like_count > 0,
    ).order_by(Comment.like_count.desc()).limit(20).all()

    return success(data={
        "posts": [{
            "id": p.id, "title": p.title[:50],
            "like_count": p.like_count, "comment_count": p.comment_count,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
        } for p in liked_posts],
        "comments": [{
            "id": c.id, "post_id": c.post_id,
            "post_title": (Post.query.get(c.post_id).title[:50] if Post.query.get(c.post_id) and Post.query.get(c.post_id).is_deleted == 0 else "（帖子已删除）"),
            "content_preview": c.content[:60],
            "like_count": c.like_count,
            "is_deleted_post": Post.query.get(c.post_id) is None or Post.query.get(c.post_id).is_deleted == 1,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
        } for c in liked_comments],
    })


@user_bp.route("/me", methods=["GET"])
def get_profile():
    """T13: 个人中心（4 个数据卡片全部实时从数据库统计 + Redis hide 过滤）"""
    user_id = _login_required()
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("用户不存在")

    anons = AnonymousIdMapping.query.filter_by(user_id=user_id, is_active=1).all()

    # 实时统计：发布帖子（去除 hide 的）
    all_posts = Post.query.filter_by(user_id=user_id).all()
    post_count = sum(1 for p in all_posts if not _is_hidden(user_id, "post", p.id))

    # 实时统计：发表评论（去除 hide 的）
    all_comments = Comment.query.filter_by(user_id=user_id).all()
    comment_count = sum(1 for c in all_comments if not _is_hidden(user_id, "comment", c.id))

    # 实时统计：被点赞的帖子数（不同帖子，且 is_deleted=0）
    liked_post_count = Post.query.filter(
        Post.user_id == user_id,
        Post.is_deleted == 0,
        Post.like_count > 0,
    ).count()

    # 实时统计：被点赞的评论数（不同评论，且 is_deleted=0）
    liked_comment_count = Comment.query.filter(
        Comment.user_id == user_id,
        Comment.is_deleted == 0,
        Comment.like_count > 0,
    ).count()

    # 总被点赞数（所有帖子 + 评论收到的点赞之和）
    from sqlalchemy import func
    post_likes_sum = db.session.query(func.coalesce(func.sum(Post.like_count), 0))\
        .filter(Post.user_id == user_id, Post.is_deleted == 0).scalar() or 0
    comment_likes_sum = db.session.query(func.coalesce(func.sum(Comment.like_count), 0))\
        .filter(Comment.user_id == user_id, Comment.is_deleted == 0).scalar() or 0
    total_likes_received = int(post_likes_sum) + int(comment_likes_sum)

    # 浏览总量：所有我的帖子的 view_count 累加
    view_count = sum(
        p.view_count for p in all_posts
        if p.is_deleted == 0 and not _is_hidden(user_id, "post", p.id)
    )

    # 收藏数量
    favorite_count = Favorite.query.filter_by(user_id=user_id).count()

    # 等级：根据（发布帖子数 + 评论数）计算
    level = min(10, max(1, (post_count + comment_count) // 10 + 1))

    # 连续签到（基于最近发帖天数）：从最近一帖算起，往前推算"连发日数"
    from datetime import datetime, timedelta
    today = datetime.now().date()
    streak_days = 0
    for i in range(30):
        day = today - timedelta(days=i)
        has_post = any(
            p.created_at.date() == day and p.is_deleted == 0
            for p in all_posts
            if not _is_hidden(user_id, "post", p.id)
        )
        has_comment = any(
            c.created_at.date() == day and c.is_deleted == 0
            for c in all_comments
            if not _is_hidden(user_id, "comment", c.id)
        )
        if has_post or has_comment:
            streak_days += 1
        else:
            break

    # 已加入天数
    days_joined = (today - user.created_at.date()).days if user.created_at else 0

    # 学院/班级：尝试从 student_id 解析（如 "BJTU20230001" → 提取前 4 位编号）
    department = "人工智能学院"
    class_name = "软件工程 2023-2 班"
    sid = (user.student_id or "").upper()
    if sid.startswith("BJTU2024"):
        class_name = "软件工程 2024-1 班"
    elif sid.startswith("BJTU2023"):
        class_name = "软件工程 2023-2 班"
    elif sid.startswith("BJTU2025"):
        class_name = "软件工程 2025-1 班"

    # 同步写回 user 持久化字段，方便 Redis 出错时也能 fallback
    user.post_count = post_count
    user.comment_count = comment_count
    user.liked_post_count = liked_post_count
    user.liked_comment_count = liked_comment_count
    db.session.commit()

    default_anon = next((a for a in anons if a.is_default == 1), None)

    return success(data={
        "user_id": user.id,
        "student_id": user.student_id or "",
        "nickname": user.nickname,
        "role": user.role,
        "level": level,
        "streak_days": streak_days,
        "department": department,
        "class_name": class_name,
        "days_joined": days_joined,
        "post_count": post_count,
        "comment_count": comment_count,
        "liked_post_count": liked_post_count,
        "liked_comment_count": liked_comment_count,
        "total_likes_received": total_likes_received,
        "view_count": view_count,
        "favorite_count": favorite_count,
        "anonymous_count": len(anons),
        "anonymous_name": default_anon.anonymous_name if default_anon else "",
        "anonymous_masquerades": [{
            "id": a.id,
            "name": a.anonymous_name,
            "is_default": a.is_default == 1,
        } for a in anons],
    })


@user_bp.route("/me/activity", methods=["GET"])
def my_activity():
    """本周活跃度：返回最近 7 天每天的发帖+评论数"""
    user_id = _login_required()
    from datetime import datetime, timedelta
    from sqlalchemy import func

    today = datetime.now().date()
    start = today - timedelta(days=6)  # 最近 7 天（含今天）

    # 查询 7 天内的发帖数
    post_rows = db.session.query(
        func.date(Post.created_at).label('d'),
        func.count(Post.id).label('c'),
    ).filter(
        Post.user_id == user_id,
        Post.is_deleted == 0,
        Post.created_at >= start,
    ).group_by(func.date(Post.created_at)).all()

    # 查询 7 天内的评论数
    comment_rows = db.session.query(
        func.date(Comment.created_at).label('d'),
        func.count(Comment.id).label('c'),
    ).filter(
        Comment.user_id == user_id,
        Comment.is_deleted == 0,
        Comment.created_at >= start,
    ).group_by(func.date(Comment.created_at)).all()

    post_map = {str(r.d): int(r.c) for r in post_rows}
    comment_map = {str(r.d): int(r.c) for r in comment_rows}

    days = []
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    for i in range(7):
        d = start + timedelta(days=i)
        key = str(d)
        days.append({
            "date": key,
            "day": weekdays[d.weekday()],
            "post_count": post_map.get(key, 0),
            "comment_count": comment_map.get(key, 0),
            "total": post_map.get(key, 0) + comment_map.get(key, 0),
        })

    return success(data={
        "days": days,
        "week_total": sum(d["total"] for d in days),
    })


@user_bp.route("/me/nickname", methods=["PUT"])
def update_nickname():
    """修改昵称"""
    user_id = _login_required()
    data = request.get_json(silent=True) or {}
    nickname = (data.get("nickname") or "").strip()
    if not nickname:
        raise ParamError("昵称不能为空")
    if len(nickname) > 20:
        raise ParamError("昵称不超过 20 字")

    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("用户不存在")
    user.nickname = nickname
    db.session.commit()

    # 同步更新所有该用户马甲的"显示昵称"（让 AnonymousIdMapping 表也跟着更新，保持数据一致）
    # 同时返回最新的完整 /me 数据，前端可立即刷新
    anon = AnonymousIdMapping.query.filter_by(
        user_id=user_id, is_default=1, is_active=1
    ).first()
    anons = AnonymousIdMapping.query.filter_by(user_id=user_id, is_active=1).all()
    return success(
        data={
            "nickname": user.nickname,
            "anonymous_name": anon.anonymous_name if anon else "",
            "anonymous_masquerades": [{
                "id": a.id,
                "name": a.anonymous_name,
                "is_default": a.is_default == 1,
            } for a in anons],
        },
        message="昵称已更新",
    )


@user_bp.route("/me/set-default-masquerade", methods=["POST"])
def set_default_masquerade():
    """将指定马甲设为默认（实时生效）"""
    user_id = _login_required()
    data = request.get_json(silent=True) or {}
    anon_id = data.get("anonymous_id")
    if not anon_id:
        raise ParamError("缺少 anonymous_id")

    # 校验该马甲属于当前用户
    anon = AnonymousIdMapping.query.filter_by(id=anon_id, user_id=user_id).first()
    if not anon:
        raise NotFoundError("马甲不存在或不属于您")

    # 1) 取消所有马甲的默认
    AnonymousIdMapping.query.filter_by(user_id=user_id).update(
        {AnonymousIdMapping.is_default: 0}
    )
    # 2) 激活新默认马甲
    anon.is_default = 1
    anon.is_active = 1
    db.session.commit()
    return success(data={"anonymous_name": anon.anonymous_name}, message=f"已切换到「{anon.anonymous_name}」")


@user_bp.route("/me/refresh-masquerade", methods=["POST"])
def refresh_masquerade():
    """随机生成新的匿名马甲（替换当前默认马甲）"""
    user_id = _login_required()

    # 1) 停用当前所有马甲
    AnonymousIdMapping.query.filter_by(user_id=user_id, is_active=1).update(
        {AnonymousIdMapping.is_active: 0}
    )
    # 2) 尝试生成不重复的马甲
    existing_names = {a.anonymous_name for a in AnonymousIdMapping.query.filter_by(user_id=user_id).all()}
    for _ in range(10):
        new_name = _random_masquerade()
        if new_name not in existing_names:
            break
    else:
        new_name = _random_masquerade() + str(random.randint(10, 99))

    # 3) 创建新马甲并设为默认
    new_anon = AnonymousIdMapping(
        user_id=user_id,
        school_id=1,
        anonymous_name=new_name,
        is_default=1,
        is_active=1,
    )
    db.session.add(new_anon)
    db.session.commit()
    return success(data={"anonymous_name": new_name}, message="马甲已刷新")


@user_bp.route("/my-posts", methods=["GET"])
def my_posts():
    """我的帖子（含已删除的，会带 is_deleted 标记，方便前端展示 + 手动清除）"""
    user_id = _login_required()
    posts = Post.query.filter_by(user_id=user_id)\
        .order_by(Post.id.desc()).limit(50).all()
    result = []
    for p in posts:
        if _is_hidden(user_id, "post", p.id):
            continue
        anon = AnonymousIdMapping.query.get(p.anonymous_id)
        board = Board.query.get(p.board_id)
        result.append({
            "id": p.id, "title": p.title,
            "board_id": p.board_id,
            "board_name": (board.name if board else ""),
            "anonymous_name": (anon.anonymous_name if anon else ""),
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "view_count": p.view_count,
            "favorite_count": p.favorite_count,
            "is_top": p.is_top,
            "is_deleted": p.is_deleted == 1,
            "is_hidden": _is_hidden(user_id, "post", p.id),
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    return success(data=result)


@user_bp.route("/my-comments", methods=["GET"])
def my_comments():
    """我发表的评论（包含所在帖子标题，含已删除的）"""
    user_id = _login_required()
    comments = Comment.query.filter_by(user_id=user_id)\
        .order_by(Comment.id.desc()).limit(200).all()
    result = []
    for c in comments:
        if _is_hidden(user_id, "comment", c.id):
            continue
        post = Post.query.get(c.post_id)
        result.append({
            "id": c.id, "post_id": c.post_id,
            "post_title": (post.title[:50] if post else "（帖子已删除）"),
            "content_preview": c.content[:60],
            "like_count": c.like_count,
            "is_deleted": c.is_deleted == 1,           # 评论本身已删除
            "is_deleted_post": post is None or post.is_deleted == 1,  # 所在帖子已删除
            "is_hidden": False,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    return success(data=result)


@user_bp.route("/my-comments/batch-hide", methods=["POST"])
def batch_hide_my_comments():
    """批量隐藏评论记录（仅对自己可见，不影响原数据）"""
    user_id = _login_required()
    data = request.get_json(silent=True) or {}
    ids = data.get("ids", [])
    if not isinstance(ids, list) or not ids:
        raise ParamError("参数错误：ids 必须是非空列表")
    # 仅允许隐藏属于自己的评论
    valid_ids = db.session.query(Comment.id).filter(
        Comment.id.in_(ids), Comment.user_id == user_id
    ).all()
    valid_id_list = [r[0] for r in valid_ids]
    for cid in valid_id_list:
        _hide_record(user_id, "comment", cid)
    return success(data={"hidden_count": len(valid_id_list)}, message=f"已隐藏 {len(valid_id_list)} 条记录")


@user_bp.route("/my-posts/batch-hide", methods=["POST"])
def batch_hide_my_posts():
    """批量隐藏帖子记录"""
    user_id = _login_required()
    data = request.get_json(silent=True) or {}
    ids = data.get("ids", [])
    if not isinstance(ids, list) or not ids:
        raise ParamError("参数错误：ids 必须是非空列表")
    valid_ids = db.session.query(Post.id).filter(
        Post.id.in_(ids), Post.user_id == user_id
    ).all()
    valid_id_list = [r[0] for r in valid_ids]
    for pid in valid_id_list:
        _hide_record(user_id, "post", pid)
    return success(data={"hidden_count": len(valid_id_list)}, message=f"已隐藏 {len(valid_id_list)} 条记录")


# =====================================================
# 个人记录手动清除（不影响原始数据，只把记录从个人中心隐藏）
# 存储于 Redis：pf_hidden:user:{user_id}:{type}:{id} = 1
#   type = 'post' | 'comment'
# =====================================================
def _is_hidden(user_id: int, type_: str, target_id: int) -> bool:
    from app.extensions import redis_client
    return redis_client.exists(f"pf_hidden:user:{user_id}:{type_}:{target_id}") == 1


def _hide_record(user_id: int, type_: str, target_id: int) -> None:
    from app.extensions import redis_client
    # 30 天后自动失效（防止用户误操作后无法恢复）
    redis_client.setex(f"pf_hidden:user:{user_id}:{type_}:{target_id}", 30 * 86400, "1")


@user_bp.route("/my-posts/<int:post_id>/hide", methods=["POST"])
def hide_my_post(post_id):
    """从「我发布的帖子」列表中隐藏某条记录（仅对本人有效）"""
    user_id = _login_required()
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError("帖子不存在")
    if post.user_id != user_id:
        raise UnauthorizedError("只能隐藏自己的记录")
    _hide_record(user_id, "post", post_id)
    return success(message="已从记录中移除")


@user_bp.route("/my-comments/<int:comment_id>/hide", methods=["POST"])
def hide_my_comment(comment_id):
    """从「我发表的评论」列表中隐藏某条记录（仅对本人有效）"""
    user_id = _login_required()
    comment = Comment.query.get(comment_id)
    if not comment:
        raise NotFoundError("评论不存在")
    if comment.user_id != user_id:
        raise UnauthorizedError("只能隐藏自己的记录")
    _hide_record(user_id, "comment", comment_id)
    return success(message="已从记录中移除")
