import os
import sys
import shutil
import subprocess

python_version = '{{ cookiecutter.python_version }}'
def post_gen_project():
    project_dir = os.getcwd()
    parent_dir_path = os.path.dirname(project_dir)
    print('Post-generating project...........................', project_dir)
    
    # 同步依赖包
    print('Syncing dependencies...........................')
    try:
        subprocess.run(['uv', 'venv', '-p', python_version], cwd=project_dir)
        subprocess.run(['uv' ,'sync', '--upgrade-package', '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'], cwd=project_dir,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except Exception as e:
        print('Please sync dependencies manually ', str(e))

    # 初始化Git仓库
    print('Initializing Git repository...........................')
    try:
        subprocess.run(['git', 'init'], cwd=project_dir)
        subprocess.run(['git', 'add', '.'], cwd=project_dir)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=project_dir)
    except Exception as e:
        print('Please initialize Git repository manually ', str(e))

post_gen_project()