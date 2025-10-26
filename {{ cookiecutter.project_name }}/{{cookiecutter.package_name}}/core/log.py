from loguru import logger
import sys

# Loguru一行代码即可完成相同功能
logger.add(sys.stdout, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<5} | {module}.{function}:{line} | {message}")
logger.add("{{cookiecutter.package_name}}.log", mode="w", level="DEBUG", rotation="500 MB", retention="10 days",enqueue=True, format="{time} - {name} - {level} - {file}:{line} - {message}")


# 4. 导出Logger实例（供其他模块导入）
__all__ = ["logger"]