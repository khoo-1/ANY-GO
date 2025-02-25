from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict
from datetime import date

from ..models.stock import TransitStock
from ..models.product import Product
from ..models.packing import PackingList
from ..schemas.stock import TransitStockCreate, TransitStockQuery

def get_transit_stock(db: Session, query: TransitStockQuery) -> List[TransitStock]:
    """获取在途库存记录"""
    filters = []
    if query.product_id:
        filters.append(TransitStock.product_id == query.product_id)
    if query.packing_list_id:
        filters.append(TransitStock.packing_list_id == query.packing_list_id)
    if query.transport_type:
        filters.append(TransitStock.transport_type == query.transport_type)
    if query.status:
        filters.append(TransitStock.status == query.status)
    if query.start_date:
        filters.append(TransitStock.shipping_date >= query.start_date)
    if query.end_date:
        filters.append(TransitStock.shipping_date <= query.end_date)

    records = (
        db.query(TransitStock)
        .join(Product)
        .join(PackingList)
        .filter(and_(*filters))
        .order_by(TransitStock.shipping_date.desc())
        .offset(query.skip)
        .limit(query.limit)
        .all()
    )
    return records

def create_transit_stock(db: Session, data: TransitStockCreate) -> TransitStock:
    """创建在途库存记录"""
    # 检查产品是否存在
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise ValueError("产品不存在")
    
    # 检查装箱单是否存在
    packing_list = db.query(PackingList).filter(PackingList.id == data.packing_list_id).first()
    if not packing_list:
        raise ValueError("装箱单不存在")
    
    # 创建在途库存记录
    record = TransitStock(**data.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def update_transit_status(db: Session, id: int, status: str):
    """更新在途库存状态"""
    record = db.query(TransitStock).filter(TransitStock.id == id).first()
    if not record:
        raise ValueError("在途库存记录不存在")
    
    record.status = status
    if status == "arrived":
        record.arrival_date = date.today()
    
    db.commit()
    db.refresh(record)
    return record

def get_transit_summary(db: Session, product_id: Optional[int] = None) -> Dict:
    """获取在途库存汇总信息"""
    query = db.query(
        TransitStock.transport_type,
        func.sum(TransitStock.quantity).label("total_quantity"),
        func.count(TransitStock.id).label("record_count")
    ).filter(TransitStock.status == "in_transit")
    
    if product_id:
        query = query.filter(TransitStock.product_id == product_id)
    
    summary = query.group_by(TransitStock.transport_type).all()
    
    result = {
        "total": {
            "quantity": 0,
            "record_count": 0
        },
        "by_transport_type": {}
    }
    
    for transport_type, quantity, count in summary:
        result["total"]["quantity"] += quantity
        result["total"]["record_count"] += count
        result["by_transport_type"][transport_type] = {
            "quantity": quantity,
            "record_count": count
        }
    
    return result 