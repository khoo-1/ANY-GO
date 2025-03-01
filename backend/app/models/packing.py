from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class PackingList(Base):
    """打包清单模型"""
    __tablename__ = "packing_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    status = Column(String(20), default="draft")  # draft, in_progress, completed, cancelled
    created_by = Column(Integer, ForeignKey("users.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    items = relationship("PackingItem", back_populates="packing_list", cascade="all, delete-orphan")
    box_specs = relationship("BoxSpecs", back_populates="packing_list", uselist=False, cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_packing_lists")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_packing_lists")

class PackingItem(Base):
    """打包项目模型"""
    __tablename__ = "packing_items"

    id = Column(Integer, primary_key=True, index=True)
    packing_list_id = Column(Integer, ForeignKey("packing_lists.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    notes = Column(String(500))
    is_packed = Column(Boolean, default=False)
    box_quantities = Column(JSON)  # 存储每个箱子的数量，格式：{"box1": 10, "box2": 5}
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    packing_list = relationship("PackingList", back_populates="items")
    product = relationship("Product")

class BoxSpecs(Base):
    """箱子规格模型"""
    __tablename__ = "box_specs"

    id = Column(Integer, primary_key=True, index=True)
    packing_list_id = Column(Integer, ForeignKey("packing_lists.id"))
    length = Column(Float, nullable=False)  # 长度（厘米）
    width = Column(Float, nullable=False)   # 宽度（厘米）
    height = Column(Float, nullable=False)  # 高度（厘米）
    weight = Column(Float, nullable=False)  # 重量（千克）
    volume = Column(Float, nullable=False)  # 体积（立方厘米）
    edge_volume = Column(Float, nullable=False)  # 边缘体积（立方厘米）
    total_pieces = Column(Integer, nullable=False)  # 总件数
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    packing_list = relationship("PackingList", back_populates="box_specs") 