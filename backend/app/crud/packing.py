from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List

from ..models.packing import PackingList, PackingItem, BoxSpecs
from ..schemas.packing import (
    PackingListCreate,
    PackingListUpdate,
    PackingItemCreate,
    PackingItemUpdate,
    BoxSpecsCreate,
    BoxSpecsUpdate
)

def get_packing_list(db: Session, list_id: int) -> Optional[PackingList]:
    """获取打包清单"""
    return db.query(PackingList).filter(PackingList.id == list_id).first()

def get_packing_lists(db: Session, skip: int = 0, limit: int = 100) -> List[PackingList]:
    """获取打包清单列表"""
    return db.query(PackingList).offset(skip).limit(limit).all()

def create_packing_list(db: Session, packing_list: PackingListCreate, user_id: int) -> Optional[PackingList]:
    """创建打包清单"""
    try:
        # 创建打包清单
        db_list = PackingList(
            name=packing_list.name,
            description=packing_list.description,
            status=packing_list.status,
            created_by=user_id,
            assigned_to=packing_list.assigned_to,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(db_list)
        db.commit()
        db.refresh(db_list)

        # 创建打包项目
        for item in packing_list.items:
            db_item = PackingItem(
                packing_list_id=db_list.id,
                product_id=item.product_id,
                quantity=item.quantity,
                notes=item.notes,
                is_packed=item.is_packed,
                box_quantities=item.box_quantities,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_list)
        return db_list

    except IntegrityError:
        db.rollback()
        return None
    except Exception as e:
        db.rollback()
        print(f"创建打包清单时出错: {e}")
        return None

def update_packing_list(db: Session, list_id: int, packing_list: PackingListUpdate) -> Optional[PackingList]:
    """更新打包清单"""
    try:
        db_list = get_packing_list(db, list_id)
        if not db_list:
            return None

        # 更新基本信息
        for field, value in packing_list.dict(exclude_unset=True).items():
            if field != "items":
                setattr(db_list, field, value)

        # 更新打包项目
        if packing_list.items is not None:
            # 删除现有项目
            db.query(PackingItem).filter(PackingItem.packing_list_id == list_id).delete()

            # 添加新项目
            for item in packing_list.items:
                db_item = PackingItem(
                    packing_list_id=list_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    notes=item.notes,
                    is_packed=item.is_packed,
                    box_quantities=item.box_quantities,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(db_item)

        db_list.updated_at = datetime.now()
        db.commit()
        db.refresh(db_list)
        return db_list

    except Exception as e:
        db.rollback()
        print(f"更新打包清单时出错: {e}")
        return None

def delete_packing_list(db: Session, list_id: int) -> bool:
    """删除打包清单"""
    try:
        db_list = get_packing_list(db, list_id)
        if not db_list:
            return False

        db.delete(db_list)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        print(f"删除打包清单时出错: {e}")
        return False

def add_item_to_packing_list(db: Session, list_id: int, item: PackingItemCreate) -> Optional[PackingItem]:
    """添加打包项目"""
    try:
        db_item = PackingItem(
            packing_list_id=list_id,
            product_id=item.product_id,
            quantity=item.quantity,
            notes=item.notes,
            is_packed=item.is_packed,
            box_quantities=item.box_quantities,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    except Exception as e:
        db.rollback()
        print(f"添加打包项目时出错: {e}")
        return None

def update_packing_list_item(db: Session, list_id: int, item_id: int, item: PackingItemUpdate) -> Optional[PackingItem]:
    """更新打包项目"""
    try:
        db_item = db.query(PackingItem).filter(
            PackingItem.packing_list_id == list_id,
            PackingItem.id == item_id
        ).first()

        if not db_item:
            return None

        for field, value in item.dict(exclude_unset=True).items():
            setattr(db_item, field, value)

        db_item.updated_at = datetime.now()
        db.commit()
        db.refresh(db_item)
        return db_item

    except Exception as e:
        db.rollback()
        print(f"更新打包项目时出错: {e}")
        return None

def remove_item_from_packing_list(db: Session, list_id: int, item_id: int) -> bool:
    """删除打包项目"""
    try:
        db_item = db.query(PackingItem).filter(
            PackingItem.packing_list_id == list_id,
            PackingItem.id == item_id
        ).first()

        if not db_item:
            return False

        db.delete(db_item)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        print(f"删除打包项目时出错: {e}")
        return False

def update_box_specs(db: Session, list_id: int, box_specs: BoxSpecsUpdate) -> Optional[BoxSpecs]:
    """更新箱子规格"""
    try:
        db_specs = db.query(BoxSpecs).filter(BoxSpecs.packing_list_id == list_id).first()

        if db_specs:
            # 更新现有规格
            for field, value in box_specs.dict().items():
                setattr(db_specs, field, value)
            db_specs.updated_at = datetime.now()
        else:
            # 创建新规格
            db_specs = BoxSpecs(
                packing_list_id=list_id,
                **box_specs.dict(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(db_specs)

        db.commit()
        db.refresh(db_specs)
        return db_specs

    except Exception as e:
        db.rollback()
        print(f"更新箱子规格时出错: {e}")
        return None 