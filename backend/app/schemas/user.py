from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr

class UserBase(BaseModel):
    """用户基础模式"""
    username: constr(min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    permissions: Optional[List[str]] = None

class UserCreate(UserBase):
    """创建用户模式"""
    password: constr(min_length=6, max_length=50)

class UserUpdate(BaseModel):
    """更新用户模式"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[constr(min_length=6, max_length=50)] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    permissions: Optional[List[str]] = None

class UserInDB(UserBase):
    """数据库中的用户模式"""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    """令牌模式"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """令牌数据模式"""
    username: Optional[str] = None

class LoginRequest(BaseModel):
    """登录请求"""
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6, max_length=50)

class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: constr(min_length=6, max_length=50)
    new_password: constr(min_length=6, max_length=50)

class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    user_id: int
    new_password: constr(min_length=6, max_length=50)