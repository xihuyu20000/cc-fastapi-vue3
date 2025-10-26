from sqlalchemy import Column, Integer, String

from {{cookiecutter.package_name}}.core.db import BaseDao, BaseEntity


class Org(BaseEntity):
    __tablename__ = "sys_org"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    pid = Column(Integer, default=0, nullable=True)
    name = Column(String(50), unique=True, nullable=False, index=True)


class OrgDao(BaseDao[Org]):
    model = Org


orgDao: OrgDao = OrgDao(Org)
