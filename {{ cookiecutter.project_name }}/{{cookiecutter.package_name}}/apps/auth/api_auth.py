import datetime
from datetime import timedelta

from fastapi import APIRouter, Form, Request, HTTPException

from {{cookiecutter.package_name}}.apps.auth.dao_user import userDao
from {{cookiecutter.package_name}}.core.db import get_db
from {{cookiecutter.package_name}}.core.settings import config
from {{cookiecutter.package_name}}.core.utils_auth import create_access_token
from {{cookiecutter.package_name}}.core.utils_resp import RespJSON, gen_resp

auth = APIRouter(prefix='/auth', tags=['安全'])


# 1. 登录验证
@auth.post('/token', summary='用户登录并返回JWT令牌')
def token(username: str = Form(), password: str = Form()) -> RespJSON:
    user = userDao.authenticate_user(get_db(), username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 生成令牌（包含用户名和角色）
    access_token_expires = timedelta(minutes=int(config.get('ACCESS_TOKEN_EXPIRE_MINUTES')))  # type:ignore
    access_token = create_access_token(
        data={
            "sub": user.id,
            "ustyle": user.ustyle,
            "iat": datetime.datetime.utcnow(),  # 标准声明：签发时间（UTC时间）
        },  # 令牌中存储的信息
        expires_delta=access_token_expires
    )

    return gen_resp(data={"access_token": access_token, "token_type": "bearer"}, msg='登录成功')


# 2. 获取当前用户信息（需登录）
@auth.get("/me", summary='获取当前用户信息（需登录）')
async def read_current_user(request: Request) -> RespJSON:
    print('获取uid', request.state._state)
    uid = request.state.uid
    current_user = userDao.get_by_id(get_db(), int(uid))  # type: ignore
    return gen_resp(data={'username': current_user.username}, msg='获取当前用户信息成功')  # type:ignore


# 3. 退出
@auth.post('/logout', summary='登出')
def dologout():
    return gen_resp(msg='登出成功')
