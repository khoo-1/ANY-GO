import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import engine, get_db, Base, DATABASE_URL
from app.models import User
import json

# 加载环境变量
load_dotenv()

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def init_users():
    # 确保表已创建
    Base.metadata.create_all(bind=engine)
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 检查管理员用户是否已存在
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            # 创建管理员用户
            admin_permissions = [
                "users:read", "users:write", 
                "products:read", "products:write", 
                "packing_lists:read", "packing_lists:write", 
                "profit:read", "stock:read"
            ]
            
            admin = User(
                username="admin",
                email="admin@example.com",
                full_name="管理员",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                permissions=admin_permissions,
                disabled=False
            )
            
            db.add(admin)
            print("已创建管理员用户")
            
            # 创建普通用户
            user_permissions = [
                "products:read", 
                "packing_lists:read", 
                "profit:read", 
                "stock:read"
            ]
            
            user = User(
                username="user",
                email="user@example.com",
                full_name="普通用户",
                hashed_password=get_password_hash("user123"),
                role="user",
                permissions=user_permissions,
                disabled=False
            )
            
            db.add(user)
            print("已创建普通用户")
            
            # 提交事务
            db.commit()
            print("用户初始化完成")
        else:
            print("管理员用户已存在，跳过初始化")
            
    except Exception as e:
        db.rollback()
        print(f"初始化用户时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print(f"开始初始化用户... 使用连接: {DATABASE_URL}")
    init_users() 