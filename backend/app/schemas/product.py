from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from .base import BaseSchema, PageParams

class ProductBase(BaseSchema):
    """产品基础模式"""
    sku: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    chinese_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: str = Field(default="未分类", max_length=50)
    type: str = Field(..., pattern="^(普货|纺织|混装)$")
    
    # 价格信息
    price: Decimal = Field(default=0, ge=0)
    cost: Decimal = Field(default=0, ge=0)
    freight_cost: Decimal = Field(default=0, ge=0)
    
    # 库存信息
    stock: int = Field(default=0, ge=0)
    alert_threshold: int = Field(default=10, ge=0)
    
    # 其他信息
    supplier: Optional[str] = None
    images: List[str] = []
    status: str = Field(default="active", pattern="^(active|inactive)$")
    
    @validator("sku")
    def validate_sku(cls, v):
        """验证SKU格式"""
        if not v.strip():
            raise ValueError("SKU不能为空")
        return v.strip().upper()

class ProductCreate(ProductBase):
    """创建产品"""
    is_auto_created: bool = False
    needs_completion: bool = False

class ProductUpdate(BaseSchema):
    """更新产品"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    chinese_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    type: Optional[str] = Field(None, pattern="^(普货|纺织|混装)$")
    price: Optional[Decimal] = Field(None, ge=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    freight_cost: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    alert_threshold: Optional[int] = Field(None, ge=0)
    supplier: Optional[str] = None
    images: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    needs_completion: Optional[bool] = None

class ProductInDB(ProductBase):
    """数据库中的产品"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_auto_created: bool
    needs_completion: bool

class ProductResponse(ProductBase):
    """产品响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_auto_created: bool
    needs_completion: bool

    @property
    def total_cost(self) -> Decimal:
        """计算总成本"""
        return self.cost + self.freight_cost

class ProductQuery(PageParams):
    """产品查询参数"""
    keyword: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(普货|纺织|混装)$")
    category: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    show_auto_created: Optional[bool] = None
    needs_completion: Optional[bool] = None
    min_stock: Optional[int] = Field(None, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)

class BatchCreateProduct(BaseModel):
    """批量创建产品"""
    products: List[ProductCreate]

class BatchDeleteProduct(BaseModel):
    """批量删除产品"""
    ids: List[int]

class UpdateStockRequest(BaseModel):
    """更新库存请求"""
    quantity: int
    type: str = Field(..., pattern="^(入库|出库|调整)$")
    reason: Optional[str] = None

class ProductExportRequest(BaseModel):
    """产品导出请求"""
    keyword: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(普货|纺织|混装)$")
    category: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    in_stock: Optional[bool] = None
    fields: Optional[List[str]] = None

    @validator('fields')
    def validate_fields(cls, v):
        if v:
            valid_fields = {
                "sku", "name", "chinese_name", "type", "category",
                "price", "cost", "stock", "alert_threshold",
                "supplier", "status"
            }
            invalid_fields = set(v) - valid_fields
            if invalid_fields:
                raise ValueError(f"无效的字段: {', '.join(invalid_fields)}")
        return v

class ProductListResponse(BaseModel):
    """产品列表响应"""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """计算总页数"""
        return (self.total + self.page_size - 1) // self.page_size 