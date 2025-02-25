from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import date, datetime, timedelta

from ..models.stock import StockTimeline, StockRecord, TransitStock
from ..models.product import Product
from ..schemas.stock import StockTimelineQuery

def get_stock_timeline(db: Session, query: StockTimelineQuery) -> List[StockTimeline]:
    """获取库存时间线记录"""
    filters = []
    if query.product_id:
        filters.append(StockTimeline.product_id == query.product_id)
    if query.start_date:
        filters.append(StockTimeline.date >= query.start_date)
    if query.end_date:
        filters.append(StockTimeline.date <= query.end_date)

    records = (
        db.query(StockTimeline)
        .join(Product)
        .filter(and_(*filters))
        .order_by(StockTimeline.date.desc())
        .offset(query.skip)
        .limit(query.limit)
        .all()
    )
    return records

def generate_timeline(db: Session, start_date: date, end_date: date):
    """生成指定时间范围的库存时间线"""
    # 获取所有产品
    products = db.query(Product).all()
    
    current_date = start_date
    while current_date <= end_date:
        for product in products:
            # 获取前一天的记录
            prev_record = (
                db.query(StockTimeline)
                .filter(
                    StockTimeline.product_id == product.id,
                    StockTimeline.date == current_date - timedelta(days=1)
                )
                .first()
            )
            
            # 获取当天的库存变动
            stock_changes = (
                db.query(StockRecord)
                .filter(
                    StockRecord.product_id == product.id,
                    StockRecord.operation_date == current_date
                )
                .all()
            )
            
            # 获取在途库存
            transit_stock = (
                db.query(TransitStock)
                .filter(
                    TransitStock.product_id == product.id,
                    TransitStock.status == "in_transit",
                    TransitStock.shipping_date <= current_date,
                    or_(
                        TransitStock.estimated_arrival > current_date,
                        TransitStock.estimated_arrival == None
                    )
                )
                .all()
            )
            
            # 计算当天的库存变动
            incoming = sum(record.quantity for record in stock_changes if record.operation_type == "IN")
            outgoing = sum(record.quantity for record in stock_changes if record.operation_type == "OUT")
            adjustments = sum(record.quantity for record in stock_changes if record.operation_type == "ADJUST")
            
            # 计算在途库存
            in_transit = sum(record.quantity for record in transit_stock)
            transit_details = [
                {
                    "packing_list_id": record.packing_list_id,
                    "quantity": record.quantity,
                    "shipping_date": record.shipping_date,
                    "estimated_arrival": record.estimated_arrival,
                    "transport_type": record.transport_type
                }
                for record in transit_stock
            ]
            
            # 计算期初和期末库存
            opening_stock = prev_record.closing_stock if prev_record else 0
            closing_stock = opening_stock + incoming - outgoing + adjustments
            
            # 创建或更新时间线记录
            timeline = (
                db.query(StockTimeline)
                .filter(
                    StockTimeline.product_id == product.id,
                    StockTimeline.date == current_date
                )
                .first()
            )
            
            if timeline:
                timeline.opening_stock = opening_stock
                timeline.closing_stock = closing_stock
                timeline.in_transit = in_transit
                timeline.in_transit_details = transit_details
                timeline.incoming = incoming
                timeline.outgoing = outgoing
                timeline.adjustments = adjustments
            else:
                timeline = StockTimeline(
                    product_id=product.id,
                    date=current_date,
                    opening_stock=opening_stock,
                    closing_stock=closing_stock,
                    in_transit=in_transit,
                    in_transit_details=transit_details,
                    incoming=incoming,
                    outgoing=outgoing,
                    adjustments=adjustments
                )
                db.add(timeline)
        
        db.commit()
        current_date += timedelta(days=1) 