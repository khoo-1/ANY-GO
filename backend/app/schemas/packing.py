from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, constr, confloat, conint

class PackingItemBase(BaseModel):
    """打包项目基础模式"""
    product_id: int
    quantity: conint(gt=0)
    notes: Optional[str] = None
    is_packed: Optional[bool] = False
    box_quantities: Optional[Dict[str, int]] = None

class PackingItemCreate(PackingItemBase):
    """创建打包项目模式"""
    pass

class PackingItemUpdate(BaseModel):
    """更新打包项目模式"""
    quantity: Optional[conint(gt=0)] = None
    notes: Optional[str] = None
    is_packed: Optional[bool] = None
    box_quantities: Optional[Dict[str, int]] = None

class PackingItemResponse(PackingItemBase):
    """打包项目响应模式"""
    id: int
    packing_list_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BoxSpecsBase(BaseModel):
    """箱子规格基础模式"""
    length: confloat(gt=0)
    width: confloat(gt=0)
    height: confloat(gt=0)
    weight: confloat(gt=0)
    volume: confloat(gt=0)
    edge_volume: confloat(gt=0)
    total_pieces: conint(gt=0)

class BoxSpecsCreate(BoxSpecsBase):
    """创建箱子规格模式"""
    pass

class BoxSpecsUpdate(BoxSpecsBase):
    """更新箱子规格模式"""
    pass

class BoxSpecsResponse(BoxSpecsBase):
    """箱子规格响应模式"""
    id: int
    packing_list_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PackingListBase(BaseModel):
    """打包清单基础模式"""
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = "draft"
    assigned_to: Optional[int] = None

class PackingListCreate(PackingListBase):
    """创建打包清单模式"""
    items: List[PackingItemCreate]

class PackingListUpdate(PackingListBase):
    """更新打包清单模式"""
    items: Optional[List[PackingItemCreate]] = None

class PackingListResponse(PackingListBase):
    """打包清单响应模式"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    items: List[PackingItemResponse]
    box_specs: Optional[BoxSpecsResponse] = None

    class Config:
        from_attributes = True 