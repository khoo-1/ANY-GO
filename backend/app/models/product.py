from sqlalchemy import Column, String, Enum, Float, Integer, Boolean, JSON
from .base import BaseModel
import enum

class ProductType(str, enum.Enum):
    NORMAL = "普货"
    TEXTILE = "纺织"
    MIXED = "混装"

class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Product(BaseModel):
    """产品模型"""
    __tablename__ = "products"

    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    chinese_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    category = Column(String, default="未分类")
    type = Column(Enum(ProductType), nullable=False)
    
    # 价格信息
    price = Column(Float, nullable=False, default=0)
    cost = Column(Float, nullable=False, default=0)
    freight_cost = Column(Float, nullable=False, default=0)
    
    # 库存信息
    stock = Column(Integer, nullable=False, default=0)
    alert_threshold = Column(Integer, nullable=False, default=10)
    
    # 其他信息
    supplier = Column(String, nullable=True)
    images = Column(JSON, nullable=False, default=list)
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE)
    
    # 自动创建标记
    is_auto_created = Column(Boolean, default=False)
    needs_completion = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Product {self.sku}>"