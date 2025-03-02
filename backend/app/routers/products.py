from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models import Product, User as UserModel
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.auth.session import get_current_user  # 使用session认证
from app.core.security import get_current_active_user
from ..crud.product import get_product, get_products, create_product, update_product, delete_product

router = APIRouter(
    prefix="/api/products",
    tags=["产品"],
    responses={404: {"description": "未找到"}},
)

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

    class Config:
        from_attributes = True

class ProductCreateSchema(ProductBase):
    pass

class ProductUpdateSchema(ProductBase):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None

class ProductResponseSchema(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

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
@router.get("/", response_model=List[ProductResponse])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取产品列表"""
    products = get_products(db, skip=skip, limit=limit)
    return products

@router.post("/", response_model=ProductResponse)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """创建新产品"""
    return create_product(db=db, product=product, user_id=current_user.id)

@router.get("/{product_id}", response_model=ProductResponse)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取产品详情"""
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product_info(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新产品信息"""
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    return update_product(db=db, product_id=product_id, product=product, user_id=current_user.id)

@router.delete("/{product_id}")
def delete_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """删除产品"""
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    delete_product(db=db, product_id=product_id)
    return {"message": "产品已删除"}

@router.get("/categories", response_model=List[str])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """获取所有商品分类列表"""
    categories = db.query(Product.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]] 