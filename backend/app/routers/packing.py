from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..core.security import get_current_active_user
from ..crud.packing import (
    get_packing_list,
    get_packing_lists,
    create_packing_list,
    update_packing_list,
    delete_packing_list,
    add_item_to_packing_list,
    update_packing_list_item,
    remove_item_from_packing_list,
    update_box_specs
)
from ..schemas.packing import (
    PackingListCreate,
    PackingListUpdate,
    PackingListResponse,
    PackingItemCreate,
    PackingItemUpdate,
    PackingItemResponse,
    BoxSpecsCreate,
    BoxSpecsUpdate,
    BoxSpecsResponse
)

router = APIRouter(
    prefix="/packing",
    tags=["打包"],
    responses={404: {"description": "未找到"}},
)

@router.get("/lists", response_model=List[PackingListResponse])
def read_packing_lists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取打包清单列表"""
    packing_lists = get_packing_lists(db, skip=skip, limit=limit)
    return packing_lists

@router.post("/lists", response_model=PackingListResponse)
def create_new_packing_list(
    packing_list: PackingListCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """创建新打包清单"""
    return create_packing_list(db=db, packing_list=packing_list, user_id=current_user.id)

@router.get("/lists/{list_id}", response_model=PackingListResponse)
def read_packing_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取打包清单详情"""
    db_list = get_packing_list(db, list_id=list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="打包清单不存在")
    return db_list

@router.put("/lists/{list_id}", response_model=PackingListResponse)
def update_packing_list_info(
    list_id: int,
    packing_list: PackingListUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新打包清单信息"""
    db_list = get_packing_list(db, list_id=list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="打包清单不存在")
    return update_packing_list(db=db, list_id=list_id, packing_list=packing_list)

@router.delete("/lists/{list_id}")
def delete_packing_list_by_id(
    list_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """删除打包清单"""
    db_list = get_packing_list(db, list_id=list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="打包清单不存在")
    delete_packing_list(db=db, list_id=list_id)
    return {"message": "打包清单已删除"}

@router.post("/lists/{list_id}/items", response_model=PackingItemResponse)
def add_item(
    list_id: int,
    item: PackingItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """添加打包项目"""
    return add_item_to_packing_list(db=db, list_id=list_id, item=item)

@router.put("/lists/{list_id}/items/{item_id}", response_model=PackingItemResponse)
def update_item(
    list_id: int,
    item_id: int,
    item: PackingItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新打包项目"""
    return update_packing_list_item(db=db, list_id=list_id, item_id=item_id, item=item)

@router.delete("/lists/{list_id}/items/{item_id}")
def remove_item(
    list_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """删除打包项目"""
    remove_item_from_packing_list(db=db, list_id=list_id, item_id=item_id)
    return {"message": "打包项目已删除"}

@router.put("/lists/{list_id}/box", response_model=BoxSpecsResponse)
def update_box_specifications(
    list_id: int,
    box_specs: BoxSpecsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新箱子规格"""
    return update_box_specs(db=db, list_id=list_id, box_specs=box_specs)
