from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from fastapi_cache.decorator import cache
import pandas as pd
import io
from datetime import datetime, timedelta

from ..database import get_db
from ..models.product import Product
from ..schemas.product import ProductResponse, ProductExportRequest, ProductListResponse
from ..auth.jwt import check_permission

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/search", response_model=ProductListResponse)
@cache(expire=300)  # 缓存5分钟
async def search_products(
    keyword: Optional[str] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("products:read"))
):
    """
    搜索商品(带分页)
    """
    # 构建基础查询
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
    
    # 计算总数
    total = query.count()
    
    # 分页
    query = query.order_by(Product.sku)
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # 执行查询
    products = query.all()
    
    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/categories", response_model=List[str])
@cache(expire=3600)  # 缓存1小时
async def get_categories(
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("products:read"))
):
    """获取所有商品分类"""
    categories = db.query(Product.category).distinct().all()
    return [c[0] for c in categories if c[0]]

@router.get("/statistics", response_model=dict)
@cache(expire=300)  # 缓存5分钟
async def get_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("products:read"))
):
    """获取商品统计信息"""
    # 使用子查询优化性能
    stats = db.query(
        func.count().label('total_products'),
        func.sum(Product.stock).label('total_stock'),
        func.avg(Product.price).label('avg_price'),
        func.count(func.nullif(Product.stock > 0, False)).label('in_stock_count'),
        func.count(func.nullif(Product.stock <= Product.alert_threshold, False)).label('low_stock_count')
    ).filter(Product.status == 'active').first()
    
    return {
        "total_products": stats.total_products or 0,
        "total_stock": int(stats.total_stock or 0),
        "avg_price": float(stats.avg_price or 0),
        "in_stock_count": stats.in_stock_count or 0,
        "low_stock_count": stats.low_stock_count or 0
    }

@router.post("/export")
async def export_products(
    request: ProductExportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("products:read"))
):
    """导出产品列表(优化大数据量处理)"""
    # 分批次查询数据
    BATCH_SIZE = 1000
    query = db.query(Product).filter(Product.status == "active")
    
    # 应用过滤条件
    if request.keyword:
        query = query.filter(
            or_(
                Product.sku.ilike(f"%{request.keyword}%"),
                Product.name.ilike(f"%{request.keyword}%"),
                Product.chinese_name.ilike(f"%{request.keyword}%")
            )
        )
    
    if request.type:
        query = query.filter(Product.type == request.type)
    
    if request.category:
        query = query.filter(Product.category == request.category)
        
    if request.min_price is not None:
        query = query.filter(Product.price >= request.min_price)
        
    if request.max_price is not None:
        query = query.filter(Product.price <= request.max_price)
        
    if request.in_stock is not None:
        if request.in_stock:
            query = query.filter(Product.stock > 0)
        else:
            query = query.filter(Product.stock == 0)
    
    # 准备数据
    data = []
    field_mapping = {
        "sku": "SKU",
        "name": "商品名称",
        "chinese_name": "中文名称",
        "type": "类型",
        "category": "分类",
        "price": "价格",
        "cost": "成本",
        "stock": "库存",
        "alert_threshold": "预警阈值",
        "supplier": "供应商",
        "status": "状态"
    }
    
    selected_fields = request.fields or list(field_mapping.keys())
    
    # 分批处理数据
    offset = 0
    while True:
        batch = query.order_by(Product.id).offset(offset).limit(BATCH_SIZE).all()
        if not batch:
            break
            
        for product in batch:
            item = {}
            for field in selected_fields:
                if field in field_mapping:
                    item[field_mapping[field]] = getattr(product, field)
            data.append(item)
            
        offset += BATCH_SIZE
        
        # 如果数据量太大,可能需要主动清理内存
        if offset % (BATCH_SIZE * 10) == 0:
            import gc
            gc.collect()
    
    # 创建Excel文件
    df = pd.DataFrame(data)
    output = io.BytesIO()
    
    # 使用xlsxwriter引擎处理大文件
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='产品列表')
        
        # 调整列宽
        worksheet = writer.sheets['产品列表']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.set_column(idx, idx, max_length + 2)
    
    output.seek(0)
    
    # 生成文件名
    filename = f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    ) 