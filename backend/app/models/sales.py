from sqlalchemy import Column, String, Enum, Float, Integer, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    SHIPPED = "shipped"  # 已发货
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

class PaymentStatus(str, enum.Enum):
    """支付状态"""
    UNPAID = "unpaid"  # 未支付
    PAID = "paid"  # 已支付
    REFUNDED = "refunded"  # 已退款

class Order(BaseModel):
    """订单"""
    __tablename__ = "orders"

    order_no = Column(String, unique=True, nullable=False)  # 订单编号
    store_name = Column(String, nullable=False)  # 店铺名称
    platform = Column(String, nullable=False)  # 平台
    order_date = Column(Date, nullable=False)  # 订单日期
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)  # 订单状态
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)  # 支付状态
    
    # 金额相关
    subtotal = Column(Float, nullable=False)  # 商品小计
    shipping_fee = Column(Float, default=0)  # 运费
    tax = Column(Float, default=0)  # 税费
    discount = Column(Float, default=0)  # 折扣
    total = Column(Float, nullable=False)  # 总金额
    
    # 客户信息
    customer_name = Column(String, nullable=True)  # 客户姓名
    customer_email = Column(String, nullable=True)  # 客户邮箱
    shipping_address = Column(JSON, nullable=True)  # 收货地址
    
    # 物流信息
    tracking_no = Column(String, nullable=True)  # 物流单号
    carrier = Column(String, nullable=True)  # 承运商
    shipping_date = Column(Date, nullable=True)  # 发货日期
    
    # 其他信息
    notes = Column(String, nullable=True)  # 备注
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 操作员
    
    # 关联
    operator = relationship("User", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(BaseModel):
    """订单明细"""
    __tablename__ = "order_items"

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)  # 数量
    unit_price = Column(Float, nullable=False)  # 单价
    subtotal = Column(Float, nullable=False)  # 小计
    tax = Column(Float, default=0)  # 税费
    discount = Column(Float, default=0)  # 折扣
    total = Column(Float, nullable=False)  # 总金额
    
    # SKU信息快照
    sku = Column(String, nullable=False)  # SKU
    product_name = Column(String, nullable=False)  # 商品名称
    specifications = Column(JSON, nullable=True)  # 规格信息
    
    # 关联
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class SalesStatistics(BaseModel):
    """销售统计"""
    __tablename__ = "sales_statistics"

    date = Column(Date, nullable=False, index=True)  # 统计日期
    store_name = Column(String, nullable=False)  # 店铺名称
    platform = Column(String, nullable=False)  # 平台
    
    # 订单统计
    order_count = Column(Integer, default=0)  # 订单数
    completed_order_count = Column(Integer, default=0)  # 完成订单数
    cancelled_order_count = Column(Integer, default=0)  # 取消订单数
    
    # 金额统计
    total_sales = Column(Float, default=0)  # 销售总额
    total_cost = Column(Float, default=0)  # 成本总额
    gross_profit = Column(Float, default=0)  # 毛利润
    shipping_fee = Column(Float, default=0)  # 运费总额
    tax = Column(Float, default=0)  # 税费总额
    discount = Column(Float, default=0)  # 折扣总额
    
    # 商品统计
    total_items = Column(Integer, default=0)  # 商品总数
    unique_items = Column(Integer, default=0)  # 不同商品数
    
    # 其他统计
    average_order_value = Column(Float, default=0)  # 平均订单金额
    conversion_rate = Column(Float, default=0)  # 转化率
    
    class Config:
        unique_together = [("date", "store_name", "platform")] 