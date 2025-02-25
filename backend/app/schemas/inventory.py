from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from .base import BaseSchema, PageParams

class InventoryAnalysisBase(BaseSchema):
    """库存分析基础模式"""
    date: date
    type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    total_products: int = 0
    total_quantity: int = 0
    total_value: Decimal = Decimal('0')
    turnover_rate: float = 0
    turnover_days: float = 0
    average_inventory: Decimal = Decimal('0')
    inventory_cost: Decimal = Decimal('0')
    active_products: int = 0
    inactive_products: int = 0
    stockout_products: int = 0
    overstock_products: int = 0
    healthy_stock_ratio: float = 0
    stockout_ratio: float = 0
    overstock_ratio: float = 0

class InventoryAnalysisCreate(InventoryAnalysisBase):
    """创建库存分析"""
    pass

class InventoryAnalysisInDB(InventoryAnalysisBase):
    """数据库中的库存分析"""
    id: int

class InventoryAnalysisResponse(InventoryAnalysisInDB):
    """库存分析响应"""
    pass

class ProductTurnoverBase(BaseSchema):
    """商品周转基础模式"""
    product_id: int
    date: date
    type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    beginning_stock: int = 0
    ending_stock: int = 0
    average_stock: float = 0
    sales_quantity: int = 0
    sales_amount: Decimal = Decimal('0')
    turnover_rate: float = 0
    turnover_days: float = 0
    stock_status: Optional[str] = None

class ProductTurnoverCreate(ProductTurnoverBase):
    """创建商品周转"""
    pass

class ProductTurnoverInDB(ProductTurnoverBase):
    """数据库中的商品周转"""
    id: int

class ProductTurnoverResponse(ProductTurnoverInDB):
    """商品周转响应"""
    product_sku: str
    product_name: str

class CategoryTurnoverBase(BaseSchema):
    """品类周转基础模式"""
    category: str
    date: date
    type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    total_products: int = 0
    total_stock: int = 0
    total_value: Decimal = Decimal('0')
    sales_quantity: int = 0
    sales_amount: Decimal = Decimal('0')
    turnover_rate: float = 0
    turnover_days: float = 0
    active_products: int = 0
    inactive_products: int = 0
    stockout_products: int = 0
    overstock_products: int = 0

class CategoryTurnoverCreate(CategoryTurnoverBase):
    """创建品类周转"""
    pass

class CategoryTurnoverInDB(CategoryTurnoverBase):
    """数据库中的品类周转"""
    id: int

class CategoryTurnoverResponse(CategoryTurnoverInDB):
    """品类周转响应"""
    pass

class InventoryQuery(PageParams):
    """库存查询参数"""
    type: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ProductTurnoverQuery(PageParams):
    """商品周转查询参数"""
    product_id: Optional[int] = None
    category: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    stock_status: Optional[str] = None

class CategoryTurnoverQuery(PageParams):
    """品类周转查询参数"""
    category: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class TurnoverSummary(BaseModel):
    """周转汇总"""
    overall_turnover_rate: float
    overall_turnover_days: float
    total_inventory_value: Decimal
    total_sales_amount: Decimal
    inventory_health: Dict[str, float]  # 库存健康度指标
    top_turnover_products: List[Dict]  # 周转率最高的商品
    bottom_turnover_products: List[Dict]  # 周转率最低的商品
    category_analysis: List[Dict]  # 品类分析 