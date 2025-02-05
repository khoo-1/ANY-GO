from sqlalchemy import Column, String, Enum, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class BackupType(str, enum.Enum):
    """备份类型"""
    FULL = "full"
    PRODUCTS = "products"
    PACKING_LISTS = "packing_lists"

class BackupStatus(str, enum.Enum):
    """备份状态"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Backup(BaseModel):
    """备份模型"""
    __tablename__ = "backups"

    filename = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    type = Column(Enum(BackupType), default=BackupType.FULL)
    status = Column(Enum(BackupStatus), default=BackupStatus.PENDING)
    path = Column(String, nullable=False)
    description = Column(String, nullable=True)
    error = Column(String, nullable=True)
    created_by = Column(ForeignKey("users.id"), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # 关联
    user = relationship("User") 