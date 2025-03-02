import os
import sys
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.product import Product
from app.models.packing import PackingList, PackingItem, BoxSpecs
from app.core.security import get_password_hash

# 数据库URL
DATABASE_URL = "sqlite:///./app.db"

# 尝试删除现有数据库文件
try:
    if os.path.exists("app.db"):
        print("正在删除现有数据库文件...")
        os.remove("app.db")
        time.sleep(1)  # 等待文件系统释放文件
        print("数据库文件已删除")
except Exception as e:
    print(f"删除数据库文件时出错: {e}")
    print("请确保没有其他程序正在使用数据库文件")
    sys.exit(1)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=True
)

# 创建所有表
print("正在创建数据库表...")
Base.metadata.create_all(bind=engine)
print("数据库表创建完成")

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# 创建初始用户
print("正在创建初始用户...")
admin_user = User(
    username="admin",
    email="admin@example.com",
    hashed_password=get_password_hash("admin123"),
    full_name="管理员",
    is_active=True,
    is_superuser=True,
    permissions=["admin", "read", "write", "delete"]
)

normal_user = User(
    username="user",
    email="user@example.com",
    hashed_password=get_password_hash("user123"),
    full_name="普通用户",
    is_active=True,
    is_superuser=False,
    permissions=["read"]
)

# 添加用户到数据库
db.add(admin_user)
db.add(normal_user)
db.commit()
print("初始用户创建完成")

# 关闭会话
db.close()

print("数据库初始化完成") 