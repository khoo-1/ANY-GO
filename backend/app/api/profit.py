from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from datetime import datetime, date, timedelta

from ..database import get_db
from ..models.profit import (
    ProfitAnalysis, ProductProfit, CategoryProfit,
    ProfitAnalysisType
)
from ..models.product import Product
from ..models.sales import Order, OrderItem
from ..schemas.profit import (
    ProfitAnalysisResponse, ProductProfitResponse,
    CategoryProfitResponse, ProfitQuery, ProductProfitQuery,
    CategoryProfitQuery, ProfitSummary
)
from ..auth.jwt import check_permission

router = APIRouter(prefix="/profit", tags=["利润分析"])

@router.get("/analysis", response_model=List[ProfitAnalysisResponse])
async def list_profit_analysis(
    query: ProfitQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("profit:read"))
):
    """获取利润分析列表"""
    analysis_query = db.query(ProfitAnalysis)
    
    if query.type:
        analysis_query = analysis_query.filter(ProfitAnalysis.type == query.type)
        
    if query.start_date:
        analysis_query = analysis_query.filter(ProfitAnalysis.date >= query.start_date)
        
    if query.end_date:
        analysis_query = analysis_query.filter(ProfitAnalysis.date <= query.end_date)
    
    total = analysis_query.count()
    analysis = analysis_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return analysis

@router.post("/analysis/calculate")
async def calculate_profit_analysis(
    analysis_date: date,
    analysis_type: ProfitAnalysisType,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("profit:write"))
):
    """计算指定日期的利润分析"""
    # 获取日期范围
    if analysis_type == ProfitAnalysisType.DAILY:
        start_date = analysis_date
        end_date = analysis_date
    elif analysis_type == ProfitAnalysisType.WEEKLY:
        start_date = analysis_date - timedelta(days=analysis_date.weekday())
        end_date = start_date + timedelta(days=6)
    else:  # MONTHLY
        start_date = analysis_date.replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
    
    # 计算销售数据
    sales_data = db.query(
        func.count(Order.id).label("total_orders"),
        func.sum(Order.total).label("total_sales")
    ).filter(
        Order.order_date.between(start_date, end_date),
        Order.status == "completed"
    ).first()
    
    # 计算成本数据
    cost_data = db.query(
        func.sum(OrderItem.quantity * Product.cost).label("product_cost"),
        func.sum(Order.shipping_fee).label("shipping_cost")
    ).join(
        Order, OrderItem.order_id == Order.id
    ).join(
        Product, OrderItem.product_id == Product.id
    ).filter(
        Order.order_date.between(start_date, end_date),
        Order.status == "completed"
    ).first()
    
    # 计算运营成本（示例：按订单数分摊固定运营成本）
    operation_cost = (sales_data.total_orders or 0) * 10  # 假设每单10元运营成本
    other_cost = (sales_data.total_orders or 0) * 5  # 假设每单5元其他成本
    
    # 计算总成本
    total_cost = (cost_data.product_cost or 0) + (cost_data.shipping_cost or 0) + operation_cost + other_cost
    
    # 计算利润数据
    total_sales = sales_data.total_sales or 0
    gross_profit = total_sales - (cost_data.product_cost or 0)
    net_profit = total_sales - total_cost
    
    # 计算利润率
    gross_profit_rate = (gross_profit / total_sales * 100) if total_sales > 0 else 0
    net_profit_rate = (net_profit / total_sales * 100) if total_sales > 0 else 0
    
    # 创建或更新分析记录
    analysis = db.query(ProfitAnalysis).filter(
        ProfitAnalysis.date == analysis_date,
        ProfitAnalysis.type == analysis_type
    ).first()
    
    if analysis:
        analysis.total_orders = sales_data.total_orders or 0
        analysis.total_sales = total_sales
        analysis.product_cost = cost_data.product_cost or 0
        analysis.shipping_cost = cost_data.shipping_cost or 0
        analysis.operation_cost = operation_cost
        analysis.other_cost = other_cost
        analysis.total_cost = total_cost
        analysis.gross_profit = gross_profit
        analysis.net_profit = net_profit
        analysis.gross_profit_rate = gross_profit_rate
        analysis.net_profit_rate = net_profit_rate
    else:
        analysis = ProfitAnalysis(
            date=analysis_date,
            type=analysis_type,
            total_orders=sales_data.total_orders or 0,
            total_sales=total_sales,
            product_cost=cost_data.product_cost or 0,
            shipping_cost=cost_data.shipping_cost or 0,
            operation_cost=operation_cost,
            other_cost=other_cost,
            total_cost=total_cost,
            gross_profit=gross_profit,
            net_profit=net_profit,
            gross_profit_rate=gross_profit_rate,
            net_profit_rate=net_profit_rate
        )
        db.add(analysis)
    
    # 计算商品利润
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
        
        sales_quantity = product_sales.sales_quantity or 0
        sales_amount = product_sales.sales_amount or 0
        
        # 计算成本
        unit_cost = product.cost
        total_cost = unit_cost * sales_quantity
        shipping_cost = sales_quantity * 5  # 假设每件商品5元运费
        
        # 计算利润
        gross_profit = sales_amount - total_cost
        net_profit = gross_profit - shipping_cost
        
        # 计算利润率
        gross_profit_rate = (gross_profit / sales_amount * 100) if sales_amount > 0 else 0
        net_profit_rate = (net_profit / sales_amount * 100) if sales_amount > 0 else 0
        
        # 创建或更新商品利润记录
        product_profit = db.query(ProductProfit).filter(
            ProductProfit.product_id == product.id,
            ProductProfit.date == analysis_date,
            ProductProfit.type == analysis_type
        ).first()
        
        if product_profit:
            product_profit.sales_quantity = sales_quantity
            product_profit.sales_amount = sales_amount
            product_profit.unit_cost = unit_cost
            product_profit.total_cost = total_cost
            product_profit.shipping_cost = shipping_cost
            product_profit.gross_profit = gross_profit
            product_profit.net_profit = net_profit
            product_profit.gross_profit_rate = gross_profit_rate
            product_profit.net_profit_rate = net_profit_rate
        else:
            product_profit = ProductProfit(
                product_id=product.id,
                date=analysis_date,
                type=analysis_type,
                sales_quantity=sales_quantity,
                sales_amount=sales_amount,
                unit_cost=unit_cost,
                total_cost=total_cost,
                shipping_cost=shipping_cost,
                gross_profit=gross_profit,
                net_profit=net_profit,
                gross_profit_rate=gross_profit_rate,
                net_profit_rate=net_profit_rate
            )
            db.add(product_profit)
    
    # 计算品类利润
    categories = db.query(Product.category).distinct().all()
    for category, in categories:
        # 获取品类销售数据
        category_sales = db.query(
            func.count(distinct(Order.id)).label("total_orders"),
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
        
        # 获取品类商品数量
        total_products = db.query(func.count(Product.id)).filter(
            Product.category == category,
            Product.status == "active"
        ).scalar()
        
        total_orders = category_sales.total_orders or 0
        sales_quantity = category_sales.sales_quantity or 0
        sales_amount = category_sales.sales_amount or 0
        
        # 计算成本
        category_cost = db.query(
            func.sum(OrderItem.quantity * Product.cost).label("product_cost")
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            Product, OrderItem.product_id == Product.id
        ).filter(
            Order.order_date.between(start_date, end_date),
            Order.status == "completed",
            Product.category == category
        ).first()
        
        product_cost = category_cost.product_cost or 0
        shipping_cost = sales_quantity * 5  # 假设每件商品5元运费
        operation_cost = total_orders * 10  # 假设每单10元运营成本
        
        # 计算利润
        gross_profit = sales_amount - product_cost
        net_profit = gross_profit - shipping_cost - operation_cost
        
        # 计算利润率
        gross_profit_rate = (gross_profit / sales_amount * 100) if sales_amount > 0 else 0
        net_profit_rate = (net_profit / sales_amount * 100) if sales_amount > 0 else 0
        
        # 计算平均值
        average_order_value = sales_amount / total_orders if total_orders > 0 else 0
        average_profit_per_order = net_profit / total_orders if total_orders > 0 else 0
        
        # 创建或更新品类利润记录
        category_profit = db.query(CategoryProfit).filter(
            CategoryProfit.category == category,
            CategoryProfit.date == analysis_date,
            CategoryProfit.type == analysis_type
        ).first()
        
        if category_profit:
            category_profit.total_products = total_products
            category_profit.total_orders = total_orders
            category_profit.sales_quantity = sales_quantity
            category_profit.sales_amount = sales_amount
            category_profit.product_cost = product_cost
            category_profit.shipping_cost = shipping_cost
            category_profit.operation_cost = operation_cost
            category_profit.gross_profit = gross_profit
            category_profit.net_profit = net_profit
            category_profit.gross_profit_rate = gross_profit_rate
            category_profit.net_profit_rate = net_profit_rate
            category_profit.average_order_value = average_order_value
            category_profit.average_profit_per_order = average_profit_per_order
        else:
            category_profit = CategoryProfit(
                category=category,
                date=analysis_date,
                type=analysis_type,
                total_products=total_products,
                total_orders=total_orders,
                sales_quantity=sales_quantity,
                sales_amount=sales_amount,
                product_cost=product_cost,
                shipping_cost=shipping_cost,
                operation_cost=operation_cost,
                gross_profit=gross_profit,
                net_profit=net_profit,
                gross_profit_rate=gross_profit_rate,
                net_profit_rate=net_profit_rate,
                average_order_value=average_order_value,
                average_profit_per_order=average_profit_per_order
            )
            db.add(category_profit)
    
    db.commit()
    return {"message": "利润分析计算完成"}

@router.get("/products", response_model=List[ProductProfitResponse])
async def list_product_profit(
    query: ProductProfitQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("profit:read"))
):
    """获取商品利润列表"""
    profit_query = db.query(ProductProfit)
    
    if query.product_id:
        profit_query = profit_query.filter(ProductProfit.product_id == query.product_id)
        
    if query.category:
        profit_query = profit_query.join(Product).filter(Product.category == query.category)
        
    if query.type:
        profit_query = profit_query.filter(ProductProfit.type == query.type)
        
    if query.start_date:
        profit_query = profit_query.filter(ProductProfit.date >= query.start_date)
        
    if query.end_date:
        profit_query = profit_query.filter(ProductProfit.date <= query.end_date)
        
    if query.min_profit_rate is not None:
        profit_query = profit_query.filter(ProductProfit.net_profit_rate >= query.min_profit_rate)
        
    if query.max_profit_rate is not None:
        profit_query = profit_query.filter(ProductProfit.net_profit_rate <= query.max_profit_rate)
    
    total = profit_query.count()
    profits = profit_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return profits

@router.get("/categories", response_model=List[CategoryProfitResponse])
async def list_category_profit(
    query: CategoryProfitQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("profit:read"))
):
    """获取品类利润列表"""
    profit_query = db.query(CategoryProfit)
    
    if query.category:
        profit_query = profit_query.filter(CategoryProfit.category == query.category)
        
    if query.type:
        profit_query = profit_query.filter(CategoryProfit.type == query.type)
        
    if query.start_date:
        profit_query = profit_query.filter(CategoryProfit.date >= query.start_date)
        
    if query.end_date:
        profit_query = profit_query.filter(CategoryProfit.date <= query.end_date)
        
    if query.min_profit_rate is not None:
        profit_query = profit_query.filter(CategoryProfit.net_profit_rate >= query.min_profit_rate)
        
    if query.max_profit_rate is not None:
        profit_query = profit_query.filter(CategoryProfit.net_profit_rate <= query.max_profit_rate)
    
    total = profit_query.count()
    profits = profit_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return profits

@router.get("/summary", response_model=ProfitSummary)
async def get_profit_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("profit:read"))
):
    """获取利润汇总信息"""
    # 构建查询条件
    conditions = []
    if start_date:
        conditions.append(ProfitAnalysis.date >= start_date)
    if end_date:
        conditions.append(ProfitAnalysis.date <= end_date)
    
    # 获取整体利润指标
    overall_stats = db.query(
        func.sum(ProfitAnalysis.total_sales).label("total_sales"),
        func.sum(ProfitAnalysis.total_cost).label("total_cost"),
        func.sum(ProfitAnalysis.gross_profit).label("gross_profit"),
        func.sum(ProfitAnalysis.net_profit).label("net_profit")
    ).filter(*conditions).first()
    
    total_sales = overall_stats.total_sales or 0
    total_cost = overall_stats.total_cost or 0
    gross_profit = overall_stats.gross_profit or 0
    net_profit = overall_stats.net_profit or 0
    
    # 计算整体利润率
    gross_profit_rate = (gross_profit / total_sales * 100) if total_sales > 0 else 0
    net_profit_rate = (net_profit / total_sales * 100) if total_sales > 0 else 0
    
    # 获取利润趋势
    trend_data = db.query(
        ProfitAnalysis.date,
        ProfitAnalysis.total_sales,
        ProfitAnalysis.gross_profit,
        ProfitAnalysis.net_profit,
        ProfitAnalysis.gross_profit_rate,
        ProfitAnalysis.net_profit_rate
    ).filter(
        *conditions
    ).order_by(
        ProfitAnalysis.date
    ).all()
    
    # 获取利润最高的商品
    top_products = db.query(
        Product.id,
        Product.sku,
        Product.name,
        func.sum(ProductProfit.sales_amount).label("sales_amount"),
        func.sum(ProductProfit.net_profit).label("net_profit"),
        func.avg(ProductProfit.net_profit_rate).label("profit_rate")
    ).join(
        ProductProfit
    ).filter(
        *conditions
    ).group_by(
        Product.id
    ).order_by(
        desc("net_profit")
    ).limit(10).all()
    
    # 获取利润最低的商品
    bottom_products = db.query(
        Product.id,
        Product.sku,
        Product.name,
        func.sum(ProductProfit.sales_amount).label("sales_amount"),
        func.sum(ProductProfit.net_profit).label("net_profit"),
        func.avg(ProductProfit.net_profit_rate).label("profit_rate")
    ).join(
        ProductProfit
    ).filter(
        *conditions
    ).group_by(
        Product.id
    ).order_by(
        "net_profit"
    ).limit(10).all()
    
    # 获取品类分析
    category_stats = db.query(
        CategoryProfit.category,
        func.sum(CategoryProfit.sales_amount).label("sales_amount"),
        func.sum(CategoryProfit.net_profit).label("net_profit"),
        func.avg(CategoryProfit.net_profit_rate).label("profit_rate"),
        func.avg(CategoryProfit.average_order_value).label("avg_order_value"),
        func.avg(CategoryProfit.average_profit_per_order).label("avg_profit_per_order")
    ).filter(
        *conditions
    ).group_by(
        CategoryProfit.category
    ).all()
    
    return ProfitSummary(
        overall_gross_profit=gross_profit,
        overall_net_profit=net_profit,
        overall_gross_profit_rate=gross_profit_rate,
        overall_net_profit_rate=net_profit_rate,
        total_sales=total_sales,
        total_cost=total_cost,
        profit_trend=[{
            "date": item.date,
            "total_sales": item.total_sales,
            "gross_profit": item.gross_profit,
            "net_profit": item.net_profit,
            "gross_profit_rate": item.gross_profit_rate,
            "net_profit_rate": item.net_profit_rate
        } for item in trend_data],
        top_profit_products=[{
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "sales_amount": p.sales_amount,
            "net_profit": p.net_profit,
            "profit_rate": p.profit_rate
        } for p in top_products],
        bottom_profit_products=[{
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "sales_amount": p.sales_amount,
            "net_profit": p.net_profit,
            "profit_rate": p.profit_rate
        } for p in bottom_products],
        category_analysis=[{
            "category": c.category,
            "sales_amount": c.sales_amount,
            "net_profit": c.net_profit,
            "profit_rate": c.profit_rate,
            "avg_order_value": c.avg_order_value,
            "avg_profit_per_order": c.avg_profit_per_order
        } for c in category_stats]
    ) 