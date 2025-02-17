from sqlalchemy import Column, String, Enum, ARRAY, Boolean
from .base import BaseModel
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.OPERATOR, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    permissions = Column(ARRAY(String), nullable=False, default=list)
    last_login = Column(String, nullable=True)

    @property
    def default_permissions(self):
        """获取默认权限"""
        if self.role == UserRole.ADMIN:
            return [
                "products:read", "products:write", "products:delete",
                "packing_lists:read", "packing_lists:write", "packing_lists:delete",
                "users:read", "users:write", "users:delete",
                "system:backup"
            ]
        elif self.role == UserRole.MANAGER:
            return [
                "products:read", "products:write",
                "packing_lists:read", "packing_lists:write",
                "users:read"
            ]
        else:  # OPERATOR
            return [
                "products:read",
                "packing_lists:read"
            ] 