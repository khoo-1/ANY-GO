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
        # 检查管理员用户是否已存在
        if not get_user_by_username(db, "admin"):
            # 创建管理员用户
            admin_user = UserCreate(
                username="admin",
                email="admin@example.com",
                password="admin123",
                full_name="Administrator",
                is_superuser=True,
                permissions=["admin"]
            )
            create_user(db, admin_user)
            print("管理员用户创建成功")
        else:
            print("管理员用户已存在")

        # 检查测试用户是否已存在
        if not get_user_by_username(db, "test"):
            # 创建测试用户
            test_user = UserCreate(
                username="test",
                email="test@example.com",
                password="test123",
                full_name="Test User",
                is_superuser=False,
                permissions=["user"]
            )
            create_user(db, test_user)
            print("测试用户创建成功")
        else:
            print("测试用户已存在")

    except Exception as e:
        print(f"初始化用户时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print(f"开始初始化用户... 使用连接: {DATABASE_URL}")
    init_users() 