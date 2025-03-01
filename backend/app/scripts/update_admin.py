from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.auth.jwt import get_password_hash

def update_admin():
    """更新管理员账号"""
    db = SessionLocal()
    try:
        # 查找管理员账号
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("管理员账号不存在")
            return
        
        # 更新管理员账号
        admin.email = "admin@example.com"
        admin.full_name = "系统管理员"
        admin.role = "admin"
        admin.permissions = "packing:read,packing:write"
        admin.disabled = False
        
        db.commit()
        print("管理员账号更新成功")
        
    except Exception as e:
        print(f"更新管理员账号失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_admin() 