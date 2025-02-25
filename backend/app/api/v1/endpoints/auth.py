from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ....core.deps import authenticate_user, get_db
from ....core.security import create_access_token, get_password_hash
from ....schemas.user import UserCreate, UserResponse
from ....crud.user import create_user, get_user_by_email, get_user_by_username
from ....models.user import User
from ....config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """用户注册"""
    # 检查邮箱是否已被注册
    if get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 检查用户名是否已被使用
    if get_user_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用"
        )
    
    # 创建新用户
    user = create_user(db, obj_in=user_in)
    return user

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """用户登录"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow().isoformat()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }