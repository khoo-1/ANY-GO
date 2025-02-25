from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal
from .base import BaseSchema, PageParams

class StockRecordBase(BaseSchema):
    """库存记录基础模式"""
    product_id: int
    operation_type: str = Field(..., pattern="^(入库|出库|调整|盘点)$")
    quantity: int
    unit_price: Optional[float] = None
    batch_number: Optional[str] = None
    warehouse: Optional[str] = None
    remark: Optional[str] = None
    related_order: Optional[str] = None
    attachment: Optional[str] = None
    details: Optional[dict] = None

class StockRecordCreate(StockRecordBase):
    """创建库存记录"""
    pass

class StockRecordUpdate(BaseSchema):
    """更新库存记录"""
    remark: Optional[str] = None
    attachment: Optional[str] = None
    details: Optional[dict] = None

class StockRecordInDB(StockRecordBase):
    """数据库中的库存记录"""
    id: int
    previous_stock: int
    current_stock: int
    total_amount: Optional[float] = None
    operator_id: int
    created_at: datetime
    updated_at: datetime

class StockRecordResponse(StockRecordInDB):
    """库存记录响应"""
    product_sku: str
    product_name: str
    operator_name: str

class StockCheckBase(BaseSchema):
    """库存盘点基础模式"""
    warehouse: Optional[str] = None
    remark: Optional[str] = None
    attachment: Optional[str] = None

class StockCheckCreate(StockCheckBase):
    """创建库存盘点"""
    pass

class StockCheckUpdate(BaseSchema):
    """更新库存盘点"""
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    end_time: Optional[str] = None
    checker_id: Optional[int] = None
    remark: Optional[str] = None
    attachment: Optional[str] = None

class StockCheckItemBase(BaseSchema):
    """库存盘点明细基础模式"""
    product_id: int
    actual_stock: int
    remark: Optional[str] = None

class StockCheckItemCreate(StockCheckItemBase):
    """创建库存盘点明细"""
    pass

class StockCheckItemUpdate(BaseSchema):
    """更新库存盘点明细"""
    actual_stock: Optional[int] = None
    remark: Optional[str] = None

class StockCheckItemInDB(StockCheckItemBase):
    """数据库中的库存盘点明细"""
    id: int
    check_id: int
    system_stock: int
    difference: int
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None
    created_at: datetime
    updated_at: datetime

class StockCheckItemResponse(StockCheckItemInDB):
    """库存盘点明细响应"""
    product_sku: str
    product_name: str

class StockCheckInDB(StockCheckBase):
    """数据库中的库存盘点"""
    id: int
    check_no: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    operator_id: int
    checker_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class StockCheckResponse(StockCheckInDB):
    """库存盘点响应"""
    items: List[StockCheckItemResponse]
    operator_name: str
    checker_name: Optional[str] = None

class StockAlertBase(BaseSchema):
    """库存预警基础模式"""
    product_id: int
    alert_type: str = Field(..., pattern="^(low|high)$")
    threshold: int
    current_stock: int
    remark: Optional[str] = None

class StockAlertCreate(StockAlertBase):
    """创建库存预警"""
    pass

class StockAlertUpdate(BaseSchema):
    """更新库存预警"""
    status: Optional[str] = Field(None, pattern="^(active|resolved)$")
    resolved_time: Optional[str] = None
    resolver_id: Optional[int] = None
    remark: Optional[str] = None

class StockAlertInDB(StockAlertBase):
    """数据库中的库存预警"""
    id: int
    status: str
    resolved_time: Optional[str] = None
    resolver_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class StockAlertResponse(StockAlertInDB):
    """库存预警响应"""
    product_sku: str
    product_name: str
    resolver_name: Optional[str] = None

class StockQuery(PageParams):
    """库存查询参数"""
    keyword: Optional[str] = None
    operation_type: Optional[str] = None
    warehouse: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    product_id: Optional[int] = None
    batch_number: Optional[str] = None

class StockCheckQuery(PageParams):
    """库存盘点查询参数"""
    status: Optional[str] = None
    warehouse: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    operator_id: Optional[int] = None

class StockAlertQuery(PageParams):
    """库存预警查询参数"""
    alert_type: Optional[str] = None
    status: Optional[str] = None
    product_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class StockSummary(BaseModel):
    """库存汇总"""
    total_products: int
    total_quantity: int
    total_amount: float
    alert_count: int
    check_count: int

class StockTimelineBase(BaseSchema):
    """库存时间线基础模式"""
    product_id: int
    date: date
    opening_stock: int
    closing_stock: int
    in_transit: int = 0
    in_transit_details: Optional[List[Dict]] = None
    incoming: int = 0
    outgoing: int = 0
    adjustments: int = 0

class StockTimelineCreate(StockTimelineBase):
    """创建库存时间线"""
    pass

class StockTimelineInDB(StockTimelineBase):
    """数据库中的库存时间线"""
    id: int

class StockTimelineResponse(StockTimelineInDB):
    """库存时间线响应"""
    product_sku: str
    product_name: str

class TransitStockBase(BaseSchema):
    """在途库存基础模式"""
    product_id: int
    packing_list_id: int
    quantity: int
    shipping_date: Optional[date] = None
    estimated_arrival: Optional[date] = None
    transport_type: str = Field(..., pattern="^(sea|air)$")
    status: str = Field(default="in_transit", pattern="^(in_transit|arrived|cancelled)$")

class TransitStockCreate(TransitStockBase):
    """创建在途库存"""
    pass

class TransitStockInDB(TransitStockBase):
    """数据库中的在途库存"""
    id: int
    created_at: datetime
    updated_at: datetime

class TransitStockResponse(TransitStockInDB):
    """在途库存响应"""
    product_sku: str
    product_name: str
    packing_list_no: str

class StockTimelineQuery(PageParams):
    """库存时间线查询参数"""
    product_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class TransitStockQuery(PageParams):
    """在途库存查询参数"""
    product_id: Optional[int] = None
    packing_list_id: Optional[int] = None
    transport_type: Optional[str] = Field(None, pattern="^(sea|air)$")
    status: Optional[str] = Field(None, pattern="^(in_transit|arrived|cancelled)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None 