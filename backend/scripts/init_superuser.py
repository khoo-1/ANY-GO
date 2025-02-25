from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash
from app.db.session import SessionLocal

def init_superuser():
    db = SessionLocal()
    try:
        # 检查是否已存在超级管理员
        superuser = db.query(User).filter(User.is_superuser == True).first()
        if not superuser:
            # 创建超级管理员账号
            superuser = User(
                username="admin",
                password=get_password_hash("admin123"),  # 默认密码
                is_superuser=True
            )
            db.add(superuser)
            db.commit()
            print("超级管理员账号创建成功！")
        else:
            print("超级管理员账号已存在！")
    except Exception as e:
        print(f"创建超级管理员账号失败：{str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    init_superuser()