from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """令牌模型"""
    token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None 