from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.routers.auth import get_current_active_user
from app.models import User

router = APIRouter(prefix="/api/products", tags=["产品"])

# 产品模型
class ProductBase(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    price: float
    cost: float
    weight: Optional[float] = None
    stock: int = 0
    category: Optional[str] = None
    tags: List[str] = []

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 模拟产品数据
fake_products = [
    {
        "id": 1,
        "name": "智能手表",
        "sku": "SW-001",
        "description": "多功能智能手表，支持心率监测、运动追踪等功能",
        "price": 299.99,
        "cost": 150.00,
        "weight": 0.05,
        "stock": 100,
        "category": "电子产品",
        "tags": ["智能穿戴", "电子产品", "热销"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": 2,
        "name": "便携式蓝牙音箱",
        "sku": "BS-002",
        "description": "高品质便携式蓝牙音箱，防水设计，续航时间长",
        "price": 89.99,
        "cost": 40.00,
        "weight": 0.3,
        "stock": 150,
        "category": "电子产品",
        "tags": ["音频设备", "电子产品", "户外"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "id": 3,
        "name": "多功能厨房刀具套装",
        "sku": "KS-003",
        "description": "高品质不锈钢厨房刀具套装，包含主厨刀、面包刀、水果刀等",
        "price": 129.99,
        "cost": 60.00,
        "weight": 1.2,
        "stock": 80,
        "category": "厨房用品",
        "tags": ["厨房用品", "家居", "套装"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

# 路由定义
@router.get("/", response_model=dict)
async def get_products(
    page: int = 1,
    pageSize: int = 20,
    keyword: str = "",
    type: str = None,
    category: Optional[str] = None,
    status: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取产品列表，支持分页和筛选
    """
    # 检查权限
    if "products:read" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限访问此资源"
        )
    
    # 计算分页参数
    skip = (page - 1) * pageSize
    limit = pageSize
    
    # 筛选产品
    filtered_products = fake_products
    
    if keyword:
        keyword = keyword.lower()
        filtered_products = [
            p for p in filtered_products 
            if keyword in p["sku"].lower() or keyword in p["name"].lower()
        ]
    
    if type:
        filtered_products = [p for p in filtered_products if p.get("type") == type]
    
    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]
        
    if status:
        filtered_products = [p for p in filtered_products if p.get("status") == status]
    
    # 计算总数
    total = len(filtered_products)
    
    # 分页
    paginated_products = filtered_products[skip : skip + limit]
    
    return {
        "items": paginated_products,
        "total": total
    }

@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    根据ID获取产品详情
    """
    # 检查权限
    if "products:read" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限访问此资源"
        )
    
    # 查找产品
    for product in fake_products:
        if product["id"] == product_id:
            return product
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="产品不存在"
    )

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新产品
    """
    # 检查权限
    if "products:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )
    
    # 模拟创建产品
    new_id = max(p["id"] for p in fake_products) + 1
    now = datetime.utcnow()
    
    new_product = {
        "id": new_id,
        **product.dict(),
        "created_at": now,
        "updated_at": now
    }
    
    fake_products.append(new_product)
    return new_product

@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_update: ProductBase,
    current_user: User = Depends(get_current_active_user)
):
    """
    更新产品信息
    """
    # 检查权限
    if "products:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )
    
    # 查找并更新产品
    for i, product in enumerate(fake_products):
        if product["id"] == product_id:
            updated_product = {
                **product,
                **product_update.dict(),
                "updated_at": datetime.utcnow()
            }
            fake_products[i] = updated_product
            return updated_product
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="产品不存在"
    )

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    删除产品
    """
    # 检查权限
    if "products:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )
    
    # 查找并删除产品
    for i, product in enumerate(fake_products):
        if product["id"] == product_id:
            fake_products.pop(i)
            return
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="产品不存在"
    )

@router.get("/categories", response_model=List[str])
async def get_categories(current_user: User = Depends(get_current_active_user)):
    """
    获取所有商品分类列表
    """
    # 检查权限
    if "products:read" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限访问此资源"
        )
    
    # 从产品数据中提取唯一的分类列表
    categories = list(set(p["category"] for p in fake_products if p["category"]))
    return categories 