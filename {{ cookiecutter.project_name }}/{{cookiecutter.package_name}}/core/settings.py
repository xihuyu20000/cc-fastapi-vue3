import os
from dotenv import dotenv_values, load_dotenv, find_dotenv
from pathlib import Path
# 自动搜索 .env 文件
# 或者指定 .env 文件位置
env_path = Path('') / '.env'
load_dotenv(find_dotenv(filename=str(env_path)), verbose=True, override=True)


class Config:
    def __init__(self):
        self.config = {
            **dotenv_values(".env"),    # 基础配置
            **dotenv_values(".env.secret"),  # 密钥配置
            **os.environ                    # 系统环境变量
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)

config = Config()