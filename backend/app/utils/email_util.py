"""多账号 QQ 邮箱 SMTP 轮发（避免单账号日发量上限）"""
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app


def _parse_accounts() -> list[tuple[str, str]]:
    """解析 SMTP_ACCOUNTS 配置，返回 [(邮箱, 授权码), ...]"""
    raw = current_app.config.get("SMTP_ACCOUNTS", "")
    accounts = []
    for item in raw.split(","):
        item = item.strip()
        if not item or ":" not in item:
            continue
        email_part, pwd = item.split(":", 1)
        email_part = email_part.strip()
        pwd = pwd.strip()
        # 用正则提取裸邮箱（parseaddr 在 Python 3.8 把裸邮箱当 realname）
        m = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", email_part)
        email = m.group(0) if m else email_part
        if email and pwd and not pwd.startswith("your_"):
            accounts.append((email, pwd))
    return accounts


class EmailConfigError(Exception):
    """SMTP 账号未配置或格式错误"""


def _send(msg: MIMEMultipart, to_email: str) -> bool:
    accounts = _parse_accounts()
    if not accounts:
        raise EmailConfigError("SMTP_ACCOUNTS 未配置有效 QQ 邮箱账号（请在 backend/.env 中填写真实邮箱和授权码）")

    server = current_app.config.get("SMTP_SERVER", "smtp.qq.com")
    port = current_app.config.get("SMTP_PORT", 465)
    use_ssl = current_app.config.get("SMTP_USE_SSL", True)

    last_error = None
    for email, password in accounts:
        try:
            msg["From"] = email
            msg["To"] = to_email

            if use_ssl:
                with smtplib.SMTP_SSL(server, port, timeout=10) as s:
                    s.login(email, password)
                    s.send_message(msg)
            else:
                with smtplib.SMTP(server, port, timeout=10) as s:
                    s.starttls()
                    s.login(email, password)
                    s.send_message(msg)
            return True
        except Exception as e:
            last_error = f"{email}: {type(e).__name__}: {str(e)[:80]}"
            continue

    raise EmailConfigError(
        f"所有 SMTP 账号均发送失败，最后错误：{last_error}。请检查 backend/.env 中 SMTP_ACCOUNTS 配置"
    )


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """发送纯 HTML 邮件（兼容老接口）"""
    msg = MIMEText(html_content, "html", "utf-8")
    msg["Subject"] = subject
    return _send(msg, to_email)


def send_email_multipart(to_email: str, subject: str, html_content: str, plain_content: str) -> bool:
    """发送多部分邮件（HTML + 纯文本），邮件客户端会自动选择最佳呈现方式"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg.attach(MIMEText(plain_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    return _send(msg, to_email)
