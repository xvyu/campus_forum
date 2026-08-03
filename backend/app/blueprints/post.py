"""帖子蓝图：发帖、列表、详情、点赞/点踩/删除"""
import re
from flask import Blueprint, request, session, g
from app.extensions import db, redis_client
from app.errors import success, fail, ParamError, NotFoundError, UnauthorizedError, RateLimitError, DuplicateError, PermissionDeniedError as ForbiddenError
from app.models.user import User, AnonymousIdMapping
from app.models.post import Board, Post, Comment
from app.utils import ratelimit, sensitive

post_bp = Blueprint("post", __name__)


# 剥 HTML 标签 → 纯文本，用于字数校验（避免 base64 图片被算入字符数）
_HTML_TAG_RE = re.compile(r'<[^>]+>')
_WHITESPACE_RE = re.compile(r'\s+')


def _strip_html(s: str) -> str:
    """去掉所有 HTML 标签，返回纯文本"""
    if not s:
        return ''
    s = _HTML_TAG_RE.sub('', s)
    s = s.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    s = _WHITESPACE_RE.sub('', s)
    return s


def _login_required():
    user_id = session.get("user_id") or g.get("user_id")
    if not user_id:
        raise UnauthorizedError()
    return user_id


@post_bp.route("/", methods=["GET"])
def index():
    return success(data={"module": "post", "status": "ok"}, message="post blueprint ok")


@post_bp.route("", methods=["POST"])
def create_post():
    """T09: 发帖"""
    user_id = _login_required()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    board_id = data.get("board_id")
    anonymous_id = data.get("anonymous_id")

    if not all([title, content, board_id]):
        raise ParamError("缺少必填参数（title/content/board_id）")
    if len(title) > 50:
        raise ParamError("标题不超过 50 字")
    # 字数校验：剥离 HTML 标签后算纯文本（图片/文件占位符不计入）
    plain_text = _strip_html(content)
    if len(plain_text) > 5000:
        raise ParamError("正文不超过 5000 字")

    # IP 限流（每分钟 5 帖）
    ip = request.remote_addr or "unknown"
    if not ratelimit.check_rate_limit(f"post_ip:{ip}", 5, 60):
        raise RateLimitError()

    # 敏感词检查
    sensitive.check_or_raise(f"{title} {content}")

    # 匿名身份：未传则用默认马甲
    if not anonymous_id:
        anon = AnonymousIdMapping.query.filter_by(
            user_id=user_id, is_default=1, is_active=1
        ).first()
        if not anon:
            raise ParamError("无可用匿名身份")
        anonymous_id = anon.id

    post = Post(
        school_id=1, user_id=user_id, board_id=board_id,
        anonymous_id=anonymous_id, title=title, content=content,
        ip=ip,
    )
    db.session.add(post)
    db.session.commit()

    # 更新板块帖子数
    Board.query.filter_by(id=board_id).update({Board.post_count: Board.post_count + 1})
    db.session.commit()

    return success(data={"post_id": post.id}, message="发帖成功")


@post_bp.route("", methods=["GET"])
def list_posts():
    """T10: 帖子列表（游标分页 + 按板块筛选 + 标题搜索）"""
    board_id = request.args.get("board_id", type=int)
    cursor = request.args.get("cursor", type=int)
    limit = min(request.args.get("limit", 20, type=int), 50)
    sort = request.args.get("sort", "latest")  # latest / hot / view / time
    kw = (request.args.get("kw") or "").strip()

    query = Post.query.filter(Post.status == 1, Post.is_deleted == 0)
    if board_id:
        query = query.filter(Post.board_id == board_id)
    if kw:
        query = query.filter(Post.title.like(f"%{kw}%"))
    if cursor:
        query = query.filter(Post.id < cursor)

    if sort == "hot":
        query = query.order_by(Post.like_count.desc(), Post.id.desc())
    elif sort == "view":
        # 按浏览量从高到低排序，并附上发布时间作为第二排序键（保证稳定排序）
        query = query.order_by(Post.view_count.desc(), Post.id.desc())
    elif sort == "time":
        # 按发布时间从新到旧排序（Post.id 单调递增）
        query = query.order_by(Post.id.desc())
    else:
        # 默认 latest 与 time 一致
        query = query.order_by(Post.id.desc())

    posts = query.limit(limit + 1).all()
    has_more = len(posts) > limit
    items = posts[:limit]

    result = []
    for p in items:
        anon = AnonymousIdMapping.query.get(p.anonymous_id)
        board = Board.query.get(p.board_id)
        result.append({
            "id": p.id, "board_id": p.board_id,
            "board_name": (board.name if board else ""),
            "title": p.title, "content_preview": p.content[:100],
            "anonymous_name": anon.anonymous_name if anon else "匿名用户",
            "like_count": p.like_count, "comment_count": p.comment_count,
            "view_count": p.view_count, "favorite_count": p.favorite_count,
            "is_top": p.is_top,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    return success(data={
        "list": result,
        "next_cursor": items[-1].id if items and has_more else None,
        "has_more": has_more,
    })


# =====================================================
# 排行榜：浏览榜 / 评论榜
# =====================================================
def _serialize_ranking(post, rank: int, sort_key: str) -> dict:
    """统一排行列表项的格式"""
    anon = AnonymousIdMapping.query.get(post.anonymous_id)
    board = Board.query.get(post.board_id)
    return {
        "rank": rank,
        "id": post.id,
        "title": post.title,
        "anonymous_name": anon.anonymous_name if anon else "匿名用户",
        "board_name": board.name if board else "",
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "view_count": post.view_count,
        "favorite_count": post.favorite_count,
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
    }


@post_bp.route("/ranking", methods=["GET"])
def post_ranking():
    """首页榜单三合一：?board_id=全部/板块id&range=all|week|month&sort=view|comment|time"""
    from datetime import datetime, timedelta
    board_id = request.args.get("board_id", "all")
    range_type = request.args.get("range", "all")  # all / week / month
    sort_type = request.args.get("sort", "view")   # view / comment / time
    limit = min(request.args.get("limit", 10, type=int), 30)

    query = Post.query.filter(Post.status == 1, Post.is_deleted == 0)

    # 板块筛选
    if board_id and board_id != "all":
        try:
            query = query.filter(Post.board_id == int(board_id))
        except (TypeError, ValueError):
            pass

    # 时间范围
    if range_type == "week":
        cutoff = datetime.now() - timedelta(days=7)
        query = query.filter(Post.created_at >= cutoff)
    elif range_type == "month":
        cutoff = datetime.now() - timedelta(days=30)
        query = query.filter(Post.created_at >= cutoff)

    # 排序
    if sort_type == "comment":
        posts = query.order_by(Post.comment_count.desc(), Post.id.desc()).limit(limit).all()
    elif sort_type == "time":
        posts = query.order_by(Post.created_at.desc(), Post.id.desc()).limit(limit).all()
    elif sort_type == "favorite":
        posts = query.order_by(Post.favorite_count.desc(), Post.id.desc()).limit(limit).all()
    else:
        sort_type = "view"
        posts = query.order_by(Post.view_count.desc(), Post.id.desc()).limit(limit).all()

    return success(data={
        "board_id": board_id,
        "range": range_type,
        "sort": sort_type,
        "list": [_serialize_ranking(p, i + 1, sort_type) for i, p in enumerate(posts)],
    })


@post_bp.route("/hot-keywords", methods=["GET"])
def hot_keywords():
    """热门搜索关键词：直接用帖子标题作为热词，按热度排序"""
    from sqlalchemy import func

    # 取所有有效帖子
    posts = Post.query.filter(
        Post.is_deleted == 0,
        Post.status == 1,
    ).all()

    # 1) 按标题分组统计（精确匹配）
    title_groups: dict[str, dict] = {}
    for p in posts:
        title = (p.title or '').strip()
        if not title:
            continue
        if title not in title_groups:
            title_groups[title] = {
                "label": title,
                "count": 0,        # 帖子数（精确匹配数）
                "heat": 0,         # 热度（点赞+浏览+评论）
            }
        title_groups[title]["count"] += 1
        title_groups[title]["heat"] += (p.like_count or 0) + (p.view_count or 0) + (p.comment_count or 0)

    # 2) 简易分词（提取标题中的 2~10 字中文片段）
    word_count: dict[str, int] = {}
    stop_words = {'的', '了', '是', '在', '我', '你', '他', '她', '它', '有', '和', '就', '都', '也',
                  '不', '人', '一种', '一个', '一些', '我们', '你们', '他们', '这个', '那个',
                  '可以', '应该', '需要', '可能', '或者', '如果', '那么', '因为', '所以', '但是'}
    import re
    split_re = re.compile(r'[\s,。.!?？!；;：:\-_—/\\()（）【】\[\]·…=+]+')
    for p in posts:
        title = p.title or ''
        words = split_re.split(title)
        for w in words:
            w = w.strip()
            if 2 <= len(w) <= 10 and w not in stop_words and not re.match(r'^[0-9=+\-]+$', w):
                # 用 fr"{w}" 强制匹配这个词在数据库里出现多少次
                word_count[w] = Post.query.filter(
                    Post.is_deleted == 0, Post.status == 1,
                    Post.title.like(f"%{w}%"),
                ).count()

    # 合并：标题作为主要来源 + 词频作为补充
    candidates: dict[str, dict] = {}
    for title, info in title_groups.items():
        candidates[title] = {
            "label": title,
            "count": info["count"],
            "heat": info["heat"],
        }
    for word, cnt in word_count.items():
        if word in candidates:
            continue
        # 词的 count = 数据库中包含该词的帖子数（真实计数）
        if cnt > 0:
            candidates[word] = {"label": word, "count": cnt, "heat": cnt * 5}

    # 按热度排序 + 取前 10
    top = sorted(candidates.values(), key=lambda x: (-x["heat"], -x["count"]))[:10]

    # 不足 10 条时，从真实的帖子中补
    if len(top) < 10:
        for p in sorted(posts, key=lambda x: -(x.like_count + x.view_count)):
            if len(top) >= 10: break
            t = (p.title or '').strip()
            if 1 <= len(t) <= 12 and t not in candidates:
                candidates[t] = {"label": t, "count": 1, "heat": p.like_count + p.view_count + 1}
                top = sorted(candidates.values(), key=lambda x: (-x["heat"], -x["count"]))[:10]

    return success(data=[{"label": x["label"], "count": x["count"]} for x in top])


@post_bp.route("/search-suggest", methods=["GET"])
def search_suggest():
    """搜索建议：输入框自动补全
    参数：prefix=xxx（前缀，至少 1 字）
    """
    prefix = (request.args.get("prefix") or "").strip()
    if not prefix:
        return success(data=[])

    posts = Post.query.filter(
        Post.is_deleted == 0,
        Post.status == 1,
        Post.title.like(f"%{prefix}%"),
    ).order_by(Post.like_count.desc(), Post.id.desc()).limit(8).all()

    return success(data=[{"title": p.title, "id": p.id} for p in posts])


@post_bp.route("/trending", methods=["GET"])
def post_trending():
    """首页 trending 板块：每板块的浏览量上涨数据（按板块）"""
    from datetime import datetime, timedelta
    range_type = request.args.get("range", "week")  # week / month

    if range_type == "month":
        cutoff = datetime.now() - timedelta(days=30)
    else:
        cutoff = datetime.now() - timedelta(days=7)
        range_type = "week"

    # 每个板块的总浏览、本期新增浏览、活跃帖数
    sql = """
        SELECT
            b.id AS board_id,
            b.name AS board_name,
            b.icon AS board_icon,
            COALESCE(SUM(p.view_count), 0) AS total_view,
            COALESCE(SUM(CASE WHEN p.created_at >= %s THEN p.view_count ELSE 0 END), 0) AS recent_view,
            COUNT(p.id) AS post_count,
            COALESCE(SUM(CASE WHEN p.created_at >= %s THEN 1 ELSE 0 END), 0) AS recent_post_count
        FROM pf_boards b
        LEFT JOIN pf_posts p ON p.board_id = b.id AND p.is_deleted = 0
        WHERE b.status = 1
        GROUP BY b.id, b.name, b.icon
        ORDER BY recent_view DESC
    """
    conn = db.session.connection()
    rows = conn.exec_driver_sql(sql, (cutoff, cutoff)).fetchall()

    boards_data = []
    max_recent = max([int(r[4]) for r in rows] + [1])  # 用于计算比例
    for r in rows:
        boards_data.append({
            "board_id": int(r[0]),
            "board_name": r[1],
            "board_icon": r[2] or "💬",
            "total_view": int(r[3]),
            "recent_view": int(r[4]),
            "post_count": int(r[5]),
            "recent_post_count": int(r[6]),
            "percent": round(int(r[4]) / max_recent * 100, 1) if max_recent > 0 else 0,
        })

    # 全站总览
    total_recent = sum(b["recent_view"] for b in boards_data)
    total_posts = sum(b["recent_post_count"] for b in boards_data)

    return success(data={
        "range": range_type,
        "boards": boards_data,
        "summary": {
            "total_recent_view": total_recent,
            "total_recent_posts": total_posts,
            "active_boards": len([b for b in boards_data if b["recent_view"] > 0]),
            "max_recent_view": max_recent,
        }
    })


def _build_comments_tree(post_id: int, anonymous_id_model, post_author_id: int, viewer_id: int, viewer_role: int) -> list:
    """复用 comment 模块的 3 层树构造"""
    from app.blueprints.comment import _build_comments_tree as _tree
    return _tree(post_id, anonymous_id_model, post_author_id, viewer_id, viewer_role)


@post_bp.route("/<int:post_id>", methods=["GET"])
def get_post_detail(post_id):
    """T10: 帖子详情：仅在「主动进入浏览」时 +1 浏览量"""
    post = Post.query.filter_by(id=post_id, is_deleted=0).first()
    if not post:
        raise NotFoundError("帖子不存在")

    # 浏览量 +1：仅本次请求触发了「进入详情」才计数
    # 1) 同一用户/IP 10 秒内不重复计数（Redis 去重）
    # 2) 不影响点赞/评论等其他接口的计数（只有 GET 详情才触发）
    user_id = session.get("user_id") or 0
    ip = request.remote_addr or "unknown"
    viewer_key = f"view:post:{post_id}:u{user_id}:ip{ip}"
    is_new_view = redis_client.set(viewer_key, "1", ex=10, nx=True)  # 10 秒内不重复
    if is_new_view:
        Post.query.filter_by(id=post_id).update({Post.view_count: Post.view_count + 1})
        db.session.commit()
        # 重新读取最新的 view_count（因为上面 update 是基于已加载的 post）
        db.session.refresh(post)

    anon = AnonymousIdMapping.query.get(post.anonymous_id)
    board = Board.query.get(post.board_id)

    # 评论树（最多 3 层）
    viewer_id = session.get("user_id") or 0
    viewer_role = session.get("role", 1)
    comments_data = _build_comments_tree(
        post_id, AnonymousIdMapping, post.user_id, viewer_id, viewer_role
    )

    return success(data={
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "anonymous_name": anon.anonymous_name if anon else "匿名用户",
        "board_name": board.name if board else "",
        "like_count": post.like_count,
        "dislike_count": post.dislike_count,
        "comment_count": post.comment_count,
        "view_count": post.view_count,
        "is_top": post.is_top,
        "is_author": session.get("user_id") == post.user_id,
        "is_admin": session.get("role") == 3,
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
        "comments": comments_data,
    })


@post_bp.route("/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    """T10: 点赞/点踩"""
    user_id = _login_required()
    data = request.get_json(silent=True) or {}
    action = data.get("action", "like")  # like / dislike / cancel

    post = Post.query.filter_by(id=post_id, is_deleted=0).first()
    if not post:
        raise NotFoundError("帖子不存在")

    key = f"like:{user_id}:post:{post_id}"
    current = redis_client.get(key)

    if action == "cancel":
        if current == "like":
            Post.query.filter_by(id=post_id).update({Post.like_count: Post.like_count - 1})
            # 帖主收到的「被点赞帖子计数」：只有取消到 0 才 -1
            if post.like_count - 1 == 0:
                User.query.filter_by(id=post.user_id).update({User.liked_post_count: User.liked_post_count - 1})
        elif current == "dislike":
            Post.query.filter_by(id=post_id).update({Post.dislike_count: Post.dislike_count - 1})
        redis_client.delete(key)
    elif action == "like":
        if current == "dislike":
            Post.query.filter_by(id=post_id).update({
                Post.like_count: Post.like_count + 1,
                Post.dislike_count: Post.dislike_count - 1,
            })
            # 从踩改为赞：赞从 0 变为 1，+1
            User.query.filter_by(id=post.user_id).update({User.liked_post_count: User.liked_post_count + 1})
        elif current != "like":
            Post.query.filter_by(id=post_id).update({Post.like_count: Post.like_count + 1})
            # 第一次点赞：+1
            User.query.filter_by(id=post.user_id).update({User.liked_post_count: User.liked_post_count + 1})
        redis_client.setex(key, 86400, "like")
    elif action == "dislike":
        if current == "like":
            Post.query.filter_by(id=post_id).update({
                Post.like_count: Post.like_count - 1,
                Post.dislike_count: Post.dislike_count + 1,
            })
            # 从赞改为踩：赞从 1 变为 0，-1
            User.query.filter_by(id=post.user_id).update({User.liked_post_count: User.liked_post_count - 1})
        elif current != "dislike":
            Post.query.filter_by(id=post_id).update({Post.dislike_count: Post.dislike_count + 1})
        redis_client.setex(key, 86400, "dislike")

    db.session.commit()
    return success(message=f"已{action}")


@post_bp.route("/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """删除帖子：仅作者本人 + 管理员可删（软删除）"""
    user_id = _login_required()
    post = Post.query.filter_by(id=post_id, is_deleted=0).first()
    if not post:
        raise NotFoundError("帖子不存在")

    role = session.get("role", 1)
    is_author = post.user_id == user_id
    is_admin = role == 3
    if not (is_author or is_admin):
        raise ForbiddenError("无权删除该帖子")

    Post.query.filter_by(id=post_id).update({Post.is_deleted: 1, Post.status: 0})
    Board.query.filter_by(id=post.board_id).update(
        {Board.post_count: Board.post_count - 1}
    ) if post.board_id else None
    # 彻底删除：原帖 is_deleted=1 → 帖主 post_count 减 1（持久化字段「发布帖子数」）
    # 注：User.post_count 字段未独立维护，此处改回退到实时统计
    db.session.commit()
    return success(message="帖子已删除")
