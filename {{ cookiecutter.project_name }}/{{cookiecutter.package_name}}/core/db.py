from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import create_engine, func, Integer, DateTime, Text, String, Column
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from {{cookiecutter.package_name}}.core.settings import config 
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

engine = create_engine(str(config.get('connect_url', 'sqlite:///aaa.db')), echo=bool(config.get('dev', True)))
DBSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
BaseM = declarative_base()

def get_db() -> Session: # type: ignore
    return DBSession() # type: ignore

class BaseEntity(BaseM):
    """基础模型类，包含通用字段和方法"""
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    status = Column(Integer, default=1, comment='状态:1 启用、0 停用、-1 删除')
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, onupdate=func.now(), comment="更新时间")
    created_by = Column(String(32), comment="创建人ID")
    updated_by = Column(String(32), comment="更新人ID")
    remark = Column(Text, comment='描述')

    def to_dict(self):
        """将模型实例转为字典，可选包含关系字段"""
        data = {}
        # 遍历模型所有列
        for col in self.__table__.columns:
            value = getattr(self, col.name)
            # 处理特殊类型
            if isinstance(value, datetime):
                data[col.name] = value.isoformat()  # 转 ISO 8601 字符串
            elif isinstance(value, Decimal):
                data[col.name] = str(value)  # 转字符串避免精度丢失
            else:
                data[col.name] = value

        return data

    def model_update(self, form: BaseModel):
        """根据表单数据更新模型实例"""
        # [col.name for col in org.__table__.columns], '属性',form.model_dump().keys())
        for field, value in form.model_dump().items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)
        return self


class BaseForm(BaseModel):
    """基础表单数据模型"""
    page: int = Field(default=1)
    pageSize: int = Field(default=20)
    status: int | None = Field(default=None)
    remark: str | None = Field(default=None)

# 定义数据访问对象基类
ModelType = TypeVar("ModelType", bound=BaseM)
# 数据访问对象基类
class BaseDao(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, session: Session, id: int) -> Optional[ModelType]:
        '''
        根据id查询数据
        :param id: 数据id
        :return: 数据对象
        '''
        return session.get(self.model, id)
    
    def list_all(self, session: Session) -> List[ModelType]:
        '''
        查询所有数据
        :return: 数据列表
        '''
        return session.query(self.model).all()
    
    def create(self, session: Session, **kwargs) -> ModelType:
        '''
        创建数据
        :param kwargs: 数据字段及值
        :param model: 数据对象
        :return: 数据对象
        '''
        model = self.model(**kwargs)
        session.add(model)
        session.commit()
        session.refresh(model)
        return model
    
    def update(self, session: Session, model: ModelType, **kwargs) -> ModelType:
        '''
        更新数据
        :param kwargs: 数据字段及值
        :param model: 数据对象
        :return: 数据对象
        '''

        for key, value in kwargs.items():
            setattr(model, key, value)
        session.commit()
        session.refresh(model)
        return model
    
    def delete(self, session: Session, model: ModelType) -> None:
        session.delete(model)
        session.commit()
        
    def list_paginated(
        self,
        session: Session,
        page: int,          # 当前页码（从1开始）
        limit: int,         # 每页数量
        sort_by: Optional[str] = None,  # 排序字段（如 "age"）
        order: str = "asc", # 排序顺序（"asc"/"desc"）
        conditions: Optional[Union[Dict[str, Any], Any]] = None  # 查询条件（字典或 SQLAlchemy 表达式）
    ) -> Dict[str, Any]:
        """
        分页查询：返回数据列表 + 分页元信息
        :param conditions: 支持两种形式：
            1. 字典（简化条件）：{"username": "zhangsan", "age_gt": 25}（"age_gt" 表示 age > 25）
            2. SQLAlchemy 表达式：User.username == "zhangsan" & User.age > 25（更灵活）
        """
        # 1. 计算偏移量
        offset = (page - 1) * limit
        
        # 2. 构建基础查询
        query = session.query(self.model)
        
        # 3. 应用条件过滤
        if conditions:
            query = self._apply_conditions(query, conditions)
        
        # 4. 应用排序
        if sort_by:
            sort_expr = getattr(self.model, sort_by)
            if order.lower() == "desc":
                sort_expr = sort_expr.desc()
            query = query.order_by(sort_expr)
        
        # 5. 执行分页查询
        items = query.offset(offset).limit(limit).all()
        
        # 6. 查询总记录数（用于计算分页元信息）
        total_count = session.query(func.count(self.model.id)).scalar()
        
        # 7. 组装分页结果
        return {
            "data": items,
            "pagination": {
                "current_page": page,
                "page_size": limit,
                "total_items": total_count,
                "total_pages": (total_count + limit - 1) // limit,  # 向上取整
                "has_next": page < (total_count + limit - 1) // limit,
                "has_prev": page > 1
            }
        }

    def list_by_conditions(
        self,
        session: Session,
        conditions: Optional[Union[Dict[str, Any], Any]] = None,
        sort_by: Optional[str] = None,
        order: str = "asc"
    ) -> List[ModelType]:
        """根据条件查询列表（无分页）"""
        query = session.query(self.model)
        if conditions:
            query = self._apply_conditions(query, conditions)
        if sort_by:
            sort_expr = getattr(self.model, sort_by)
            if order.lower() == "desc":
                sort_expr = sort_expr.desc()
            query = query.order_by(sort_expr)
        return query.all()

    def get_by_conditions(
        self,
        session: Session,
        conditions: Optional[Union[Dict[str, Any], Any]] = None
    ) -> Optional[ModelType]:
        """根据条件查询单个实例（不存在返回 None）"""
        query = session.query(self.model)
        if conditions:
            query = self._apply_conditions(query, conditions)
        return query.first()


    def count_by_conditions(
        self,
        session: Session,
        conditions: Optional[Union[Dict[str, Any], Any]] = None
    ) -> int:
        """统计符合条件的记录数"""
        query = session.query(func.count(self.model.id))
        if conditions:
            query = self._apply_conditions(query, conditions)
        return query.scalar()

    # ------------------------------
    # 内部工具方法：统一处理条件（字典转 SQLAlchemy 表达式）
    # ------------------------------
    def _apply_conditions(
        self,
        query: Any,
        conditions: Union[Dict[str, Any], Any]
    ) -> Any:
        """将字典条件转换为 SQLAlchemy 过滤表达式，或直接使用 SQLAlchemy 表达式"""
        if isinstance(conditions, dict):
            # 处理字典中的条件（支持运算符，如 "age_gt" → age > value）
            for key, value in conditions.items():
                if "_" in key:
                    # 拆分字段名与运算符（如 "age_gt" → field=age, op=gt）
                    field_name, op = key.rsplit("_", 1)
                    field = getattr(self.model, field_name)
                    # 根据运算符构建过滤条件
                    if op == "gt":
                        query = query.filter(field > value)
                    elif op == "lt":
                        query = query.filter(field < value)
                    elif op == "gte":
                        query = query.filter(field >= value)
                    elif op == "lte":
                        query = query.filter(field <= value)
                    elif op == "eq":
                        query = query.filter(field == value)
                    elif op == "ne":
                        query = query.filter(field != value)
                    elif op == "like":
                        query = query.filter(field.like(f"%{value}%"))  # 模糊匹配
                    else:
                        raise ValueError(f"不支持的运算符: {op}")
                else:
                    # 直接等于（如 "username" → username == value）
                    query = query.filter(getattr(self.model, key) == value)
        else:
            # 直接使用 SQLAlchemy 表达式（如 User.age > 25）
            query = query.filter(conditions)
        return query  