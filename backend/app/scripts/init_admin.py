from sqlalchemy.orm import Session
from app.models import User, UserRole, UserStatus
from app.core.security import get_password_hash
from app.database import SessionLocal

def init_superuser(db: Session) -> None:
    # 检查是否已存在超级管理员
    admin = db.query(User).filter(User.is_superuser == True).first()
    if admin:
        print("超级管理员已存在，跳过初始化")
        return

    # 创建超级管理员账号
    superuser = User(
        email="admin@any-go.com",
        username="admin",
        full_name="System Administrator",
        hashed_password=get_password_hash("admin123"),  # 请在首次登录后修改此密码
        is_active=True,
        is_superuser=True,
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        permissions=[
            "products:read", "products:write", "products:delete",
            "packing_lists:read", "packing_lists:write", "packing_lists:delete",
            "users:read", "users:write", "users:delete",
            "system:backup"
        ]
    )

    try:
        db.add(superuser)
        db.commit()
        print("超级管理员账号创建成功")
        print("用户名: admin")
        print("密码: admin123")
        print("请在首次登录后立即修改密码！")
    except Exception as e:
        db.rollback()
        print(f"创建超级管理员失败: {str(e)}")

def main():
    db = SessionLocal()
    try:
        init_superuser(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()