from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PackingList, PackingItem, Product, User
from app.schemas.packing_list import (
    PackingListCreate,
    PackingListResponse,
    PackingListUpdate
)

router = APIRouter(
    prefix="/api/packing",
    tags=["packing"]
)

# 模型定义
class PackingListItemBase(BaseModel):
    product_id: int
    quantity: int
    notes: Optional[str] = None

class PackingListItemCreate(PackingListItemBase):
    pass

class PackingListItemUpdate(PackingListItemBase):
    is_packed: Optional[bool] = None

class PackingListItemResponse(PackingListItemBase):
    id: int
    packing_list_id: int
    is_packed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PackingListBase(BaseModel):
    name: str
    description: Optional[str] = None

class PackingListCreate(PackingListBase):
    items: List[PackingListItemCreate]

class PackingListUpdate(PackingListBase):
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    items: Optional[List[PackingListItemCreate]] = None

class PackingListResponse(PackingListBase):
    id: int
    status: str
    created_by: int
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    items: List[PackingListItemResponse]

    class Config:
        orm_mode = True

# 路由定义
@router.get("/", response_model=List[PackingListResponse])
async def get_packing_lists(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取装箱单列表"""
    # 检查权限
    if "packing_lists:read" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问装箱单"
        )
    
    # 构建查询
    query = db.query(PackingList)
    
    # 根据状态筛选
    if status:
        query = query.filter(PackingList.status == status)
    
    # 分页
    packing_lists = query.offset(skip).limit(limit).all()
    
    return packing_lists

@router.get("/{packing_list_id}", response_model=PackingListResponse)
async def get_packing_list(
    packing_list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个装箱单详情"""
    # 检查权限
    if "packing_lists:read" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问装箱单"
        )
    
    # 查询装箱单
    packing_list = db.query(PackingList).filter(PackingList.id == packing_list_id).first()
    
    if packing_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="装箱单不存在"
        )
    
    return packing_list

@router.post("/", response_model=PackingListResponse, status_code=status.HTTP_201_CREATED)
async def create_packing_list(
    packing_list: PackingListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建装箱单"""
    # 检查权限
    if "packing_lists:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限创建装箱单"
        )
    
    # 创建装箱单
    db_packing_list = PackingList(
        name=packing_list.name,
        description=packing_list.description,
        status="draft",
        created_by=current_user.id
    )
    
    db.add(db_packing_list)
    db.commit()
    db.refresh(db_packing_list)
    
    # 创建装箱单明细
    for item in packing_list.items:
        # 检查产品是否存在
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"产品ID {item.product_id} 不存在"
            )
        
        db_item = PackingItem(
            packing_list_id=db_packing_list.id,
            product_id=item.product_id,
            quantity=item.quantity,
            notes=item.notes
        )
        
        db.add(db_item)
    
    db.commit()
    db.refresh(db_packing_list)
    
    return db_packing_list

@router.put("/{packing_list_id}", response_model=PackingListResponse)
async def update_packing_list(
    packing_list_id: int,
    packing_list_update: PackingListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新装箱单"""
    # 检查权限
    if "packing_lists:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新装箱单"
        )
    
    # 查询装箱单
    db_packing_list = db.query(PackingList).filter(PackingList.id == packing_list_id).first()
    
    if db_packing_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="装箱单不存在"
        )
    
    # 更新基本信息
    if packing_list_update.name is not None:
        db_packing_list.name = packing_list_update.name
    
    if packing_list_update.description is not None:
        db_packing_list.description = packing_list_update.description
    
    if packing_list_update.status is not None:
        db_packing_list.status = packing_list_update.status
    
    if packing_list_update.assigned_to is not None:
        # 检查指定的用户是否存在
        assignee = db.query(User).filter(User.id == packing_list_update.assigned_to).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户ID {packing_list_update.assigned_to} 不存在"
            )
        db_packing_list.assigned_to = packing_list_update.assigned_to
    
    # 如果提供了新的明细项，则更新
    if packing_list_update.items is not None:
        # 删除现有明细
        db.query(PackingItem).filter(PackingItem.packing_list_id == packing_list_id).delete()
        
        # 添加新明细
        for item in packing_list_update.items:
            # 检查产品是否存在
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"产品ID {item.product_id} 不存在"
                )
            
            db_item = PackingItem(
                packing_list_id=db_packing_list.id,
                product_id=item.product_id,
                quantity=item.quantity,
                notes=item.notes
            )
            
            db.add(db_item)
    
    db.commit()
    db.refresh(db_packing_list)
    
    return db_packing_list

@router.delete("/{packing_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_packing_list(
    packing_list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除装箱单"""
    # 检查权限
    if "packing_lists:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除装箱单"
        )
    
    # 查询装箱单
    db_packing_list = db.query(PackingList).filter(PackingList.id == packing_list_id).first()
    
    if db_packing_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="装箱单不存在"
        )
    
    # 删除装箱单（关联的明细会通过cascade自动删除）
    db.delete(db_packing_list)
    db.commit()
    
    return None

@router.post("/{packing_list_id}/approve", response_model=PackingListResponse)
async def approve_packing_list(
    packing_list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """审批装箱单"""
    # 检查权限
    if "packing_lists:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限审批装箱单"
        )
    
    # 查询装箱单
    db_packing_list = db.query(PackingList).filter(PackingList.id == packing_list_id).first()
    
    if db_packing_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="装箱单不存在"
        )
    
    # 更新状态
    db_packing_list.status = "approved"
    db.commit()
    db.refresh(db_packing_list)
    
    return db_packing_list

@router.post("/{packing_list_id}/items", response_model=PackingListItemResponse)
async def add_packing_list_item(
    packing_list_id: int,
    item: PackingListItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加装箱单明细"""
    # 检查权限
    if "packing_lists:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改装箱单"
        )
    
    # 查询装箱单
    db_packing_list = db.query(PackingList).filter(PackingList.id == packing_list_id).first()
    
    if db_packing_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="装箱单不存在"
        )
    
    # 检查产品是否存在
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"产品ID {item.product_id} 不存在"
        )
    
    # 创建明细
    db_item = PackingItem(
        packing_list_id=packing_list_id,
        product_id=item.product_id,
        quantity=item.quantity,
        notes=item.notes
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

@router.put("/{packing_list_id}/items/{item_id}", response_model=PackingListItemResponse)
async def update_packing_list_item(
    packing_list_id: int,
    item_id: int,
    item_update: PackingListItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新装箱单明细"""
    # 检查权限
    if "packing_lists:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改装箱单"
        )
    
    # 查询明细
    db_item = db.query(PackingItem).filter(
        PackingItem.id == item_id,
        PackingItem.packing_list_id == packing_list_id
    ).first()
    
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="装箱单明细不存在"
        )
    
    # 检查产品是否存在
    if item_update.product_id is not None:
        product = db.query(Product).filter(Product.id == item_update.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"产品ID {item_update.product_id} 不存在"
            )
        db_item.product_id = item_update.product_id
    
    # 更新其他字段
    if item_update.quantity is not None:
        db_item.quantity = item_update.quantity
    
    if item_update.notes is not None:
        db_item.notes = item_update.notes
    
    if item_update.is_packed is not None:
        db_item.is_packed = item_update.is_packed
    
    db.commit()
    db.refresh(db_item)
    
    return db_item

@router.delete("/{packing_list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_packing_list_item(
    packing_list_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除装箱单明细"""
    # 检查权限
    if "packing_lists:write" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改装箱单"
        )
    
    # 查询明细
    db_item = db.query(PackingItem).filter(
        PackingItem.id == item_id,
        PackingItem.packing_list_id == packing_list_id
    ).first()
    
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="装箱单明细不存在"
        )
    
    # 删除明细
    db.delete(db_item)
    db.commit()
    
    return None
