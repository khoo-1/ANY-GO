from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from decimal import Decimal
from .base import BaseSchema, PageParams

class OrderItemBase(BaseSchema):
    """订单明细基础模式"""
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    tax: Optional[Decimal] = Field(0, ge=0)
    discount: Optional[Decimal] = Field(0, ge=0)
    specifications: Optional[Dict] = None

class OrderItemCreate(OrderItemBase):
    """创建订单明细"""
    pass

class OrderItemUpdate(BaseSchema):
    """更新订单明细"""
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    tax: Optional[Decimal] = Field(None, ge=0)
    discount: Optional[Decimal] = Field(None, ge=0)

class OrderItemInDB(OrderItemBase):
    """数据库中的订单明细"""
    id: int
    order_id: int
    subtotal: Decimal
    total: Decimal
    sku: str
    product_name: str
    created_at: datetime
    updated_at: datetime

class OrderBase(BaseSchema):
    """订单基础模式"""
    store_name: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., min_length=1, max_length=50)
    order_date: date
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    shipping_address: Optional[Dict] = None
    shipping_fee: Optional[Decimal] = Field(0, ge=0)
    tax: Optional[Decimal] = Field(0, ge=0)
    discount: Optional[Decimal] = Field(0, ge=0)
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    """创建订单"""
    items: List[OrderItemCreate]

class OrderUpdate(BaseSchema):
    """更新订单"""
    status: Optional[str] = Field(None, pattern="^(pending|processing|shipped|completed|cancelled)$")
    payment_status: Optional[str] = Field(None, pattern="^(unpaid|paid|refunded)$")
    tracking_no: Optional[str] = None
    carrier: Optional[str] = None
    shipping_date: Optional[date] = None
    notes: Optional[str] = None

class OrderInDB(OrderBase):
    """数据库中的订单"""
    id: int
    order_no: str
    status: str
    payment_status: str
    subtotal: Decimal
    total: Decimal
    tracking_no: Optional[str] = None
    carrier: Optional[str] = None
    shipping_date: Optional[date] = None
    operator_id: int
    created_at: datetime
    updated_at: datetime

class OrderResponse(OrderInDB):
    """订单响应"""
    items: List[OrderItemInDB]
    operator_name: str

class OrderQuery(PageParams):
    """订单查询参数"""
    keyword: Optional[str] = None
    store_name: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|processing|shipped|completed|cancelled)$")
    payment_status: Optional[str] = Field(None, pattern="^(unpaid|paid|refunded)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    operator_id: Optional[int] = None

class SalesStatisticsBase(BaseSchema):
    """销售统计基础模式"""
    date: date
    store_name: str
    platform: str
    order_count: int = 0
    completed_order_count: int = 0
    cancelled_order_count: int = 0
    total_sales: Decimal = Decimal('0')
    total_cost: Decimal = Decimal('0')
    gross_profit: Decimal = Decimal('0')
    shipping_fee: Decimal = Decimal('0')
    tax: Decimal = Decimal('0')
    discount: Decimal = Decimal('0')
    total_items: int = 0
    unique_items: int = 0
    average_order_value: Decimal = Decimal('0')
    conversion_rate: Decimal = Decimal('0')

class SalesStatisticsCreate(SalesStatisticsBase):
    """创建销售统计"""
    pass

class SalesStatisticsUpdate(BaseSchema):
    """更新销售统计"""
    order_count: Optional[int] = None
    completed_order_count: Optional[int] = None
    cancelled_order_count: Optional[int] = None
    total_sales: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    gross_profit: Optional[Decimal] = None
    shipping_fee: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    total_items: Optional[int] = None
    unique_items: Optional[int] = None
    average_order_value: Optional[Decimal] = None
    conversion_rate: Optional[Decimal] = None

class SalesStatisticsInDB(SalesStatisticsBase):
    """数据库中的销售统计"""
    id: int
    created_at: datetime
    updated_at: datetime

class SalesStatisticsResponse(SalesStatisticsInDB):
    """销售统计响应"""
    pass

class SalesQuery(PageParams):
    """销售查询参数"""
    store_name: Optional[str] = None
    platform: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class SalesSummary(BaseModel):
    """销售汇总"""
    total_orders: int
    total_sales: Decimal
    total_profit: Decimal
    average_order_value: Decimal
    conversion_rate: Decimal
    top_products: List[Dict]
    top_stores: List[Dict] 