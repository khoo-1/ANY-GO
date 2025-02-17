from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from .base import BaseSchema

class UserBase(BaseSchema):
    """用户基础模式"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    role: str = Field(default="operator", pattern="^(admin|manager|operator)$")
    status: str = Field(default="active", pattern="^(active|inactive)$")
    permissions: List[str] = []

class UserCreate(UserBase):
    """创建用户"""
    password: str

class UserUpdate(UserBase):
    """更新用户"""
    password: Optional[str] = None

class UserInDBBase(UserBase):
    """数据库中的用户"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    """返回给API的用户"""
    pass

class UserInDB(UserInDBBase):
    """数据库中完整的用户"""
    hashed_password: str

class UserResponse(UserBase):
    """用户响应"""
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    """令牌"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str

class LoginResponse(BaseModel):
    """登录响应"""
    token: Token
    user: UserResponse

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=50)

class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    user_id: int
    new_password: str = Field(..., min_length=6, max_length=50) 