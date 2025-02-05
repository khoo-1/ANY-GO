from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.stock import StockRecord, StockCheck, StockCheckItem, StockAlert
from ..models.product import Product
from ..schemas.stock import (
    StockRecordCreate, StockRecordUpdate, StockRecordResponse,
    StockCheckCreate, StockCheckUpdate, StockCheckResponse,
    StockCheckItemCreate, StockCheckItemUpdate, StockCheckItemResponse,
    StockAlertCreate, StockAlertUpdate, StockAlertResponse,
    StockQuery, StockCheckQuery, StockAlertQuery, StockSummary
)
from ..auth.jwt import check_permission

router = APIRouter(prefix="/stock", tags=["库存管理"])

# 库存记录相关接口
@router.get("/records", response_model=List[StockRecordResponse])
async def list_stock_records(
    query: StockQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:read"))
):
    """获取库存记录列表"""
    records_query = db.query(StockRecord)
    
    if query.keyword:
        records_query = records_query.join(Product).filter(
            Product.sku.ilike(f"%{query.keyword}%") |
            Product.name.ilike(f"%{query.keyword}%")
        )
    
    if query.operation_type:
        records_query = records_query.filter(StockRecord.operation_type == query.operation_type)
    
    if query.warehouse:
        records_query = records_query.filter(StockRecord.warehouse == query.warehouse)
        
    if query.start_date:
        records_query = records_query.filter(StockRecord.created_at >= query.start_date)
        
    if query.end_date:
        records_query = records_query.filter(StockRecord.created_at <= query.end_date)
        
    if query.product_id:
        records_query = records_query.filter(StockRecord.product_id == query.product_id)
        
    if query.batch_number:
        records_query = records_query.filter(StockRecord.batch_number == query.batch_number)
    
    total = records_query.count()
    records = records_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return records

@router.post("/records", response_model=StockRecordResponse)
async def create_stock_record(
    data: StockRecordCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:write"))
):
    """创建库存记录"""
    # 获取产品信息
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 计算库存变动
    previous_stock = product.stock
    if data.operation_type == "入库":
        current_stock = previous_stock + data.quantity
    elif data.operation_type == "出库":
        if previous_stock < data.quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        current_stock = previous_stock - data.quantity
    else:  # 调整或盘点
        current_stock = data.quantity
    
    # 计算总金额
    total_amount = None
    if data.unit_price is not None:
        total_amount = data.unit_price * abs(data.quantity)
    
    # 创建库存记录
    record = StockRecord(
        **data.dict(),
        previous_stock=previous_stock,
        current_stock=current_stock,
        total_amount=total_amount,
        operator_id=current_user.id
    )
    
    # 更新产品库存
    product.stock = current_stock
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record

@router.get("/records/{id}", response_model=StockRecordResponse)
async def get_stock_record(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:read"))
):
    """获取库存记录详情"""
    record = db.query(StockRecord).filter(StockRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    return record

@router.put("/records/{id}", response_model=StockRecordResponse)
async def update_stock_record(
    id: int,
    data: StockRecordUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:write"))
):
    """更新库存记录"""
    record = db.query(StockRecord).filter(StockRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)
    
    db.commit()
    db.refresh(record)
    return record

# 库存盘点相关接口
@router.get("/checks", response_model=List[StockCheckResponse])
async def list_stock_checks(
    query: StockCheckQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:read"))
):
    """获取库存盘点列表"""
    checks_query = db.query(StockCheck)
    
    if query.status:
        checks_query = checks_query.filter(StockCheck.status == query.status)
        
    if query.warehouse:
        checks_query = checks_query.filter(StockCheck.warehouse == query.warehouse)
        
    if query.start_date:
        checks_query = checks_query.filter(StockCheck.created_at >= query.start_date)
        
    if query.end_date:
        checks_query = checks_query.filter(StockCheck.created_at <= query.end_date)
        
    if query.operator_id:
        checks_query = checks_query.filter(StockCheck.operator_id == query.operator_id)
    
    total = checks_query.count()
    checks = checks_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return checks

@router.post("/checks", response_model=StockCheckResponse)
async def create_stock_check(
    data: StockCheckCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:write"))
):
    """创建库存盘点"""
    # 生成盘点单号
    check_no = f"SC{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 创建盘点记录
    check = StockCheck(
        **data.dict(),
        check_no=check_no,
        operator_id=current_user.id,
        start_time=datetime.now().isoformat()
    )
    
    db.add(check)
    db.commit()
    db.refresh(check)
    
    return check

@router.get("/checks/{id}", response_model=StockCheckResponse)
async def get_stock_check(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:read"))
):
    """获取库存盘点详情"""
    check = db.query(StockCheck).filter(StockCheck.id == id).first()
    if not check:
        raise HTTPException(status_code=404, detail="库存盘点不存在")
    return check

@router.put("/checks/{id}", response_model=StockCheckResponse)
async def update_stock_check(
    id: int,
    data: StockCheckUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:write"))
):
    """更新库存盘点"""
    check = db.query(StockCheck).filter(StockCheck.id == id).first()
    if not check:
        raise HTTPException(status_code=404, detail="库存盘点不存在")
    
    # 如果状态变更为已完成，设置结束时间和审核人
    if data.status == "completed" and check.status != "completed":
        data.end_time = datetime.now().isoformat()
        data.checker_id = current_user.id
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(check, key, value)
    
    db.commit()
    db.refresh(check)
    return check

@router.post("/checks/{id}/items", response_model=StockCheckItemResponse)
async def add_check_item(
    id: int,
    data: StockCheckItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:write"))
):
    """添加盘点明细"""
    check = db.query(StockCheck).filter(StockCheck.id == id).first()
    if not check:
        raise HTTPException(status_code=404, detail="库存盘点不存在")
    
    if check.status == "completed":
        raise HTTPException(status_code=400, detail="盘点已完成，无法添加明细")
    
    # 获取产品信息
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 计算差异
    difference = data.actual_stock - product.stock
    
    # 计算差异金额
    total_amount = None
    if product.cost:
        total_amount = difference * product.cost
    
    # 创建盘点明细
    item = StockCheckItem(
        **data.dict(),
        check_id=id,
        system_stock=product.stock,
        difference=difference,
        unit_price=product.cost,
        total_amount=total_amount
    )
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item

@router.put("/checks/{check_id}/items/{item_id}", response_model=StockCheckItemResponse)
async def update_check_item(
    check_id: int,
    item_id: int,
    data: StockCheckItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:write"))
):
    """更新盘点明细"""
    item = db.query(StockCheckItem).filter(
        StockCheckItem.id == item_id,
        StockCheckItem.check_id == check_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="盘点明细不存在")
    
    if item.stock_check.status == "completed":
        raise HTTPException(status_code=400, detail="盘点已完成，无法修改明细")
    
    # 如果修改了实际库存，重新计算差异
    if data.actual_stock is not None:
        data.difference = data.actual_stock - item.system_stock
        if item.unit_price:
            data.total_amount = data.difference * item.unit_price
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/checks/{check_id}/items/{item_id}")
async def delete_check_item(
    check_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:write"))
):
    """删除盘点明细"""
    item = db.query(StockCheckItem).filter(
        StockCheckItem.id == item_id,
        StockCheckItem.check_id == check_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="盘点明细不存在")
    
    if item.stock_check.status == "completed":
        raise HTTPException(status_code=400, detail="盘点已完成，无法删除明细")
    
    db.delete(item)
    db.commit()
    
    return {"message": "删除成功"}

# 库存预警相关接口
@router.get("/alerts", response_model=List[StockAlertResponse])
async def list_stock_alerts(
    query: StockAlertQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:read"))
):
    """获取库存预警列表"""
    alerts_query = db.query(StockAlert)
    
    if query.alert_type:
        alerts_query = alerts_query.filter(StockAlert.alert_type == query.alert_type)
        
    if query.status:
        alerts_query = alerts_query.filter(StockAlert.status == query.status)
        
    if query.product_id:
        alerts_query = alerts_query.filter(StockAlert.product_id == query.product_id)
        
    if query.start_date:
        alerts_query = alerts_query.filter(StockAlert.created_at >= query.start_date)
        
    if query.end_date:
        alerts_query = alerts_query.filter(StockAlert.created_at <= query.end_date)
    
    total = alerts_query.count()
    alerts = alerts_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
    
    return alerts

@router.post("/alerts", response_model=StockAlertResponse)
async def create_stock_alert(
    data: StockAlertCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:write"))
):
    """创建库存预警"""
    # 检查产品是否存在
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 创建预警记录
    alert = StockAlert(**data.dict())
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return alert

@router.put("/alerts/{id}", response_model=StockAlertResponse)
async def update_stock_alert(
    id: int,
    data: StockAlertUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:write"))
):
    """更新库存预警"""
    alert = db.query(StockAlert).filter(StockAlert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="库存预警不存在")
    
    # 如果状态变更为已解决，设置解决时间和处理人
    if data.status == "resolved" and alert.status != "resolved":
        data.resolved_time = datetime.now().isoformat()
        data.resolver_id = current_user.id
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(alert, key, value)
    
    db.commit()
    db.refresh(alert)
    return alert

@router.get("/summary", response_model=StockSummary)
async def get_stock_summary(
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("stock:read"))
):
    """获取库存汇总信息"""
    # 获取产品总数
    total_products = db.query(Product).count()
    
    # 获取库存总数和总金额
    stock_summary = db.query(
        func.sum(Product.stock).label("total_quantity"),
        func.sum(Product.stock * Product.cost).label("total_amount")
    ).first()
    
    # 获取活动预警数量
    alert_count = db.query(StockAlert).filter(StockAlert.status == "active").count()
    
    # 获取进行中的盘点数量
    check_count = db.query(StockCheck).filter(StockCheck.status != "completed").count()
    
    return StockSummary(
        total_products=total_products,
        total_quantity=stock_summary.total_quantity or 0,
        total_amount=stock_summary.total_amount or 0,
        alert_count=alert_count,
        check_count=check_count
    ) 