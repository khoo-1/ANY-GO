from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from datetime import datetime, date, timedelta

from ..database import get_db
from ..models.inventory import (
    InventoryAnalysis, ProductTurnover, CategoryTurnover,
    InventoryAnalysisType
)
from ..models.product import Product
from ..models.sales import Order, OrderItem
from ..schemas.inventory import (
    InventoryAnalysisResponse, ProductTurnoverResponse,
    CategoryTurnoverResponse, InventoryQuery, ProductTurnoverQuery,
    CategoryTurnoverQuery, TurnoverSummary
)
from ..auth.jwt import check_permission

router = APIRouter(prefix="/inventory", tags=["库存分析"])

@router.get("/analysis", response_model=List[InventoryAnalysisResponse])
async def list_inventory_analysis(
    query: InventoryQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("inventory:read"))
):
    """获取库存分析列表"""
    analysis_query = db.query(InventoryAnalysis)
    
    if query.type:
        analysis_query = analysis_query.filter(InventoryAnalysis.type == query.type)
        
    if query.start_date:
        analysis_query = analysis_query.filter(InventoryAnalysis.date >= query.start_date)
        
    if query.end_date:
        analysis_query = analysis_query.filter(InventoryAnalysis.date <= query.end_date)
    
    total = analysis_query.count()
    analysis = analysis_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return analysis

@router.post("/analysis/calculate")
async def calculate_inventory_analysis(
    analysis_date: date,
    analysis_type: InventoryAnalysisType,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("inventory:write"))
):
    """计算指定日期的库存分析"""
    # 获取日期范围
    if analysis_type == InventoryAnalysisType.DAILY:
        start_date = analysis_date
        end_date = analysis_date
    elif analysis_type == InventoryAnalysisType.WEEKLY:
        start_date = analysis_date - timedelta(days=analysis_date.weekday())
        end_date = start_date + timedelta(days=6)
    else:  # MONTHLY
        start_date = analysis_date.replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
    
    # 计算库存总览
    inventory_summary = db.query(
        func.count(Product.id).label("total_products"),
        func.sum(Product.stock).label("total_quantity"),
        func.sum(Product.stock * Product.cost).label("total_value")
    ).filter(
        Product.status == "active"
    ).first()
    
    # 计算销售数据
    sales_data = db.query(
        func.sum(OrderItem.quantity).label("sales_quantity"),
        func.sum(OrderItem.total).label("sales_amount")
    ).join(
        Order, OrderItem.order_id == Order.id
    ).filter(
        Order.order_date.between(start_date, end_date),
        Order.status == "completed"
    ).first()
    
    # 计算库存结构
    stock_structure = db.query(
        func.count(case((Product.stock > 0, 1), else_=None)).label("active_products"),
        func.count(case((Product.stock == 0, 1), else_=None)).label("stockout_products"),
        func.count(case((Product.stock > Product.alert_threshold * 2, 1), else_=None)).label("overstock_products")
    ).filter(
        Product.status == "active"
    ).first()
    
    # 计算周转率和周转天数
    period_days = (end_date - start_date).days + 1
    average_inventory = inventory_summary.total_value or 0
    sales_amount = sales_data.sales_amount or 0
    
    if average_inventory > 0 and period_days > 0:
        turnover_rate = (sales_amount / average_inventory) * (365 / period_days)
        turnover_days = 365 / turnover_rate if turnover_rate > 0 else 0
    else:
        turnover_rate = 0
        turnover_days = 0
    
    # 计算库存健康度
    total_products = inventory_summary.total_products or 0
    healthy_stock_ratio = (
        (total_products - stock_structure.stockout_products - stock_structure.overstock_products)
        / total_products * 100 if total_products > 0 else 0
    )
    stockout_ratio = stock_structure.stockout_products / total_products * 100 if total_products > 0 else 0
    overstock_ratio = stock_structure.overstock_products / total_products * 100 if total_products > 0 else 0
    
    # 创建或更新分析记录
    analysis = db.query(InventoryAnalysis).filter(
        InventoryAnalysis.date == analysis_date,
        InventoryAnalysis.type == analysis_type
    ).first()
    
    if analysis:
        # 更新现有记录
        analysis.total_products = inventory_summary.total_products
        analysis.total_quantity = inventory_summary.total_quantity
        analysis.total_value = inventory_summary.total_value
        analysis.turnover_rate = turnover_rate
        analysis.turnover_days = turnover_days
        analysis.average_inventory = average_inventory
        analysis.inventory_cost = inventory_summary.total_value
        analysis.active_products = stock_structure.active_products
        analysis.inactive_products = total_products - stock_structure.active_products
        analysis.stockout_products = stock_structure.stockout_products
        analysis.overstock_products = stock_structure.overstock_products
        analysis.healthy_stock_ratio = healthy_stock_ratio
        analysis.stockout_ratio = stockout_ratio
        analysis.overstock_ratio = overstock_ratio
    else:
        # 创建新记录
        analysis = InventoryAnalysis(
            date=analysis_date,
            type=analysis_type,
            total_products=inventory_summary.total_products,
            total_quantity=inventory_summary.total_quantity,
            total_value=inventory_summary.total_value,
            turnover_rate=turnover_rate,
            turnover_days=turnover_days,
            average_inventory=average_inventory,
            inventory_cost=inventory_summary.total_value,
            active_products=stock_structure.active_products,
            inactive_products=total_products - stock_structure.active_products,
            stockout_products=stock_structure.stockout_products,
            overstock_products=stock_structure.overstock_products,
            healthy_stock_ratio=healthy_stock_ratio,
            stockout_ratio=stockout_ratio,
            overstock_ratio=overstock_ratio
        )
        db.add(analysis)
    
    # 计算商品周转率
    products = db.query(Product).filter(Product.status == "active").all()
    for product in products:
        # 获取商品销售数据
        product_sales = db.query(
            func.sum(OrderItem.quantity).label("sales_quantity"),
            func.sum(OrderItem.total).label("sales_amount")
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.order_date.between(start_date, end_date),
            Order.status == "completed",
            OrderItem.product_id == product.id
        ).first()
        
        # 计算商品周转指标
        sales_quantity = product_sales.sales_quantity or 0
        sales_amount = product_sales.sales_amount or 0
        average_stock = product.stock  # 简化处理，使用当前库存作为平均库存
        
        if average_stock > 0 and period_days > 0:
            product_turnover_rate = (sales_quantity / average_stock) * (365 / period_days)
            product_turnover_days = 365 / product_turnover_rate if product_turnover_rate > 0 else 0
        else:
            product_turnover_rate = 0
            product_turnover_days = 0
        
        # 判断库存状态
        if product.stock == 0:
            stock_status = "stockout"
        elif product.stock > product.alert_threshold * 2:
            stock_status = "overstock"
        else:
            stock_status = "normal"
        
        # 创建或更新商品周转记录
        product_turnover = db.query(ProductTurnover).filter(
            ProductTurnover.product_id == product.id,
            ProductTurnover.date == analysis_date,
            ProductTurnover.type == analysis_type
        ).first()
        
        if product_turnover:
            product_turnover.beginning_stock = product.stock
            product_turnover.ending_stock = product.stock
            product_turnover.average_stock = average_stock
            product_turnover.sales_quantity = sales_quantity
            product_turnover.sales_amount = sales_amount
            product_turnover.turnover_rate = product_turnover_rate
            product_turnover.turnover_days = product_turnover_days
            product_turnover.stock_status = stock_status
        else:
            product_turnover = ProductTurnover(
                product_id=product.id,
                date=analysis_date,
                type=analysis_type,
                beginning_stock=product.stock,
                ending_stock=product.stock,
                average_stock=average_stock,
                sales_quantity=sales_quantity,
                sales_amount=sales_amount,
                turnover_rate=product_turnover_rate,
                turnover_days=product_turnover_days,
                stock_status=stock_status
            )
            db.add(product_turnover)
    
    # 计算品类周转率
    categories = db.query(Product.category).distinct().all()
    for category, in categories:
        # 获取品类销售数据
        category_sales = db.query(
            func.sum(OrderItem.quantity).label("sales_quantity"),
            func.sum(OrderItem.total).label("sales_amount")
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            Product, OrderItem.product_id == Product.id
        ).filter(
            Order.order_date.between(start_date, end_date),
            Order.status == "completed",
            Product.category == category
        ).first()
        
        # 获取品类库存数据
        category_inventory = db.query(
            func.count(Product.id).label("total_products"),
            func.sum(Product.stock).label("total_stock"),
            func.sum(Product.stock * Product.cost).label("total_value"),
            func.count(case((Product.stock > 0, 1), else_=None)).label("active_products"),
            func.count(case((Product.stock == 0, 1), else_=None)).label("stockout_products"),
            func.count(case((Product.stock > Product.alert_threshold * 2, 1), else_=None)).label("overstock_products")
        ).filter(
            Product.category == category,
            Product.status == "active"
        ).first()
        
        # 计算品类周转指标
        sales_quantity = category_sales.sales_quantity or 0
        sales_amount = category_sales.sales_amount or 0
        average_stock = category_inventory.total_stock or 0
        
        if average_stock > 0 and period_days > 0:
            category_turnover_rate = (sales_quantity / average_stock) * (365 / period_days)
            category_turnover_days = 365 / category_turnover_rate if category_turnover_rate > 0 else 0
        else:
            category_turnover_rate = 0
            category_turnover_days = 0
        
        # 创建或更新品类周转记录
        category_turnover = db.query(CategoryTurnover).filter(
            CategoryTurnover.category == category,
            CategoryTurnover.date == analysis_date,
            CategoryTurnover.type == analysis_type
        ).first()
        
        if category_turnover:
            category_turnover.total_products = category_inventory.total_products
            category_turnover.total_stock = category_inventory.total_stock
            category_turnover.total_value = category_inventory.total_value
            category_turnover.sales_quantity = sales_quantity
            category_turnover.sales_amount = sales_amount
            category_turnover.turnover_rate = category_turnover_rate
            category_turnover.turnover_days = category_turnover_days
            category_turnover.active_products = category_inventory.active_products
            category_turnover.inactive_products = category_inventory.total_products - category_inventory.active_products
            category_turnover.stockout_products = category_inventory.stockout_products
            category_turnover.overstock_products = category_inventory.overstock_products
        else:
            category_turnover = CategoryTurnover(
                category=category,
                date=analysis_date,
                type=analysis_type,
                total_products=category_inventory.total_products,
                total_stock=category_inventory.total_stock,
                total_value=category_inventory.total_value,
                sales_quantity=sales_quantity,
                sales_amount=sales_amount,
                turnover_rate=category_turnover_rate,
                turnover_days=category_turnover_days,
                active_products=category_inventory.active_products,
                inactive_products=category_inventory.total_products - category_inventory.active_products,
                stockout_products=category_inventory.stockout_products,
                overstock_products=category_inventory.overstock_products
            )
            db.add(category_turnover)
    
    db.commit()
    return {"message": "库存分析计算完成"}

@router.get("/turnover/products", response_model=List[ProductTurnoverResponse])
async def list_product_turnover(
    query: ProductTurnoverQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("inventory:read"))
):
    """获取商品周转列表"""
    turnover_query = db.query(ProductTurnover)
    
    if query.product_id:
        turnover_query = turnover_query.filter(ProductTurnover.product_id == query.product_id)
        
    if query.category:
        turnover_query = turnover_query.join(Product).filter(Product.category == query.category)
        
    if query.type:
        turnover_query = turnover_query.filter(ProductTurnover.type == query.type)
        
    if query.start_date:
        turnover_query = turnover_query.filter(ProductTurnover.date >= query.start_date)
        
    if query.end_date:
        turnover_query = turnover_query.filter(ProductTurnover.date <= query.end_date)
        
    if query.stock_status:
        turnover_query = turnover_query.filter(ProductTurnover.stock_status == query.stock_status)
    
    total = turnover_query.count()
    turnovers = turnover_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return turnovers

@router.get("/turnover/categories", response_model=List[CategoryTurnoverResponse])
async def list_category_turnover(
    query: CategoryTurnoverQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("inventory:read"))
):
    """获取品类周转列表"""
    turnover_query = db.query(CategoryTurnover)
    
    if query.category:
        turnover_query = turnover_query.filter(CategoryTurnover.category == query.category)
        
    if query.type:
        turnover_query = turnover_query.filter(CategoryTurnover.type == query.type)
        
    if query.start_date:
        turnover_query = turnover_query.filter(CategoryTurnover.date >= query.start_date)
        
    if query.end_date:
        turnover_query = turnover_query.filter(CategoryTurnover.date <= query.end_date)
    
    total = turnover_query.count()
    turnovers = turnover_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return turnovers

@router.get("/summary", response_model=TurnoverSummary)
async def get_turnover_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("inventory:read"))
):
    """获取周转汇总信息"""
    # 构建查询条件
    conditions = []
    if start_date:
        conditions.append(InventoryAnalysis.date >= start_date)
    if end_date:
        conditions.append(InventoryAnalysis.date <= end_date)
    
    # 获取整体周转指标
    overall_stats = db.query(
        func.avg(InventoryAnalysis.turnover_rate).label("turnover_rate"),
        func.avg(InventoryAnalysis.turnover_days).label("turnover_days"),
        func.avg(InventoryAnalysis.total_value).label("inventory_value")
    ).filter(*conditions).first()
    
    # 获取销售总额
    sales_total = db.query(
        func.sum(Order.total).label("total_sales")
    ).filter(
        Order.status == "completed",
        Order.order_date.between(start_date, end_date) if start_date and end_date else True
    ).scalar() or 0
    
    # 获取库存健康度
    latest_analysis = db.query(InventoryAnalysis).filter(
        *conditions
    ).order_by(
        desc(InventoryAnalysis.date)
    ).first()
    
    inventory_health = {
        "healthy_stock_ratio": latest_analysis.healthy_stock_ratio if latest_analysis else 0,
        "stockout_ratio": latest_analysis.stockout_ratio if latest_analysis else 0,
        "overstock_ratio": latest_analysis.overstock_ratio if latest_analysis else 0
    }
    
    # 获取周转率最高的商品
    top_products = db.query(
        Product.id,
        Product.sku,
        Product.name,
        func.avg(ProductTurnover.turnover_rate).label("turnover_rate"),
        func.avg(ProductTurnover.turnover_days).label("turnover_days")
    ).join(
        ProductTurnover
    ).filter(
        *conditions
    ).group_by(
        Product.id
    ).order_by(
        desc("turnover_rate")
    ).limit(10).all()
    
    # 获取周转率最低的商品
    bottom_products = db.query(
        Product.id,
        Product.sku,
        Product.name,
        func.avg(ProductTurnover.turnover_rate).label("turnover_rate"),
        func.avg(ProductTurnover.turnover_days).label("turnover_days")
    ).join(
        ProductTurnover
    ).filter(
        *conditions
    ).group_by(
        Product.id
    ).order_by(
        "turnover_rate"
    ).limit(10).all()
    
    # 获取品类分析
    category_stats = db.query(
        CategoryTurnover.category,
        func.avg(CategoryTurnover.turnover_rate).label("turnover_rate"),
        func.avg(CategoryTurnover.turnover_days).label("turnover_days"),
        func.avg(CategoryTurnover.total_value).label("inventory_value"),
        func.avg(CategoryTurnover.sales_amount).label("sales_amount")
    ).filter(
        *conditions
    ).group_by(
        CategoryTurnover.category
    ).all()
    
    return TurnoverSummary(
        overall_turnover_rate=overall_stats.turnover_rate or 0,
        overall_turnover_days=overall_stats.turnover_days or 0,
        total_inventory_value=overall_stats.inventory_value or 0,
        total_sales_amount=sales_total,
        inventory_health=inventory_health,
        top_turnover_products=[{
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "turnover_rate": p.turnover_rate,
            "turnover_days": p.turnover_days
        } for p in top_products],
        bottom_turnover_products=[{
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "turnover_rate": p.turnover_rate,
            "turnover_days": p.turnover_days
        } for p in bottom_products],
        category_analysis=[{
            "category": c.category,
            "turnover_rate": c.turnover_rate,
            "turnover_days": c.turnover_days,
            "inventory_value": c.inventory_value,
            "sales_amount": c.sales_amount
        } for c in category_stats]
    ) 