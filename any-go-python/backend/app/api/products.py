from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.product import Product
from ..schemas.product import ProductResponse
from ..auth.jwt import check_permission

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    keyword: Optional[str] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("products:read"))
):
    """
    搜索商品
    """
    query = db.query(Product).filter(Product.status == "active")
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                Product.sku.ilike(f"%{keyword}%"),
                Product.name.ilike(f"%{keyword}%"),
                Product.chinese_name.ilike(f"%{keyword}%")
            )
        )
    
    # 类型筛选
    if type:
        query = query.filter(Product.type == type)
    
    # 分类筛选
    if category:
        query = query.filter(Product.category == category)
    
    # 价格范围
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # 库存状态
    if in_stock is not None:
        if in_stock:
            query = query.filter(Product.stock > 0)
        else:
            query = query.filter(Product.stock == 0)
    
    # 按SKU排序
    products = query.order_by(Product.sku).all()
    
    return products 