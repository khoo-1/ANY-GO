from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseSchema

class UserBase(BaseSchema):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50)
    role: str = Field(default="operator", pattern="^(admin|manager|operator)$")
    status: str = Field(default="active", pattern="^(active|inactive)$")
    permissions: List[str] = []

class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=6, max_length=50)

class UserUpdate(BaseSchema):
    """更新用户"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    role: Optional[str] = Field(None, pattern="^(admin|manager|operator)$")
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    permissions: Optional[List[str]] = None

class UserInDB(UserBase):
    """数据库中的用户"""
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

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