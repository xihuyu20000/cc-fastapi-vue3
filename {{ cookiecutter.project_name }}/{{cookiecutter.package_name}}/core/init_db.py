import sys
sys.path.append('')
sys.path.append('src')

from {{cookiecutter.package_name}}.apps.auth.dao_user import User
from {{cookiecutter.package_name}}.core.db import engine, get_db, BaseM
from {{cookiecutter.package_name}}.core.utils_auth import get_password_hash
def init_db():
    db = get_db()

    users=[User(username=f'test{i}', hashpwd=get_password_hash(f'test{i}')) for i in range(1, 101)]
    db.add_all(users)

    db.commit()
    db.close()

def main():
    BaseM.metadata.drop_all(bind=engine)
    BaseM.metadata.create_all(bind=engine)
    init_db()

if __name__ == '__main__':
    main()