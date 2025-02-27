from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
import enum

from app.database import Base

# 添加缺失的枚举类
class ProductType(enum.Enum):
    """产品类型枚举"""
    PHYSICAL = "physical"  # 实物产品
    DIGITAL = "digital"    # 数字产品
    SERVICE = "service"    # 服务类产品

class ProductStatus(enum.Enum):
    """产品状态枚举"""
    ACTIVE = "active"        # 活跃
    INACTIVE = "inactive"    # 非活跃
    DRAFT = "draft"          # 草稿
    ARCHIVED = "archived"    # 已归档

class Product(Base):
    """产品模型"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    sku = Column(String, unique=True, index=True)
    price = Column(Float)
    weight = Column(Float)
    dimensions = Column(String)
    category = Column(String, index=True)
    tags = Column(String)  # 逗号分隔的标签列表
    # 添加类型和状态字段
    type = Column(Enum(ProductType), default=ProductType.PHYSICAL)
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))