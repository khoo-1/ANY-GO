from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from datetime import datetime, date, timedelta

from ..database import get_db
from ..models.sales import Order, OrderItem, SalesStatistics
from ..models.product import Product
from ..schemas.sales import (
    OrderCreate, OrderUpdate, OrderResponse, OrderQuery,
    SalesStatisticsCreate, SalesStatisticsUpdate, SalesStatisticsResponse,
    SalesQuery, SalesSummary
)
from ..auth.jwt import check_permission

router = APIRouter(prefix="/sales", tags=["销售管理"])

# 订单相关接口
@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    query: OrderQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("sales:read"))
):
    """获取订单列表"""
    orders_query = db.query(Order)
    
    if query.keyword:
        orders_query = orders_query.filter(
            Order.order_no.ilike(f"%{query.keyword}%") |
            Order.customer_name.ilike(f"%{query.keyword}%") |
            Order.customer_email.ilike(f"%{query.keyword}%")
        )
    
    if query.store_name:
        orders_query = orders_query.filter(Order.store_name == query.store_name)
        
    if query.platform:
        orders_query = orders_query.filter(Order.platform == query.platform)
        
    if query.status:
        orders_query = orders_query.filter(Order.status == query.status)
        
    if query.payment_status:
        orders_query = orders_query.filter(Order.payment_status == query.payment_status)
        
    if query.start_date:
        orders_query = orders_query.filter(Order.order_date >= query.start_date)
        
    if query.end_date:
        orders_query = orders_query.filter(Order.order_date <= query.end_date)
        
    if query.operator_id:
        orders_query = orders_query.filter(Order.operator_id == query.operator_id)
    
    total = orders_query.count()
    orders = orders_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return orders

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("sales:write"))
):
    """创建订单"""
    # 生成订单编号
    order_no = f"SO{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 计算订单金额
    subtotal = sum(item.quantity * item.unit_price for item in data.items)
    total = subtotal + data.shipping_fee + data.tax - data.discount
    
    # 创建订单
    order = Order(
        **data.dict(exclude={'items'}),
        order_no=order_no,
        subtotal=subtotal,
        total=total,
        operator_id=current_user.id
    )
    
    db.add(order)
    db.flush()  # 获取订单ID
    
    # 创建订单明细
    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"产品ID {item_data.product_id} 不存在")
        
        # 计算明细金额
        item_subtotal = item_data.quantity * item_data.unit_price
        item_total = item_subtotal + item_data.tax - item_data.discount
        
        # 创建明细
        item = OrderItem(
            order_id=order.id,
            **item_data.dict(),
            subtotal=item_subtotal,
            total=item_total,
            sku=product.sku,
            product_name=product.name
        )
        
        db.add(item)
        
        # 更新库存
        product.stock -= item_data.quantity
        if product.stock < 0:
            raise HTTPException(status_code=400, detail=f"产品 {product.name} 库存不足")
    
    db.commit()
    db.refresh(order)
    
    return order

@router.get("/orders/{id}", response_model=OrderResponse)
async def get_order(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("sales:read"))
):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order

@router.put("/orders/{id}", response_model=OrderResponse)
async def update_order(
    id: int,
    data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("sales:write"))
):
    """更新订单"""
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 如果订单已完成或取消，不允许修改
    if order.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="订单已完成或取消，无法修改")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(order, key, value)
    
    db.commit()
    db.refresh(order)
    return order

# 销售统计相关接口
@router.get("/statistics", response_model=List[SalesStatisticsResponse])
async def list_sales_statistics(
    query: SalesQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("sales:read"))
):
    """获取销售统计列表"""
    stats_query = db.query(SalesStatistics)
    
    if query.store_name:
        stats_query = stats_query.filter(SalesStatistics.store_name == query.store_name)
        
    if query.platform:
        stats_query = stats_query.filter(SalesStatistics.platform == query.platform)
        
    if query.start_date:
        stats_query = stats_query.filter(SalesStatistics.date >= query.start_date)
        
    if query.end_date:
        stats_query = stats_query.filter(SalesStatistics.date <= query.end_date)
    
    total = stats_query.count()
    stats = stats_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return stats

@router.post("/statistics/calculate")
async def calculate_sales_statistics(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("sales:write"))
):
    """计算指定日期范围的销售统计"""
    current_date = start_date
    while current_date <= end_date:
        # 按店铺和平台分组计算统计数据
        stats_data = db.query(
            Order.store_name,
            Order.platform,
            func.count(Order.id).label("order_count"),
            func.sum(case((Order.status == "completed", 1), else_=0)).label("completed_order_count"),
            func.sum(case((Order.status == "cancelled", 1), else_=0)).label("cancelled_order_count"),
            func.sum(Order.total).label("total_sales"),
            func.sum(Order.shipping_fee).label("shipping_fee"),
            func.sum(Order.tax).label("tax"),
            func.sum(Order.discount).label("discount")
        ).filter(
            Order.order_date == current_date
        ).group_by(
            Order.store_name,
            Order.platform
        ).all()
        
        for store_name, platform, order_count, completed_count, cancelled_count, total_sales, shipping_fee, tax, discount in stats_data:
            # 计算商品统计
            items_data = db.query(
                func.sum(OrderItem.quantity).label("total_items"),
                func.count(distinct(OrderItem.product_id)).label("unique_items"),
                func.sum(OrderItem.quantity * Product.cost).label("total_cost")
            ).join(
                Order, OrderItem.order_id == Order.id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).filter(
                Order.order_date == current_date,
                Order.store_name == store_name,
                Order.platform == platform
            ).first()
            
            # 计算平均订单金额和转化率
            average_order_value = total_sales / order_count if order_count > 0 else 0
            conversion_rate = completed_count / order_count if order_count > 0 else 0
            
            # 创建或更新统计记录
            stats = db.query(SalesStatistics).filter(
                SalesStatistics.date == current_date,
                SalesStatistics.store_name == store_name,
                SalesStatistics.platform == platform
            ).first()
            
            if stats:
                # 更新现有记录
                stats.order_count = order_count
                stats.completed_order_count = completed_count
                stats.cancelled_order_count = cancelled_count
                stats.total_sales = total_sales
                stats.total_cost = items_data.total_cost
                stats.gross_profit = total_sales - items_data.total_cost
                stats.shipping_fee = shipping_fee
                stats.tax = tax
                stats.discount = discount
                stats.total_items = items_data.total_items
                stats.unique_items = items_data.unique_items
                stats.average_order_value = average_order_value
                stats.conversion_rate = conversion_rate
            else:
                # 创建新记录
                stats = SalesStatistics(
                    date=current_date,
                    store_name=store_name,
                    platform=platform,
                    order_count=order_count,
                    completed_order_count=completed_count,
                    cancelled_order_count=cancelled_count,
                    total_sales=total_sales,
                    total_cost=items_data.total_cost,
                    gross_profit=total_sales - items_data.total_cost,
                    shipping_fee=shipping_fee,
                    tax=tax,
                    discount=discount,
                    total_items=items_data.total_items,
                    unique_items=items_data.unique_items,
                    average_order_value=average_order_value,
                    conversion_rate=conversion_rate
                )
                db.add(stats)
        
        current_date += timedelta(days=1)
    
    db.commit()
    return {"message": "销售统计计算完成"}

@router.get("/summary", response_model=SalesSummary)
async def get_sales_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    store_name: Optional[str] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("sales:read"))
):
    """获取销售汇总信息"""
    # 构建基础查询条件
    conditions = []
    if start_date:
        conditions.append(Order.order_date >= start_date)
    if end_date:
        conditions.append(Order.order_date <= end_date)
    if store_name:
        conditions.append(Order.store_name == store_name)
    if platform:
        conditions.append(Order.platform == platform)
    
    # 获取订单汇总数据
    order_summary = db.query(
        func.count(Order.id).label("total_orders"),
        func.sum(Order.total).label("total_sales")
    ).filter(*conditions).first()
    
    # 获取利润汇总数据
    profit_summary = db.query(
        func.sum(OrderItem.quantity * (OrderItem.unit_price - Product.cost)).label("total_profit")
    ).join(
        Order, OrderItem.order_id == Order.id
    ).join(
        Product, OrderItem.product_id == Product.id
    ).filter(*conditions).first()
    
    # 获取热销商品
    top_products = db.query(
        Product.id,
        Product.sku,
        Product.name,
        func.sum(OrderItem.quantity).label("total_quantity"),
        func.sum(OrderItem.total).label("total_amount")
    ).join(
        OrderItem, Product.id == OrderItem.product_id
    ).join(
        Order, OrderItem.order_id == Order.id
    ).filter(*conditions).group_by(
        Product.id
    ).order_by(
        desc("total_amount")
    ).limit(10).all()
    
    # 获取热门店铺
    top_stores = db.query(
        Order.store_name,
        Order.platform,
        func.count(Order.id).label("order_count"),
        func.sum(Order.total).label("total_sales")
    ).filter(*conditions).group_by(
        Order.store_name,
        Order.platform
    ).order_by(
        desc("total_sales")
    ).limit(10).all()
    
    # 计算平均订单金额和转化率
    average_order_value = order_summary.total_sales / order_summary.total_orders if order_summary.total_orders > 0 else 0
    conversion_rate = db.query(
        func.count(case((Order.status == "completed", 1), else_=None)) * 100.0 / func.count(Order.id)
    ).filter(*conditions).scalar() or 0
    
    return SalesSummary(
        total_orders=order_summary.total_orders,
        total_sales=order_summary.total_sales,
        total_profit=profit_summary.total_profit,
        average_order_value=average_order_value,
        conversion_rate=conversion_rate,
        top_products=[{
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "total_quantity": p.total_quantity,
            "total_amount": p.total_amount
        } for p in top_products],
        top_stores=[{
            "store_name": s.store_name,
            "platform": s.platform,
            "order_count": s.order_count,
            "total_sales": s.total_sales
        } for s in top_stores]
    ) 