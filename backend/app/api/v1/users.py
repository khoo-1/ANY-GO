from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ...core.deps import get_db, get_current_active_user
from ...core.security import create_access_token
from ...crud import user as crud_user
from ...schemas.user import User, UserCreate, UserUpdate
from ...config import settings

router = APIRouter()

@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> User:
    """创建新用户"""
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud_user.create_user(db, user=user_in)
    return user

@router.get("/users/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> List[User]:
    """获取用户列表"""
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=User)
def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> User:
    """获取特定用户"""
    user = crud_user.get_user(db, user_id=user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user

@router.put("/users/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """更新用户"""
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user != current_user and not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    user = crud_user.update_user(db, user_id=user_id, user=user_in)
    return user

@router.delete("/users/{user_id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """删除用户"""
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    user = crud_user.delete_user(db, user_id=user_id)
    return user 