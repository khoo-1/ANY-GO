from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.database import get_db
from app.models import PackingList, Product
from app.auth.session import get_current_user  # 使用session认证
from app.models import User as UserModel

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"]
)

@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)  # 使用session认证
):
    """获取统计数据"""
    try:
        # 获取装箱单总数
        total_packing_lists = db.query(func.count(PackingList.id)).scalar() or 0
        
        # 获取商品总数
        total_products = db.query(func.count(Product.id)).scalar() or 0
        
        # 获取最近7天的装箱单数量
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_packing_lists = db.query(func.count(PackingList.id)).filter(
            PackingList.created_at >= seven_days_ago
        ).scalar() or 0
        
        # 获取最近7天的商品数量
        recent_products = db.query(func.count(Product.id)).filter(
            Product.created_at >= seven_days_ago
        ).scalar() or 0
        
        return {
            "total_packing_lists": total_packing_lists,
            "total_products": total_products,
            "recent_packing_lists": recent_packing_lists,
            "recent_products": recent_products
        }
    except Exception as e:
        print(f"获取统计数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )

@router.get("/trends")
async def get_trends(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)  # 使用session认证
):
    """获取趋势数据"""
    try:
        # 获取最近7天的数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # 按日期分组统计装箱单数量
        packing_trends = db.query(
            func.date(PackingList.created_at).label('date'),
            func.count(PackingList.id).label('count')
        ).filter(
            PackingList.created_at >= start_date,
            PackingList.created_at <= end_date
        ).group_by(
            func.date(PackingList.created_at)
        ).all()
        
        # 按日期分组统计商品数量
        product_trends = db.query(
            func.date(Product.created_at).label('date'),
            func.count(Product.id).label('count')
        ).filter(
            Product.created_at >= start_date,
            Product.created_at <= end_date
        ).group_by(
            func.date(Product.created_at)
        ).all()
        
        # 格式化数据
        packing_data = {str(row.date): row.count for row in packing_trends}
        product_data = {str(row.date): row.count for row in product_trends}
        
        # 生成日期列表
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_str = str(current_date.date())
            date_list.append({
                'date': date_str,
                'packing_count': packing_data.get(date_str, 0),
                'product_count': product_data.get(date_str, 0)
            })
            current_date += timedelta(days=1)
        
        return date_list
    except Exception as e:
        print(f"获取趋势数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取趋势数据失败: {str(e)}"
        ) 