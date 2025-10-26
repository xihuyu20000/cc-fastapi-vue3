from typing import Optional
import jwt
from passlib.context import CryptContext
import datetime as dt

from {{cookiecutter.package_name}}.core.settings import config

# ------------------- 密码哈希处理 -------------------
# 初始化密码哈希上下文
pwd_context = CryptContext(
    schemes=["argon2"],  # 仅用 Argon2
    deprecated="auto"    # 自动废弃旧算法（可选）
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """将明文密码转换为哈希值"""
    return pwd_context.hash(password)


    # ------------------- JWT令牌生成与验证 -------------------
def create_access_token(data: dict, expires_delta: Optional[dt.timedelta] = None) -> str:
    """生成JWT令牌"""
    payload = data.copy()
    # 设置过期时间

    expire = dt.datetime.now(dt.UTC) + (expires_delta or dt.timedelta(minutes=int(config.get('ACCESS_TOKEN_EXPIRE_MINUTES', 60))))
    payload.update({"exp": expire})  # 标准JWT字段：exp（过期时间）
    # 加密生成令牌
    token = jwt.encode(payload, config.get('SECRET_KEY'), algorithm=config.get('ALGORITHM'))
    return token

def verify_token(authorization: str) -> dict:
    """验证JWT令牌"""
    try:
        _, token = authorization.split()
        payload = jwt.decode(token, config.get('SECRET_KEY'), algorithms=[str(config.get('ALGORITHM'))])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}