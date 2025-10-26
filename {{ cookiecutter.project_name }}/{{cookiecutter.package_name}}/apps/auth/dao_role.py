from sqlalchemy import Column, Integer, String

from {{cookiecutter.package_name}}.core.db import BaseDao, BaseEntity


class Role(BaseEntity):
    __tablename__ = "sys_role"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)


class RoleDao(BaseDao[Role]):
    model = Role


roleDao: RoleDao = RoleDao(Role)
