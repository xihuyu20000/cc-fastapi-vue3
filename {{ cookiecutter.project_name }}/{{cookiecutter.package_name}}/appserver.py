from pathlib import Path

from fastapi import FastAPI
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from {{cookiecutter.package_name}}.apps import register_routers
from {{cookiecutter.package_name}}.core.middlewares import register_middlewares
from {{cookiecutter.package_name}}.core.settings import config

app = FastAPI(title='新项目', description='我的新项目', version='0.1.0')
register_middlewares(app)
register_routers(app)

@app.get('/')
def appserver():
    app.mount('/assets', StaticFiles(directory=Path(__file__).parent / 'distvue' / 'assets'))
    app.mount('/templates', StaticFiles(directory=Path(__file__).parent / 'distvue'))
    index_path = Path(__file__).parent / 'distvue' / 'index.html'
    return FileResponse(index_path)

if __name__ == "__main__":
    import uvicorn
    web_server_port = int(config.get('web_server_port', 7000))
    uvicorn.run("__main__:app", host="0.0.0.0", port=web_server_port, reload=False)