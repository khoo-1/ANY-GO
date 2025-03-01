from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class Product(Base):
    """产品模型"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    sku = Column(String(50), unique=True, nullable=False)
    unit = Column(String(20))  # 单位：个、箱、件等
    weight = Column(Float)  # 重量（千克）
    length = Column(Float)  # 长度（厘米）
    width = Column(Float)   # 宽度（厘米）
    height = Column(Float)  # 高度（厘米）
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    creator = relationship("User")