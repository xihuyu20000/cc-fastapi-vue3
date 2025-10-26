from typing import Optional

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Session

from {{cookiecutter.package_name}}.core.db import BaseDao, BaseEntity
from {{cookiecutter.package_name}}.core.utils_auth import get_password_hash, verify_password


class User(BaseEntity):
    __tablename__ = "sys_user"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashpwd = Column(String(1024), comment='密码，非明文')
    email = Column(String(50), comment='发送初始密码或者忘记密码')
    phone = Column(String(20), comment='手机号')
    realname = Column(String(50), comment='真实姓名')
    activated = Column(Integer, default=0, comment='是否激活, 1激活，0未激活。新用户默认未激活')
    enabled = Column(Integer, default=1, comment='禁用状态, 1：正常，0：禁用。休假或者辞职用户，停用后无法登录')
    locked = Column(Integer, default=1, comment='锁定状态, 1：正常，0：锁定。锁定用户只能查询，不能增删改操作')
    ustyle = Column(Integer, default=1, comment="用户类型， 1普通用户 2超级用户 3开发人员")
    terminals = Column(Text, comment='用户允许登录的终端，多个用逗号隔开')
    attrs = Column(Text, comment='用户属性，多个用逗号隔开，用于解决数据权限')


class UserDao(BaseDao[User]):
    model = User

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """验证用户（用户名+密码）"""
        user: User = self.get_by_conditions(db, {'username': username})
        if not user or not verify_password(password, user.hashpwd):  # type:ignore
            return None
        return user

    def reset_password(self, db: Session, username: str, password: str) -> Optional[User]:
        """重置密码"""
        user: User = self.get_by_conditions(db, {'username': username})
        if not user:
            return None
        user.hashpwd = get_password_hash(password)  # type:ignore
        db.commit()
        return user

    def modify_password(self, db: Session, username: str, old_password: str, new_password: str) -> Optional[User]:
        """修改密码"""
        user: User = self.get_by_conditions(db, {'username': username})
        if not user:
            return None
        if not verify_password(old_password, user.hashpwd):  # type:ignore
            return None
        user.hashpwd = get_password_hash(new_password)  # type:ignore
        db.commit()
        return user

    def activate_user(self, db: Session, username: str) -> User:
        """激活用户"""
        user: User = self.get_by_conditions(db, {'username': username})
        user.activated = 1  # type: ignore
        db.commit()
        return user

    def enable_user(self, db: Session, username: str) -> User:
        """启用用户"""
        user: User = self.get_by_conditions(db, {'username': username})
        user.enabled = 1
        db.commit()
        return user

    def disable_user(self, db: Session, username: str) -> User:
        """禁用用户"""
        user: User = self.get_by_conditions(db, {'username': username})
        user.enabled = 0
        db.commit()
        return user

    def lock_user(self, db: Session, username: str) -> User:
        """锁定用户"""
        user: User = self.get_by_conditions(db, {'username': username})
        user.locked = 1
        db.commit()
        return user

    def unlock_user(self, db: Session, username: str) -> User:
        """解锁用户"""
        user: User = self.get_by_conditions(db, {'username': username})
        user.locked = 0
        db.commit()
        return user


userDao: UserDao = UserDao(User)
