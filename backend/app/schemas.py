from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    
    class Config:
        from_attributes = True  # 替换原来的orm_mode = True

class UserCreate(UserBase):
    password: str  # 注意：这里使用password是正确的，因为这是API输入

class UserInDB(UserBase):
    id: int
    hashed_password: str  # 存储在数据库中的是hashed_password
    disabled: int = 0
    created_at: str
    updated_at: str 