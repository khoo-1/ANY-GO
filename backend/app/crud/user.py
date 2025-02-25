from sqlalchemy.orm import Session
from app.models.user import User
from app.auth.router import verify_password

def authenticate_user(db: Session, username: str, password: str):
    """验证用户凭据"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_user(db: Session, username: str, password: str, is_superuser: bool = False):
    """创建新用户"""
    user = User(
        username=username,
        password=password,
        is_superuser=is_superuser
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user