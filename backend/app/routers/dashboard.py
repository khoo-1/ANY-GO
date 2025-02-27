from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"]
)

@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取仪表盘统计数据"""
    # TODO: 实现实际的统计逻辑
    return {
        "totalProducts": 0,
        "totalPackingLists": 0,
        "monthSales": 0,
        "monthProfit": 0
    }

@router.get("/trends")
async def get_trends(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取趋势数据"""
    # 生成过去30天的日期
    dates = [(datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") 
            for x in range(29, -1, -1)]
    
    # TODO: 实现实际的趋势数据查询逻辑
    return {
        "dates": dates,
        "sales": [0] * 30,  # 30天的销售数据
        "profits": [0] * 30  # 30天的利润数据
    } 