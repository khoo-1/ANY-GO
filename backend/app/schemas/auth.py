# 认证相关的数据模型验证

from typing import List, Optional
from pydantic import BaseModel

class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[str] = None

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str

class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """用户创建模型"""
    password: str

class UserResponse(UserBase):
    """用户响应模型"""
    id: str
    is_active: bool
    role: str
    status: str
    permissions: List[str]

    class Config:
        from_attributes = True