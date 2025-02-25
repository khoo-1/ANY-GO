from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.packing import PackingList, PackingListItem, BoxQuantity, BoxSpecs
from ..models.product import Product
from ..schemas.packing import (
    PackingListCreate,
    PackingListUpdate,
    PackingListResponse,
    ImportResult,
    ExportRequest
)
from ..auth.jwt import check_permission

router = APIRouter(prefix="/packing-lists", tags=["packing-lists"])

@router.post("", response_model=PackingListResponse)
async def create_packing_list(
    data: PackingListCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing-lists:write"))
):
    """
    创建装箱单
    """
    try:
        # 验证商品是否存在且有效
        for item in data.items:
            product = db.query(Product).filter(
                Product.id == item.product_id,
                Product.status == "active"
            ).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"商品ID {item.product_id} 不存在或已停用"
                )

        # 创建装箱单
        packing_list = PackingList(
            store_name=data.store_name,
            type=data.type,
            remarks=data.remarks,
            status="pending",
            created_by=current_user.id
        )
        db.add(packing_list)
        db.flush()

        # 创建商品明细
        for item_data in data.items:
            item = PackingListItem(
                packing_list_id=packing_list.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity
            )
            db.add(item)
            db.flush()

            # 创建装箱数量
            for box_data in item_data.box_quantities:
                box = BoxQuantity(
                    packing_list_item_id=item.id,
                    box_no=box_data.box_no,
                    quantity=box_data.quantity,
                    specs=box_data.specs
                )
                db.add(box)

        # 创建箱子规格
        for spec_data in data.box_specs:
            spec = BoxSpecs(
                packing_list_id=packing_list.id,
                length=spec_data.length,
                width=spec_data.width,
                height=spec_data.height,
                weight=spec_data.weight,
                volume=spec_data.volume,
                edge_volume=spec_data.edge_volume,
                total_pieces=spec_data.total_pieces
            )
            db.add(spec)

        db.commit()
        db.refresh(packing_list)
        return packing_list

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数据完整性错误，请检查输入数据"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{id}", response_model=PackingListResponse)
async def update_packing_list(
    id: int,
    data: PackingListUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing-lists:write"))
):
    """
    更新装箱单
    """
    try:
        # 查找装箱单
        packing_list = db.query(PackingList).filter(PackingList.id == id).first()
        if not packing_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="装箱单不存在"
            )

        # 检查状态
        if packing_list.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能修改待审核状态的装箱单"
            )

        # 更新基本信息
        for field, value in data.dict(exclude_unset=True).items():
            setattr(packing_list, field, value)

        # 更新商品明细
        if data.items is not None:
            # 删除原有明细
            db.query(PackingListItem).filter(
                PackingListItem.packing_list_id == id
            ).delete()

            # 创建新明细
            for item_data in data.items:
                # 验证商品
                product = db.query(Product).filter(
                    Product.id == item_data.product_id,
                    Product.status == "active"
                ).first()
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"商品ID {item_data.product_id} 不存在或已停用"
                    )

                item = PackingListItem(
                    packing_list_id=id,
                    product_id=item_data.product_id,
                    quantity=item_data.quantity
                )
                db.add(item)
                db.flush()

                # 创建装箱数量
                for box_data in item_data.box_quantities:
                    box = BoxQuantity(
                        packing_list_item_id=item.id,
                        box_no=box_data.box_no,
                        quantity=box_data.quantity,
                        specs=box_data.specs
                    )
                    db.add(box)

        # 更新箱子规格
        if data.box_specs is not None:
            # 删除原有规格
            db.query(BoxSpecs).filter(
                BoxSpecs.packing_list_id == id
            ).delete()

            # 创建新规格
            for spec_data in data.box_specs:
                spec = BoxSpecs(
                    packing_list_id=id,
                    length=spec_data.length,
                    width=spec_data.width,
                    height=spec_data.height,
                    weight=spec_data.weight,
                    volume=spec_data.volume,
                    edge_volume=spec_data.edge_volume,
                    total_pieces=spec_data.total_pieces
                )
                db.add(spec)

        db.commit()
        db.refresh(packing_list)
        return packing_list

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数据完整性错误，请检查输入数据"
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/import", response_model=ImportResult)
async def import_packing_lists(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing-lists:write"))
):
    """
    从Excel导入装箱单
    """
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # 验证Excel格式
        required_columns = ['店铺名称', '类型', '商品SKU', '数量', '箱号', '装箱数量']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return ImportResult(
                success=False,
                error=f"Excel缺少必要列: {', '.join(missing_columns)}"
            )
        
        # 处理数据
        success_count = 0
        error_count = 0
        error_messages = []
        
        # 按店铺名称和类型分组
        for (store_name, type_name), group in df.groupby(['店铺名称', '类型']):
            try:
                # 创建装箱单
                packing_list = PackingList(
                    store_name=store_name,
                    type=type_name,
                    status='pending',
                    created_by=current_user.id
                )
                db.add(packing_list)
                db.flush()  # 获取ID
                
                # 处理商品明细
                for _, row in group.iterrows():
                    product = db.query(Product).filter(
                        Product.sku == row['商品SKU']
                    ).first()
                    
                    if not product:
                        raise ValueError(f"找不到SKU为 {row['商品SKU']} 的商品")
                    
                    # 创建装箱单明细
                    item = PackingListItem(
                        packing_list_id=packing_list.id,
                        product_id=product.id,
                        quantity=row['数量']
                    )
                    db.add(item)
                    
                    # 创建装箱明细
                    box = BoxQuantity(
                        packing_list_item_id=item.id,
                        box_no=str(row['箱号']),
                        quantity=row['装箱数量']
                    )
                    db.add(box)
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_messages.append(f"处理 {store_name} 的数据时出错: {str(e)}")
                continue
        
        db.commit()
        
        return ImportResult(
            success=True,
            total=success_count + error_count,
            success_count=success_count,
            error_count=error_count,
            error_messages=error_messages
        )
        
    except Exception as e:
        return ImportResult(
            success=False,
            error=f"导入失败: {str(e)}"
        )

@router.post("/export")
async def export_packing_lists(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("packing-lists:read"))
):
    """
    导出装箱单到Excel
    """
    try:
        # 查询装箱单
        query = db.query(PackingList)
        
        if request.ids:
            query = query.filter(PackingList.id.in_(request.ids))
        if request.start_date:
            query = query.filter(PackingList.created_at >= request.start_date)
        if request.end_date:
            query = query.filter(PackingList.created_at <= request.end_date)
            
        packing_lists = query.all()
        
        # 准备数据
        data = []
        for pl in packing_lists:
            for item in pl.items:
                for box in item.box_quantities:
                    row = {
                        '装箱单号': pl.code,
                        '店铺名称': pl.store_name,
                        '类型': pl.type,
                        '状态': pl.status,
                        '商品SKU': item.product.sku,
                        '商品名称': item.product.name,
                        '商品中文名': item.product.chinese_name,
                        '商品类型': item.product.type,
                        '总数量': item.quantity,
                        '箱号': box.box_no,
                        '装箱数量': box.quantity,
                        '规格说明': box.specs or '',
                        '创建时间': pl.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # 添加箱子规格
                    if request.include_box_specs and pl.box_specs:
                        for spec in pl.box_specs:
                            if spec.box_no == box.box_no:
                                row.update({
                                    '长(cm)': spec.length,
                                    '宽(cm)': spec.width,
                                    '高(cm)': spec.height,
                                    '重量(kg)': spec.weight,
                                    '体积(m³)': spec.volume
                                })
                                break
                    
                    data.append(row)
        
        # 创建Excel
        df = pd.DataFrame(data)
        
        # 导出为Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='装箱单')
        
        # 设置响应头
        filename = f"装箱单_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        
        # 返回文件流
        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers=headers
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}") 