from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.auth.jwt import get_password_hash

def init_superuser():
    """初始化超级管理员账号"""
    db = SessionLocal()
    try:
        # 检查是否已存在超级管理员
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("超级管理员账号已存在")
            return
        
        # 创建超级管理员账号
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="系统管理员",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            permissions="packing:read,packing:write",  # 添加所需的权限
            disabled=False
        )
        
        db.add(admin_user)
        db.commit()
        print("超级管理员账号创建成功")
        print("用户名: admin")
        print("密码: admin123")
        
    except Exception as e:
        print(f"创建超级管理员账号失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_superuser()