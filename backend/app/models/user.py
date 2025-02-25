from sqlalchemy import Column, String, Boolean
from .base import BaseModel

class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)