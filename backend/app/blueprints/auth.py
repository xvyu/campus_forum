"""认证蓝图：图形验证码、邮箱验证码、注册、登录/登出/当前用户"""
import io
import base64
import random
import string
from datetime import datetime

from flask import Blueprint, request, session, g
from app.extensions import db, redis_client
from app.errors import success, fail, ParamError, NotFoundError, UnauthorizedError, RateLimitError, DuplicateError, EmailSendError
from app.models.user import User, AnonymousIdMapping
from app.utils import bcrypt_util, email_util, ratelimit
from app.utils.captcha_util import generate_captcha

auth_bp = Blueprint("auth", __name__)


def _check_captcha(uuid: str, answer: str) -> bool:
    """校验图形验证码"""
    key = f"captcha:{uuid}"
    stored = redis_client.get(key)
    if not stored:
        return False
    redis_client.delete(key)
    return stored.lower() == answer.lower()


def _send_email_code(email: str) -> str:
    """生成验证码并发送；成功返回 code，失败抛 EmailSendError"""
    code = "".join(random.choices(string.digits, k=6))
    key = f"email_code:{email}"
    redis_client.setex(key, 300, code)  # 5 分钟有效
    subject = "【Campus Forum】邮箱验证码"
    valid_minutes = 5
    html = f"""
    <div style="max-width:600px;margin:0 auto;padding:32px 24px;background:#ffffff;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,'PingFang SC','Microsoft YaHei',Arial,sans-serif;color:#333;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="display:inline-block;width:60px;height:60px;line-height:60px;background:linear-gradient(135deg,#409EFF 0%,#67C23A 100%);color:#fff;font-size:28px;border-radius:12px;">🌳</div>
        <h1 style="margin:12px 0 0;font-size:22px;color:#303133;">Campus Forum</h1>
        <p style="margin:4px 0 0;font-size:13px;color:#909399;">Campus Forum</p>
      </div>

      <div style="background:#f5f7fa;padding:24px;border-radius:8px;margin-bottom:24px;">
        <p style="margin:0 0 16px;font-size:15px;color:#606266;">您好！</p>
        <p style="margin:0 0 12px;font-size:15px;color:#606266;line-height:1.8;">您正在进行 <b style="color:#409EFF;">Campus Forum</b> 邮箱验证，本次验证码为：</p>
        <div style="text-align:center;margin:20px 0;">
          <div style="display:inline-block;font-size:36px;font-weight:700;color:#409EFF;letter-spacing:8px;padding:16px 32px;background:#fff;border:2px dashed #409EFF;border-radius:8px;">{code}</div>
        </div>
        <p style="margin:0;font-size:14px;color:#909399;">验证码 <b>{valid_minutes} 分钟</b>内有效，请尽快使用。</p>
      </div>

      <div style="background:#fdf6ec;padding:14px 18px;border-left:3px solid #E6A23C;border-radius:4px;margin-bottom:24px;">
        <p style="margin:0;font-size:13px;color:#8b6914;line-height:1.7;">
          ⚠️ 安全提示：请勿将验证码透露给他人，工作人员不会向您索要此验证码。
        </p>
      </div>

      <p style="font-size:14px;color:#606266;line-height:1.8;">
        如果这不是您的操作，请忽略本邮件，您的账号安全不会受到影响。
      </p>

      <hr style="border:none;border-top:1px solid #ebeef5;margin:24px 0;" />

      <p style="text-align:center;font-size:12px;color:#909399;line-height:1.6;margin:0;">
        此邮件由系统自动发送，请勿直接回复<br />
        © 2026 Campus Forum · 让每个学生都能匿名说出心声
      </p>
    </div>
    """
    plain = (
        f"【Campus Forum】邮箱验证码\n\n"
        f"您好！\n"
        f"您正在进行Campus Forum邮箱验证，本次验证码为：{code}\n"
        f"验证码 {valid_minutes} 分钟内有效，请尽快使用。\n\n"
        f"安全提示：请勿将验证码透露给他人，工作人员不会向您索要此验证码。\n\n"
        f"如果这不是您的操作，请忽略本邮件，您的账号安全不会受到影响。\n\n"
        f"—— Campus Forum · 2026"
    )
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        email_util.send_email_multipart(email, subject, html, plain)
        from loguru import logger
        logger.success(f"[Email] 验证码已发送至 {email}")
        return code
    except email_util.EmailConfigError as e:
        from loguru import logger
        logger.error(f"[Email] 发送失败: {e}")
        redis_client.delete(key)
        raise EmailSendError(str(e))


@auth_bp.route("/", methods=["GET"])
def index():
    return success(data={"module": "auth", "status": "ok"}, message="auth blueprint ok")


@auth_bp.route("/captcha", methods=["GET"])
def get_captcha():
    """T06: 获取图形验证码（返回 base64 图片 + uuid）"""
    image, answer = generate_captcha()
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    uuid_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=16))
    redis_client.setex(f"captcha:{uuid_key}", 180, answer)

    return success(data={"uuid": uuid_key, "image": f"data:image/png;base64,{img_b64}"})


@auth_bp.route("/send-code", methods=["POST"])
def send_email_code():
    """T06: 发送邮箱验证码"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email or "@" not in email:
        raise ParamError("请输入有效邮箱")
    if not email.endswith("@qq.com"):
        raise ParamError("请使用 QQ 邮箱（@qq.com）")

    # 同一邮箱 20 秒内只发一次（防止用户狂点浪费配额）
    if not ratelimit.check_rate_limit(f"email_code_addr:{email}", 1, 20):
        raise RateLimitError("操作过于频繁，请 20 秒后再试")

    # IP 限流（每小时 10 次）
    ip = request.remote_addr or "unknown"
    if not ratelimit.check_rate_limit(f"email_code_ip:{ip}", 10, 3600):
        raise RateLimitError()

    _send_email_code(email)
    return success(message="验证码已发送")


@auth_bp.route("/register", methods=["POST"])
def register():
    """T07: 注册 + QQ 邮箱验证"""
    data = request.get_json(silent=True) or {}
    student_id = (data.get("student_id") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    captcha_uuid = (data.get("captcha_uuid") or "").strip()
    captcha_answer = (data.get("captcha_answer") or "").strip()
    email_code = (data.get("email_code") or "").strip()

    # 参数校验
    if not all([student_id, email, password, captcha_uuid, captcha_answer, email_code]):
        raise ParamError("缺少必填参数")
    if len(password) < 8:
        raise ParamError("密码至少 8 位")
    if not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
        raise ParamError("密码必须同时包含字母和数字")
    if len(student_id) < 5:
        raise ParamError("学号格式不正确")
    if not email.endswith("@qq.com"):
        raise ParamError("请使用 QQ 邮箱（@qq.com）")

    # 验证图形验证码
    if not _check_captcha(captcha_uuid, captcha_answer):
        raise ParamError("图形验证码错误或已过期")

    # 验证邮箱验证码
    stored_code = redis_client.get(f"email_code:{email}")
    if not stored_code or stored_code != email_code:
        raise ParamError("邮箱验证码错误或已过期")
    redis_client.delete(f"email_code:{email}")

    # 检查重复
    if User.query.filter_by(student_id=student_id).first():
        raise DuplicateError("该学号已注册")
    if User.query.filter_by(email=email).first():
        raise DuplicateError("该邮箱已注册")

    # 密码哈希
    password_hash = bcrypt_util.hash_password(password)

    # 创建用户
    now = datetime.now()
    user = User(
        school_id=1,
        student_id=student_id,
        email=email,
        password_hash=password_hash,
        nickname=f"树洞用户{random.randint(1000, 9999)}",
        role=1,
        status=1,
        email_verified_at=now,
    )
    db.session.add(user)
    db.session.flush()

    # 创建默认匿名身份
    anon = AnonymousIdMapping(
        user_id=user.id,
        school_id=1,
        anonymous_name=f"{random.choice(['风', '云', '星', '月', '花', '雪', '雨', '光','零','默','许'])}{random.choice(['中', '下', '边', '前', '后', '上', '间', '里'])}{random.randint(100, 999)}",
        is_default=1,
        is_active=1,
    )
    db.session.add(anon)
    db.session.commit()

    # 设置登录 Session
    session["user_id"] = user.id
    session["role"] = user.role
    session.permanent = True

    # 生成 token
    from app.utils.auth_token import generate_token
    token = generate_token(user.id, user.role)

    return success(data={"user_id": user.id, "token": token}, message="注册成功")


@auth_bp.route("/login", methods=["POST"])
def login():
    """T08: 登录"""
    data = request.get_json(silent=True) or {}
    student_id = (data.get("student_id") or "").strip()
    password = data.get("password") or ""
    captcha_uuid = (data.get("captcha_uuid") or "").strip()
    captcha_answer = (data.get("captcha_answer") or "").strip()

    if not all([student_id, password]):
        raise ParamError("请输入学号和密码")

    # IP 限流
    ip = request.remote_addr or "unknown"
    if not ratelimit.check_rate_limit(f"login_ip:{ip}", 10, 60):
        raise RateLimitError()

    # 验证图形验证码
    if captcha_uuid and captcha_answer:
        if not _check_captcha(captcha_uuid, captcha_answer):
            raise ParamError("图形验证码错误")

    user = User.query.filter_by(student_id=student_id).first()
    if not user:
        raise NotFoundError("账号不存在")
    if user.status != 1:
        raise UnauthorizedError("账号已被禁用")
    if not bcrypt_util.check_password(password, user.password_hash):
        raise ParamError("密码错误")

    session["user_id"] = user.id
    session["role"] = user.role
    session.permanent = True

    # 生成 token（替代 cookie session，解决跨域问题）
    from app.utils.auth_token import generate_token
    token = generate_token(user.id, user.role)

    return success(
        data={
            "user_id": user.id,
            "nickname": user.nickname,
            "token": token,
        },
        message="登录成功",
    )


@auth_bp.route("/reset-password/send-code", methods=["POST"])
def send_reset_code():
    """T07-扩展: 忘记密码 - 发送重置验证码（必须用注册邮箱）"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email or "@" not in email:
        raise ParamError("请输入有效邮箱")
    if not email.endswith("@qq.com"):
        raise ParamError("请使用 QQ 邮箱（@qq.com）")

    # 必须先存在该邮箱的用户
    user = User.query.filter_by(email=email).first()
    if not user:
        # 安全考虑：不直接告诉"邮箱不存在"，而是发一个伪码（不真正发邮件）
        # 这里采用真实策略：邮箱不存在则报错，避免被恶意遍历
        raise NotFoundError("该邮箱未注册")

    # 限流
    if not ratelimit.check_rate_limit(f"reset_code_addr:{email}", 1, 60):
        raise RateLimitError("操作过于频繁，请 60 秒后再试")
    ip = request.remote_addr or "unknown"
    if not ratelimit.check_rate_limit(f"reset_code_ip:{ip}", 10, 3600):
        raise RateLimitError()

    _send_email_code(email)
    return success(message="重置验证码已发送，请查收邮箱")


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """T07-扩展: 忘记密码 - 用邮箱验证码重置密码"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    email_code = (data.get("email_code") or "").strip()
    new_password = data.get("new_password") or ""

    # 参数校验
    if not all([email, email_code, new_password]):
        raise ParamError("缺少必填参数")
    if "@" not in email or not email.endswith("@qq.com"):
        raise ParamError("请使用 QQ 邮箱（@qq.com）")
    if len(new_password) < 8:
        raise ParamError("新密码至少 8 位")
    if not (any(c.isalpha() for c in new_password) and any(c.isdigit() for c in new_password)):
        raise ParamError("新密码必须同时包含字母和数字")

    # 验证邮箱验证码
    stored_code = redis_client.get(f"email_code:{email}")
    if not stored_code or stored_code != email_code:
        raise ParamError("邮箱验证码错误或已过期")
    redis_client.delete(f"email_code:{email}")

    # 找用户
    user = User.query.filter_by(email=email).first()
    if not user:
        raise NotFoundError("该邮箱未注册")

    # 新密码不能与旧密码一致
    if bcrypt_util.check_password(new_password, user.password_hash):
        raise ParamError("新密码不能与旧密码相同")

    # 重置密码
    user.password_hash = bcrypt_util.hash_password(new_password)
    db.session.commit()

    return success(message="密码已重置，请使用新密码登录")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """T08: 登出"""
    session.clear()
    return success(message="已退出登录")


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """T08: 获取当前用户"""
    user_id = session.get("user_id") or g.get("user_id")
    if not user_id:
        raise UnauthorizedError()

    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("用户不存在")

    anon = AnonymousIdMapping.query.filter_by(
        user_id=user.id, is_default=1, is_active=1
    ).first()

    return success(data={
        "user_id": user.id,
        "nickname": user.nickname,
        "role": user.role,
        "email_verified": user.email_verified_at is not None,
        "anonymous_name": anon.anonymous_name if anon else "",
    })
