from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')

class BaseSchema(BaseModel):
    """基础模式"""
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BaseResponse(BaseModel, Generic[T]):
    """基础响应"""
    code: int = 0
    data: Optional[T] = None
    message: str = "success"

class PageParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 10

class PageResponse(BaseResponse[List[T]], Generic[T]):
    """分页响应"""
    total: int
    page: int
    page_size: int

class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    details: Optional[dict] = None 