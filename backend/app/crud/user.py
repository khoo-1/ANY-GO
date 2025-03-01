from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash

def get_user(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """获取用户列表"""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> Optional[User]:
    """创建新用户"""
    try:
        # 检查用户名是否已存在
        if get_user_by_username(db, user.username):
            return None
            
        # 创建用户实例
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password),
            full_name=user.full_name,
            is_active=True,
            is_superuser=user.is_superuser if hasattr(user, 'is_superuser') else False,
            permissions=user.permissions if hasattr(user, 'permissions') else None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 添加到数据库
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except IntegrityError:
        db.rollback()
        return None
    except Exception as e:
        db.rollback()
        print(f"创建用户时出错: {e}")
        return None

def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            return None
            
        # 更新用户属性
        for field, value in user.dict(exclude_unset=True).items():
            if field == "password":
                setattr(db_user, "hashed_password", get_password_hash(value))
            else:
                setattr(db_user, field, value)
                
        db_user.updated_at = datetime.now()
        
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except Exception as e:
        db.rollback()
        print(f"更新用户时出错: {e}")
        return None

def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            return False
            
        db.delete(db_user)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"删除用户时出错: {e}")
        return False