from sqlalchemy import Column, String, Enum, Float, Integer, JSON, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel
from .product import ProductType
import enum

class PackingListStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"

class BoxSpecs(BaseModel):
    """箱子规格模型"""
    __tablename__ = "box_specs"

    length = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    edge_volume = Column(Float, nullable=False)
    total_pieces = Column(Integer, nullable=False)
    packing_list_id = Column(Integer, ForeignKey("packing_lists.id"))

class PackingListItem(BaseModel):
    """装箱单明细模型"""
    __tablename__ = "packing_list_items"

    packing_list_id = Column(Integer, ForeignKey("packing_lists.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    box_quantities = Column(JSON, nullable=False)  # [{box_no: str, quantity: int}]
    
    # 关联
    product = relationship("Product")

class PackingList(BaseModel):
    """装箱单模型"""
    __tablename__ = "packing_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="draft")  # draft, packed, shipped, delivered
    shipping_method = Column(String)
    tracking_number = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # 关系
    items = relationship("PackingItem", back_populates="packing_list", cascade="all, delete-orphan")
    box_specs = relationship("BoxSpecs", cascade="all, delete-orphan")

    @classmethod
    def extract_store_name(cls, filename: str) -> str:
        """从文件名提取店铺信息"""
        if not filename:
            raise ValueError("文件名不能为空")
            
        # 移除文件扩展名
        name_without_ext = filename.replace(".xlsx", "").replace(".xls", "")
        
        # 检查文件名格式
        suffix = "海运ERP"
        if not name_without_ext.endswith(suffix):
            raise ValueError(f"文件名格式错误，必须以{suffix}结尾")
            
        # 提取店铺名称
        store_name = name_without_ext[:-len(suffix)]
        if not store_name:
            raise ValueError('无法从文件名中提取店铺名称，请确保文件名格式为："{店铺名}海运ERP.xlsx"')
            
        return store_name

class PackingItem(BaseModel):
    """装箱单项目模型"""
    __tablename__ = "packing_items"

    id = Column(Integer, primary_key=True, index=True)
    packing_list_id = Column(Integer, ForeignKey("packing_lists.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    notes = Column(Text)
    
    # 关系
    packing_list = relationship("PackingList", back_populates="items")