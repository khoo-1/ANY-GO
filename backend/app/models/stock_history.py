from sqlalchemy import Column, String, Integer, Enum, Text, ForeignKey, DateTime
from .base import BaseModel
import enum
from datetime import datetime

class StockOperationType(str, enum.Enum):
    PURCHASE = "purchase"  # 采购入库
    SALES = "sales"       # 销售出库
    RETURN = "return"     # 退货入库
    ADJUSTMENT = "adjustment"  # 库存调整
    PACKING = "packing"   # 装箱出库
    INVENTORY = "inventory"  # 盘点调整

class StockHistory(BaseModel):
    """库存历史记录模型"""
    __tablename__ = "stock_history"

    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    operation_type = Column(Enum(StockOperationType), nullable=False)
    quantity_change = Column(Integer, nullable=False)  # 正数表示增加，负数表示减少
    previous_quantity = Column(Integer, nullable=False)  # 变动前数量
    current_quantity = Column(Integer, nullable=False)   # 变动后数量
    reference_number = Column(String)  # 关联单据编号（如装箱单号、采购单号等）
    operation_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    operator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    notes = Column(Text)
    location = Column(String)  # 库位信息
    batch_number = Column(String)  # 批次号