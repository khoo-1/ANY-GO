from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List

from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate

def get_product(db: Session, product_id: int) -> Optional[Product]:
    """根据ID获取产品"""
    return db.query(Product).filter(Product.id == product_id).first()

def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    """根据SKU获取产品"""
    return db.query(Product).filter(Product.sku == sku).first()

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """获取产品列表"""
    return db.query(Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate, user_id: int) -> Optional[Product]:
    """创建新产品"""
    try:
        # 检查SKU是否已存在
        if get_product_by_sku(db, product.sku):
            return None
            
        # 创建产品实例
        db_product = Product(
            name=product.name,
            description=product.description,
            sku=product.sku,
            unit=product.unit,
            weight=product.weight,
            length=product.length,
            width=product.width,
            height=product.height,
            created_by=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 添加到数据库
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
        
    except IntegrityError:
        db.rollback()
        return None
    except Exception as e:
        db.rollback()
        print(f"创建产品时出错: {e}")
        return None

def update_product(db: Session, product_id: int, product: ProductUpdate, user_id: int) -> Optional[Product]:
    """更新产品信息"""
    try:
        db_product = get_product(db, product_id)
        if not db_product:
            return None
            
        # 更新产品属性
        for field, value in product.dict(exclude_unset=True).items():
            setattr(db_product, field, value)
                
        db_product.updated_at = datetime.now()
        
        db.commit()
        db.refresh(db_product)
        return db_product
        
    except Exception as e:
        db.rollback()
        print(f"更新产品时出错: {e}")
        return None

def delete_product(db: Session, product_id: int) -> bool:
    """删除产品"""
    try:
        db_product = get_product(db, product_id)
        if not db_product:
            return False
            
        db.delete(db_product)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"删除产品时出错: {e}")
        return False 