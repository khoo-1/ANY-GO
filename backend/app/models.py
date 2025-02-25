from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv
from .database import Base

# 加载环境变量
load_dotenv()

# 检查数据库类型
database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
is_sqlite = database_url.startswith("sqlite")

# 根据数据库类型选择JSON类型
if is_sqlite:
    from sqlalchemy import String as SQLiteString
    JSONType = JSON().with_variant(SQLiteString, "sqlite")
else:
    JSONType = JSON

# 用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String)
    permissions = Column(JSONType)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sku = Column(String, unique=True, index=True)
    description = Column(Text)
    price = Column(Float)
    cost = Column(Float)
    weight = Column(Float, nullable=True)
    stock = Column(Integer, default=0)
    category = Column(String, nullable=True)
    supplier = Column(String, nullable=True)
    tags = Column(JSONType, default=list)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联库存表
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    # 关联装箱单明细
    packing_list_items = relationship("PackingListItem", back_populates="product")

class Inventory(Base):
    """库存表"""
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=0)
    min_quantity = Column(Integer, default=0)  # 最小库存量
    max_quantity = Column(Integer)  # 最大库存量
    last_restock_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联产品表
    product = relationship("Product", back_populates="inventory")

class PackingList(Base):
    __tablename__ = "packing_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="draft")  # draft, in_progress, completed, cancelled
    created_by = Column(Integer, ForeignKey("users.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    items = relationship("PackingListItem", back_populates="packing_list", cascade="all, delete-orphan")

class PackingListItem(Base):
    __tablename__ = "packing_list_items"

    id = Column(Integer, primary_key=True, index=True)
    packing_list_id = Column(Integer, ForeignKey("packing_lists.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    is_packed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    packing_list = relationship("PackingList", back_populates="items")
    product = relationship("Product", back_populates="packing_list_items")