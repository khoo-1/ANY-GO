from sqlalchemy import Column, String, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class LogModule(str, enum.Enum):
    """日志模块"""
    PRODUCTS = "products"
    PACKING_LISTS = "packing_lists"
    USERS = "users"
    SYSTEM = "system"

class LogAction(str, enum.Enum):
    """日志操作类型"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    IMPORT = "import"
    EXPORT = "export"
    BACKUP = "backup"

class LogStatus(str, enum.Enum):
    """日志状态"""
    SUCCESS = "success"
    FAILURE = "failure"

class OperationLog(BaseModel):
    """操作日志模型"""
    __tablename__ = "operation_logs"

    user_id = Column(ForeignKey("users.id"), nullable=True)
    username = Column(String, nullable=False)
    module = Column(Enum(LogModule), nullable=False)
    action = Column(Enum(LogAction), nullable=False)
    description = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    status = Column(Enum(LogStatus), default=LogStatus.SUCCESS)

    # 关联
    user = relationship("User") 