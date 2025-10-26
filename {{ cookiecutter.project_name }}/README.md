## 首次使用
```
pip install cookiecutter

从远程模板生成项目 例如，使用 GitHub 上的模板：
cookiecutter https://github.com/audreyr/cookiecutter-pypackage


从本地模板生成项目 如果有本地模板：
cookiecutter /path/to/local/template
```
## 修改模板
```
在新的项目中修改内容之后，复制apps、core、frontend、tests等变化的文件夹到模板项目中。

然后将backend替换为{{cookiecutter.package_name}}
```

## 同步环境
```shell
.\.venv\Scripts\activate.bat
uv sync -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 初始化数据

```shell
.\.venv\Scripts\activate.bat
uv run .\{{cookiecutter.package_name}}\core\init_db.py --active
```

## 运行测试

```shell
.\.venv\Scripts\activate.bat
pytest .\tests\test-main.py
```
## 运行项目

```shell
.\.venv\Scripts\activate.bat
fastapi dev .\{{cookiecutter.package_name}}\main.py --port 8000
```


## 前端项目
```
进入到frontend目录下
pnpm install
pnpm dev
运行pnpm build打包到distvue目录下
如果不需要前端项目，删除目录frontend。

```