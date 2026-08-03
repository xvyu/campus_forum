"""图形验证码生成（基于 captcha 库）"""
import random
import string
from captcha.image import ImageCaptcha


def generate_captcha(length: int = 4) -> tuple:
    """生成图形验证码，返回 (PIL Image, answer_text)"""
    answer = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
    image = ImageCaptcha(width=160, height=60, font_sizes=(42,))
    img = image.generate_image(answer)
    return img, answer
