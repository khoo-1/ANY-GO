from sqlalchemy import Column, String, Enum, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class StockOperationType(str, enum.Enum):
    """库存操作类型"""
    IN = "入库"
    OUT = "出库"
    ADJUST = "调整"
    CHECK = "盘点"

class StockRecord(BaseModel):
    """库存变动记录"""
    __tablename__ = "stock_records"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    operation_type = Column(Enum(StockOperationType), nullable=False)
    quantity = Column(Integer, nullable=False)  # 变动数量，正数为增加，负数为减少
    previous_stock = Column(Integer, nullable=False)  # 变动前库存
    current_stock = Column(Integer, nullable=False)  # 变动后库存
    unit_price = Column(Float, nullable=True)  # 单价
    total_amount = Column(Float, nullable=True)  # 总金额
    batch_number = Column(String, nullable=True)  # 批次号
    warehouse = Column(String, nullable=True)  # 仓库
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    remark = Column(String, nullable=True)  # 备注
    related_order = Column(String, nullable=True)  # 关联订单号
    attachment = Column(String, nullable=True)  # 附件
    details = Column(JSON, nullable=True)  # 其他详细信息

    # 关联
    product = relationship("Product", backref="stock_records")
    operator = relationship("User", backref="stock_operations")

class StockCheck(BaseModel):
    """库存盘点记录"""
    __tablename__ = "stock_checks"

    check_no = Column(String, unique=True, nullable=False)  # 盘点单号
    warehouse = Column(String, nullable=True)  # 仓库
    status = Column(String, default="pending")  # 状态：pending-待盘点，in_progress-盘点中，completed-已完成
    start_time = Column(String, nullable=True)  # 开始时间
    end_time = Column(String, nullable=True)  # 结束时间
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checker_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 审核人
    remark = Column(String, nullable=True)  # 备注
    attachment = Column(String, nullable=True)  # 附件

    # 关联
    operator = relationship("User", foreign_keys=[operator_id], backref="stock_checks")
    checker = relationship("User", foreign_keys=[checker_id], backref="checked_stocks")

class StockCheckItem(BaseModel):
    """库存盘点明细"""
    __tablename__ = "stock_check_items"

    check_id = Column(Integer, ForeignKey("stock_checks.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    system_stock = Column(Integer, nullable=False)  # 系统库存
    actual_stock = Column(Integer, nullable=False)  # 实际库存
    difference = Column(Integer, nullable=False)  # 差异数量
    unit_price = Column(Float, nullable=True)  # 单价
    total_amount = Column(Float, nullable=True)  # 差异金额
    remark = Column(String, nullable=True)  # 备注

    # 关联
    stock_check = relationship("StockCheck", backref="items")
    product = relationship("Product")

class StockAlert(BaseModel):
    """库存预警记录"""
    __tablename__ = "stock_alerts"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    alert_type = Column(String, nullable=False)  # low-库存不足，high-库存积压
    threshold = Column(Integer, nullable=False)  # 预警阈值
    current_stock = Column(Integer, nullable=False)  # 当前库存
    status = Column(String, default="active")  # 状态：active-活动，resolved-已解决
    resolved_time = Column(String, nullable=True)  # 解决时间
    resolver_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 处理人
    remark = Column(String, nullable=True)  # 备注

    # 关联
    product = relationship("Product", backref="stock_alerts")
    resolver = relationship("User", backref="resolved_alerts") 