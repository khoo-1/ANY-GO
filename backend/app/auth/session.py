from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import APIKeyCookie
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Session cookie
cookie_scheme = APIKeyCookie(name="session")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    return pwd_context.hash(password)

def get_user(db: Session, username: str) -> Optional[User]:
    """通过用户名获取用户"""
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户"""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    session: str = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )
    
    if not session:
        raise credentials_exception
        
    try:
        # 从session中获取用户名
        username = session
        user = get_user(db, username)
        if user is None:
            raise credentials_exception
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )
        return user
    except Exception:
        raise credentials_exception

def check_permission(required_permission: str):
    """检查权限装饰器"""
    async def permission_dependency(current_user: User = Depends(get_current_user)):
        # 管理员拥有所有权限
        if current_user.role == "admin":
            return current_user
            
        # 将权限字符串分割成列表
        user_permissions = current_user.permissions.split(",") if current_user.permissions else []
            
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有操作权限"
            )
        return current_user
    return permission_dependency 