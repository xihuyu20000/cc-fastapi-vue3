from sqlalchemy import Column, Integer, String

from {{cookiecutter.package_name}}.core.db import BaseDao, BaseEntity


class Res(BaseEntity):
    __tablename__ = "sys_res"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    pid = Column(Integer, default=0, nullable=True)
    name = Column(String(50), unique=True, nullable=False, index=True)


class ResDao(BaseDao[Res]):
    model = Res


resDao: ResDao = ResDao(Res)
