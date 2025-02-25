from typing import Optional, List
from pydantic import BaseModel, Field, validator, confloat
from datetime import datetime
from decimal import Decimal
from .base import BaseSchema, PageParams
from .product import ProductResponse

class BoxQuantity(BaseModel):
    """箱子数量"""
    box_no: str = Field(..., min_length=1, max_length=20, description="箱号")
    quantity: int = Field(..., gt=0, description="数量")
    specs: Optional[str] = Field(None, max_length=100, description="规格说明")

    @validator('box_no')
    def validate_box_no(cls, v):
        if not v.strip():
            raise ValueError('箱号不能为空')
        return v.strip()

class BoxSpecs(BaseSchema):
    """箱子规格"""
    length: confloat(gt=0) = Field(..., description="长度(cm)")
    width: confloat(gt=0) = Field(..., description="宽度(cm)")
    height: confloat(gt=0) = Field(..., description="高度(cm)")
    weight: confloat(gt=0) = Field(..., description="重量(kg)")
    volume: confloat(gt=0) = Field(..., description="体积(m³)")
    edge_volume: confloat(gt=0) = Field(..., description="边体积(m³)")
    total_pieces: int = Field(..., gt=0, description="总件数")

    @validator('volume')
    def validate_volume(cls, v, values):
        """验证体积计算是否正确"""
        if 'length' in values and 'width' in values and 'height' in values:
            calculated_volume = values['length'] * values['width'] * values['height'] / 1000000  # 转换为立方米
            if abs(v - calculated_volume) > 0.0001:  # 允许0.0001的误差
                raise ValueError('体积计算不正确')
        return v

    @validator('edge_volume')
    def validate_edge_volume(cls, v, values):
        """验证边体积必须大于等于实际体积"""
        if 'volume' in values and v < values['volume']:
            raise ValueError('边体积必须大于等于实际体积')
        return v

class PackingListItemBase(BaseSchema):
    """装箱单明细基础模式"""
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(..., gt=0, description="数量")
    box_quantities: List[BoxQuantity] = Field(..., min_items=1, description="装箱数量")

    @validator('box_quantities')
    def validate_box_quantities(cls, v, values):
        """验证装箱数量总和是否等于商品总数量"""
        if 'quantity' in values:
            total = sum(box.quantity for box in v)
            if total != values['quantity']:
                raise ValueError('装箱数量总和必须等于商品总数量')
        return v

class PackingListItem(PackingListItemBase):
    """装箱单明细"""
    id: int
    product: ProductResponse
    weight: float
    volume: float

class PackingListBase(BaseSchema):
    """装箱单基础模式"""
    store_name: str = Field(..., min_length=2, max_length=50, description="店铺名称")
    type: str = Field(..., pattern="^(普货|纺织|混装)$", description="类型")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")

class PackingListCreate(PackingListBase):
    """创建装箱单"""
    items: List[PackingListItemBase] = Field(..., min_items=1, description="商品明细")
    box_specs: List[BoxSpecs] = Field(..., min_items=1, description="箱子规格")

    @validator('items')
    def validate_items(cls, v):
        """验证商品明细不能为空"""
        if not v:
            raise ValueError('商品明细不能为空')
        return v

    @validator('box_specs')
    def validate_box_specs(cls, v):
        """验证箱子规格不能为空"""
        if not v:
            raise ValueError('箱子规格不能为空')
        return v

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