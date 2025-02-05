from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status, Response
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import pandas as pd

from ..database import get_db
from ..models.packing_list import PackingList, PackingListItem, BoxSpecs
from ..models.product import Product
from ..schemas.packing_list import (
    PackingListCreate, PackingListUpdate, PackingListResponse,
    PackingListQuery, ImportResult, ExportRequest, BatchApproveRequest,
    StoreStatistics
)
from ..auth.jwt import get_current_user, check_permission
from ..utils.excel import create_workbook, read_workbook

router = APIRouter(prefix="/api/packing-lists", tags=["装箱单"])

@router.get("/", response_model=List[PackingListResponse])
async def list_packing_lists(
    query: PackingListQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing_lists:read"))
):
    """获取装箱单列表"""
    query_filter = []
    
    if query.keyword:
        query_filter.append(PackingList.store_name.ilike(f"%{query.keyword}%"))
    if query.type:
        query_filter.append(PackingList.type == query.type)
    if query.status:
        query_filter.append(PackingList.status == query.status)
    if query.start_date:
        query_filter.append(PackingList.created_at >= query.start_date)
    if query.end_date:
        query_filter.append(PackingList.created_at <= query.end_date)
    
    total = db.query(PackingList).filter(*query_filter).count()
    packing_lists = (
        db.query(PackingList)
        .filter(*query_filter)
        .order_by(PackingList.created_at.desc())
        .offset((query.page - 1) * query.page_size)
        .limit(query.page_size)
        .all()
    )
    
    return {
        "items": packing_lists,
        "total": total,
        "page": query.page,
        "page_size": query.page_size
    }

@router.post("/", response_model=PackingListResponse)
async def create_packing_list(
    data: PackingListCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing_lists:write"))
):
    """创建装箱单"""
    # 验证产品是否存在
    product_ids = [item.product_id for item in data.items]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    if len(products) != len(product_ids):
        raise HTTPException(status_code=400, detail="存在无效的产品ID")
    
    # 创建装箱单
    packing_list = PackingList(
        store_name=data.store_name,
        type=data.type,
        remarks=data.remarks,
        total_boxes=sum(spec.total_pieces for spec in data.box_specs),
        total_weight=sum(spec.weight for spec in data.box_specs),
        total_volume=sum(spec.volume for spec in data.box_specs),
        total_pieces=sum(item.quantity for item in data.items),
        total_value=sum(
            item.quantity * next(p.price for p in products if p.id == item.product_id)
            for item in data.items
        )
    )
    db.add(packing_list)
    
    # 创建箱子规格
    for spec in data.box_specs:
        box_spec = BoxSpecs(**spec.dict(), packing_list_id=packing_list.id)
        db.add(box_spec)
    
    # 创建装箱单明细
    for item in data.items:
        product = next(p for p in products if p.id == item.product_id)
        packing_item = PackingListItem(
            packing_list_id=packing_list.id,
            product_id=item.product_id,
            quantity=item.quantity,
            box_quantities=item.box_quantities,
            weight=product.weight * item.quantity if hasattr(product, 'weight') else 0,
            volume=product.volume * item.quantity if hasattr(product, 'volume') else 0
        )
        db.add(packing_item)
    
    db.commit()
    db.refresh(packing_list)
    return packing_list

@router.get("/{id}", response_model=PackingListResponse)
async def get_packing_list(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing_lists:read"))
):
    """获取装箱单详情"""
    packing_list = db.query(PackingList).filter(PackingList.id == id).first()
    if not packing_list:
        raise HTTPException(status_code=404, detail="装箱单不存在")
    return packing_list

@router.put("/{id}", response_model=PackingListResponse)
async def update_packing_list(
    id: int,
    data: PackingListUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing_lists:write"))
):
    """更新装箱单"""
    packing_list = db.query(PackingList).filter(PackingList.id == id).first()
    if not packing_list:
        raise HTTPException(status_code=404, detail="装箱单不存在")
    
    # 更新基本信息
    for field, value in data.dict(exclude_unset=True).items():
        if field not in ['items', 'box_specs']:
            setattr(packing_list, field, value)
    
    if data.items:
        # 删除原有明细
        db.query(PackingListItem).filter(PackingListItem.packing_list_id == id).delete()
        
        # 验证产品并创建新明细
        product_ids = [item.product_id for item in data.items]
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        if len(products) != len(product_ids):
            raise HTTPException(status_code=400, detail="存在无效的产品ID")
            
        for item in data.items:
            product = next(p for p in products if p.id == item.product_id)
            packing_item = PackingListItem(
                packing_list_id=id,
                product_id=item.product_id,
                quantity=item.quantity,
                box_quantities=item.box_quantities,
                weight=product.weight * item.quantity if hasattr(product, 'weight') else 0,
                volume=product.volume * item.quantity if hasattr(product, 'volume') else 0
            )
            db.add(packing_item)
    
    if data.box_specs:
        # 删除原有箱子规格
        db.query(BoxSpecs).filter(BoxSpecs.packing_list_id == id).delete()
        
        # 创建新箱子规格
        for spec in data.box_specs:
            box_spec = BoxSpecs(**spec.dict(), packing_list_id=id)
            db.add(box_spec)
    
    # 更新汇总信息
    packing_list.total_boxes = sum(spec.total_pieces for spec in data.box_specs) if data.box_specs else packing_list.total_boxes
    packing_list.total_weight = sum(spec.weight for spec in data.box_specs) if data.box_specs else packing_list.total_weight
    packing_list.total_volume = sum(spec.volume for spec in data.box_specs) if data.box_specs else packing_list.total_volume
    packing_list.total_pieces = sum(item.quantity for item in data.items) if data.items else packing_list.total_pieces
    
    db.commit()
    db.refresh(packing_list)
    return packing_list

@router.delete("/{id}")
async def delete_packing_list(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing_lists:delete"))
):
    """删除装箱单"""
    packing_list = db.query(PackingList).filter(PackingList.id == id).first()
    if not packing_list:
        raise HTTPException(status_code=404, detail="装箱单不存在")
        
    db.delete(packing_list)
    db.commit()
    return {"message": "删除成功"}

@router.post("/import", response_model=ImportResult)
async def import_packing_lists(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing_lists:write"))
):
    """导入装箱单"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="仅支持Excel文件")
    
    try:
        # 读取Excel文件
        df = read_workbook(file.file)
        parsed_data = parse_packing_list(df)
        
        result = ImportResult(
            success=True,
            message="导入成功",
            total=len(parsed_data)
        )
        
        # 处理每个装箱单
        for data in parsed_data:
            try:
                # 查找或创建产品
                product = db.query(Product).filter(Product.sku == data['sku']).first()
                if not product:
                    product = Product(
                        sku=data['sku'],
                        name=data['sku'],
                        chinese_name=f"待补充({data['sku']})",
                        type=data['type'],
                        is_auto_created=True,
                        needs_completion=True
                    )
                    db.add(product)
                    db.flush()
                    result.created += 1
                
                # 创建装箱单
                packing_list = PackingList(
                    store_name=data['store_name'],
                    type=data['type'],
                    remarks=data['remarks'],
                    total_boxes=len(data['box_quantities']),
                    total_pieces=data['quantity'],
                    total_weight=0,  # 需要根据实际情况计算
                    total_volume=0,  # 需要根据实际情况计算
                    total_value=data['quantity'] * (product.price or 0)
                )
                db.add(packing_list)
                db.flush()
                
                # 创建装箱单明细
                packing_item = PackingListItem(
                    packing_list_id=packing_list.id,
                    product_id=product.id,
                    quantity=data['quantity'],
                    box_quantities=data['box_quantities']
                )
                db.add(packing_item)
                
                result.updated += 1
                
            except Exception as e:
                result.failed += 1
                result.errors.append(f"处理 {data['sku']} 失败: {str(e)}")
        
        db.commit()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"导入失败: {str(e)}")

@router.post("/export")
async def export_packing_lists(
    data: ExportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing_lists:read"))
):
    """导出装箱单"""
    packing_lists = (
        db.query(PackingList)
        .filter(PackingList.id.in_(data.ids))
        .options(
            joinedload(PackingList.items).joinedload(PackingListItem.product)
        )
        .all()
    )
    
    if not packing_lists:
        raise HTTPException(status_code=404, detail="未找到指定的装箱单")
    
    # 准备导出数据
    export_data = []
    for pl in packing_lists:
        for item in pl.items:
            item_data = {
                'store_name': pl.store_name,
                'type': pl.type,
                'sku': item.product.sku,
                'chinese_name': item.product.chinese_name,
                'quantity': item.quantity,
                'weight': item.weight,
                'volume': item.volume,
                'remarks': pl.remarks,
                'box_quantities': item.box_quantities
            }
            export_data.append(item_data)
    
    # 创建Excel文件
    excel_data = create_workbook(export_data, "packing_list")
    
    # 设置响应头
    headers = {
        'Content-Disposition': f'attachment; filename=packing_lists_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    return Response(content=excel_data, headers=headers)

@router.post("/batch-approve")
async def batch_approve(
    data: BatchApproveRequest,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing_lists:write"))
):
    """批量审批装箱单"""
    packing_lists = db.query(PackingList).filter(PackingList.id.in_(data.ids)).all()
    if not packing_lists:
        raise HTTPException(status_code=404, detail="未找到指定的装箱单")
    
    for pl in packing_lists:
        pl.status = "approved" if data.action == "approve" else "pending"
    
    db.commit()
    return {"message": f"已{data.action}选中的装箱单"}

@router.get("/statistics/store", response_model=List[StoreStatistics])
async def get_store_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing_lists:read"))
):
    """获取店铺统计信息"""
    query = db.query(PackingList)
    
    if start_date:
        query = query.filter(PackingList.created_at >= start_date)
    if end_date:
        query = query.filter(PackingList.created_at <= end_date)
    
    stats = []
    for store_name, group in query.group_by(PackingList.store_name):
        total_lists = group.count()
        total_products = sum(len(pl.items) for pl in group)
        total_pieces = sum(pl.total_pieces for pl in group)
        total_boxes = sum(pl.total_boxes for pl in group)
        total_value = sum(pl.total_value for pl in group)
        
        stats.append(StoreStatistics(
            store_name=store_name,
            total_lists=total_lists,
            total_products=total_products,
            total_pieces=total_pieces,
            total_boxes=total_boxes,
            total_value=total_value
        ))
    
    return stats 