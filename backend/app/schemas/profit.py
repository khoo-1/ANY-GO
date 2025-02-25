from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from .base import BaseSchema, PageParams

class ProfitAnalysisBase(BaseSchema):
    """利润分析基础模式"""
    date: date
    type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    
    # 销售数据
    total_orders: int = 0
    total_sales: Decimal = Decimal('0')
    
    # 成本数据
    product_cost: Decimal = Decimal('0')
    shipping_cost: Decimal = Decimal('0')
    operation_cost: Decimal = Decimal('0')
    other_cost: Decimal = Decimal('0')
    total_cost: Decimal = Decimal('0')
    
    # 利润数据
    gross_profit: Decimal = Decimal('0')
    net_profit: Decimal = Decimal('0')
    gross_profit_rate: float = 0
    net_profit_rate: float = 0

class ProfitAnalysisCreate(ProfitAnalysisBase):
    """创建利润分析"""
    pass

class ProfitAnalysisInDB(ProfitAnalysisBase):
    """数据库中的利润分析"""
    id: int

class ProfitAnalysisResponse(ProfitAnalysisInDB):
    """利润分析响应"""
    pass

class ProductProfitBase(BaseSchema):
    """商品利润基础模式"""
    product_id: int
    date: date
    type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    
    # 销售数据
    sales_quantity: int = 0
    sales_amount: Decimal = Decimal('0')
    
    # 成本数据
    unit_cost: Decimal = Decimal('0')
    total_cost: Decimal = Decimal('0')
    shipping_cost: Decimal = Decimal('0')
    
    # 利润数据
    gross_profit: Decimal = Decimal('0')
    net_profit: Decimal = Decimal('0')
    gross_profit_rate: float = 0
    net_profit_rate: float = 0

class ProductProfitCreate(ProductProfitBase):
    """创建商品利润"""
    pass

class ProductProfitInDB(ProductProfitBase):
    """数据库中的商品利润"""
    id: int

class ProductProfitResponse(ProductProfitInDB):
    """商品利润响应"""
    product_sku: str
    product_name: str

class CategoryProfitBase(BaseSchema):
    """品类利润基础模式"""
    category: str
    date: date
    type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    
    # 基础数据
    total_products: int = 0
    total_orders: int = 0
    
    # 销售数据
    sales_quantity: int = 0
    sales_amount: Decimal = Decimal('0')
    
    # 成本数据
    product_cost: Decimal = Decimal('0')
    shipping_cost: Decimal = Decimal('0')
    operation_cost: Decimal = Decimal('0')
    
    # 利润数据
    gross_profit: Decimal = Decimal('0')
    net_profit: Decimal = Decimal('0')
    gross_profit_rate: float = 0
    net_profit_rate: float = 0
    
    # 平均值
    average_order_value: Decimal = Decimal('0')
    average_profit_per_order: Decimal = Decimal('0')

class CategoryProfitCreate(CategoryProfitBase):
    """创建品类利润"""
    pass

class CategoryProfitInDB(CategoryProfitBase):
    """数据库中的品类利润"""
    id: int

class CategoryProfitResponse(CategoryProfitInDB):
    """品类利润响应"""
    pass

class ProfitQuery(PageParams):
    """利润查询参数"""
    type: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ProductProfitQuery(PageParams):
    """商品利润查询参数"""
    product_id: Optional[int] = None
    category: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_profit_rate: Optional[float] = Field(None, ge=0)
    max_profit_rate: Optional[float] = Field(None, le=100)

class CategoryProfitQuery(PageParams):
    """品类利润查询参数"""
    category: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_profit_rate: Optional[float] = Field(None, ge=0)
    max_profit_rate: Optional[float] = Field(None, le=100)

class ProfitSummary(BaseModel):
    """利润汇总"""
    overall_gross_profit: Decimal
    overall_net_profit: Decimal
    overall_gross_profit_rate: float
    overall_net_profit_rate: float
    total_sales: Decimal
    total_cost: Decimal
    profit_trend: List[Dict]  # 利润趋势
    top_profit_products: List[Dict]  # 利润最高的商品
    bottom_profit_products: List[Dict]  # 利润最低的商品
    category_analysis: List[Dict]  # 品类分析 