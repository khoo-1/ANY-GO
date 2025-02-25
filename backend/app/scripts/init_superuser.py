from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.auth import get_password_hash

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
            password=get_password_hash("admin123"),
            is_superuser=True
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