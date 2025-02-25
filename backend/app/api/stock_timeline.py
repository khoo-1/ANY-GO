from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from ..core.deps import get_db
from ..crud import stock_timeline as crud_timeline
from ..crud import transit_stock as crud_transit
from ..schemas.stock import (
    StockTimelineResponse, StockTimelineCreate, StockTimelineQuery,
    TransitStockResponse, TransitStockCreate, TransitStockQuery
)

router = APIRouter()

@router.get("/timeline", response_model=List[StockTimelineResponse])
def get_stock_timeline(
    db: Session = Depends(get_db),
    query: StockTimelineQuery = Depends()
):
    """获取库存时间线记录"""
    records = crud_timeline.get_stock_timeline(db, query)
    return records

@router.post("/timeline/generate")
def generate_stock_timeline(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """生成指定时间范围的库存时间线"""
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="时间范围不能超过一年")
    
    crud_timeline.generate_timeline(db, start_date, end_date)
    return {"message": "库存时间线生成成功"}

@router.get("/transit", response_model=List[TransitStockResponse])
def get_transit_stock(
    db: Session = Depends(get_db),
    query: TransitStockQuery = Depends()
):
    """获取在途库存记录"""
    records = crud_transit.get_transit_stock(db, query)
    return records

@router.post("/transit", response_model=TransitStockResponse)
def create_transit_stock(
    data: TransitStockCreate,
    db: Session = Depends(get_db)
):
    """创建在途库存记录"""
    record = crud_transit.create_transit_stock(db, data)
    return record

@router.put("/transit/{id}/status")
def update_transit_status(
    id: int,
    status: str = Query(..., pattern="^(in_transit|arrived|cancelled)$"),
    db: Session = Depends(get_db)
):
    """更新在途库存状态"""
    crud_transit.update_transit_status(db, id, status)
    return {"message": "状态更新成功"}

@router.get("/transit/summary")
def get_transit_summary(
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取在途库存汇总信息"""
    summary = crud_transit.get_transit_summary(db, product_id)
    return summary 