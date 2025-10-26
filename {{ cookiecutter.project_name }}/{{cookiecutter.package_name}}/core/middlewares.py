import time
import traceback
from http import HTTPStatus

import jwt
from fastapi import FastAPI
from fastapi import Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from {{cookiecutter.package_name}}.core.log import logger
from {{cookiecutter.package_name}}.core.settings import config

STRICT_WHITELIST = [s.strip() for s in str(config.get('STRICT_WHITELIST')).split(',')]
PREFIX_WHITELIST = [s.strip() for s in str(config.get('PREFIX_WHITELIST')).split(',')]


async def jwt_middleware(request: Request, call_next):
    currpath = request.url.path
    print('请求路径', currpath)

    if (currpath in STRICT_WHITELIST) or any([currpath.startswith(path) for path in PREFIX_WHITELIST]):
        print('走白名单')
        return await call_next(request)

    authorization = request.headers.get("Authorization")
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header missing"}
        )

    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid authentication scheme"}
        )

    try:
        payload = jwt.decode(jwt=token, key=str(config.get('SECRET_KEY')),
                             algorithms=[str(config.get('ALGORITHM', "HS256"))], options={"verify_sub": False})
        # Add user info to request state
        request.state.uid = payload.get("sub")
    except jwt.PyJWTError as e:
        print(e)
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token"}
        )

    return await call_next(request)


async def log_middleware(req: Request, call_next: RequestResponseEndpoint):
    try:
        start = time.perf_counter()
        req_method: str = req.method
        url_path: str = req.url.path
        query_params = req.query_params
        query_json = ''
        if 'application/json' in req.headers.get('Content-Type', ''):
            body = await req.json()
            query_json = str(body)
        auth_header = req.headers.get("Authorization")

        resp = await call_next(req)

        process_time = time.perf_counter() - start
        resp.headers["X-Response-Time"] = f"{process_time:.2f}s"

        logger.info(
            f"{req_method=} {url_path=} {query_params=} {query_json=} {auth_header=} {resp.status_code=} {process_time:.2f}s")

        return resp
    except Exception as e:
        error_info = {
            "error": str(e),
            "path": req.url.path,
            "method": req.method,
            "traceback": traceback.format_exc()
        }
        logger.error(error_info)
        return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "服务器内部错误"})


async def exception_middleware(req: Request, call_next: RequestResponseEndpoint):
    try:
        resp = await call_next(req)
        return resp
    except Exception as e:
        error_info = {
            "error": str(e),
            "path": req.url.path,
            "method": req.method,
            "traceback": traceback.format_exc()
        }
        logger.error(error_info)
        return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"message": "服务器内部错误"})

def register_middlewares(app: FastAPI):
    """注册中间件（逆序执行）"""
    app.add_middleware(CORSMiddleware,
                           allow_origins=['*'],
                           allow_methods=["*"],
                           allow_headers=["*"], )
    app.middleware('http')(exception_middleware)
    app.middleware('http')(jwt_middleware)
    app.middleware('http')(log_middleware)

