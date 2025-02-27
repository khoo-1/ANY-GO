import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import engine, get_db, Base, DATABASE_URL, SessionLocal
from app.models import User
from app.crud.user import create_user, get_user_by_username
from app.schemas.user import UserCreate
import json

# 加载环境变量
load_dotenv()

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def init_users():
    """初始化用户数据"""
    db = SessionLocal()
    try:
        # 检查管理员用户是否存在
        admin = get_user_by_username(db, "admin")
        if not admin:
            # 创建管理员用户
            admin_user = UserCreate(
                username="admin",
                email="admin@example.com",
                full_name="管理员",
                password="admin123",
                role="admin",
                permissions=["all"]
            )
            create_user(db, admin_user)
            print("管理员用户创建成功")
        else:
            print("管理员用户已存在，跳过初始化")
    finally:
        db.close()

if __name__ == "__main__":
    print(f"开始初始化用户... 使用连接: {DATABASE_URL}")
    init_users() 