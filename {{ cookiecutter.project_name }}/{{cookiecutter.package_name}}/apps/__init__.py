from fastapi import FastAPI

from {{cookiecutter.package_name}}.apps.auth.api_auth import auth
def register_routers(app:FastAPI):
    app.include_router(auth, prefix="/api")