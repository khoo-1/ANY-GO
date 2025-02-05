from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from .base import BaseSchema, PageParams
from .product import ProductResponse

class BoxQuantity(BaseModel):
    """箱子数量"""
    box_no: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    specs: Optional[str] = None

class BoxSpecs(BaseSchema):
    """箱子规格"""
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    volume: float = Field(..., gt=0)
    edge_volume: float = Field(..., gt=0)
    total_pieces: int = Field(..., gt=0)

class PackingListItemBase(BaseSchema):
    """装箱单明细基础模式"""
    product_id: int
    quantity: int = Field(..., gt=0)
    box_quantities: List[BoxQuantity]

class PackingListItem(PackingListItemBase):
    """装箱单明细"""
    id: int
    product: ProductResponse
    weight: float
    volume: float

class PackingListBase(BaseSchema):
    """装箱单基础模式"""
    store_name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(普货|纺织|混装)$")
    remarks: Optional[str] = None

class PackingListCreate(PackingListBase):
    """创建装箱单"""
    items: List[PackingListItemBase]
    box_specs: List[BoxSpecs]

class PackingListUpdate(BaseSchema):
    """更新装箱单"""
    store_name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, pattern="^(普货|纺织|混装)$")
    status: Optional[str] = Field(None, pattern="^(pending|approved)$")
    remarks: Optional[str] = None
    items: Optional[List[PackingListItemBase]] = None
    box_specs: Optional[List[BoxSpecs]] = None

class PackingListInDB(PackingListBase):
    """数据库中的装箱单"""
    id: int
    status: str = Field(default="pending", pattern="^(pending|approved)$")
    total_boxes: int
    total_weight: float
    total_volume: float
    total_pieces: int
    total_value: float
    created_at: datetime
    updated_at: datetime

class PackingListResponse(PackingListInDB):
    """装箱单响应"""
    items: List[PackingListItem]
    box_specs: List[BoxSpecs]

class PackingListQuery(PageParams):
    """装箱单查询参数"""
    keyword: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(普货|纺织|混装)$")
    status: Optional[str] = Field(None, pattern="^(pending|approved)$")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ImportResult(BaseModel):
    """导入结果"""
    success: bool
    message: str
    total: int = 0
    created: int = 0
    updated: int = 0
    failed: int = 0
    errors: List[str] = []

class ExportRequest(BaseModel):
    """导出请求"""
    ids: List[int]
    include_box_specs: bool = True
    include_product_details: bool = True

class BatchApproveRequest(BaseModel):
    """批量审批请求"""
    ids: List[int]
    action: str = Field(..., pattern="^(approve|reject)$")
    reason: Optional[str] = None

class StoreStatistics(BaseModel):
    """店铺统计"""
    store_name: str
    total_lists: int
    total_products: int
    total_pieces: int
    total_boxes: int
    total_value: float 