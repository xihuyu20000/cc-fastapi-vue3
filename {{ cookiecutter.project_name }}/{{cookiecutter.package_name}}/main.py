from fastapi import FastAPI

from {{cookiecutter.package_name}}.apps import register_routers
from {{cookiecutter.package_name}}.core.middlewares import register_middlewares
from {{cookiecutter.package_name}}.core.utils_resp import gen_resp

app = FastAPI(title='新项目', description='我的新项目', version='0.1.0')
register_middlewares(app)
register_routers(app)


@app.get("/api",
         tags=["测试"],
         summary="测试接口，返回Hello World",
         description="这只是一个测试接口")
def index():
    return gen_resp(msg="这是公开接口，无需登录即可访问")
