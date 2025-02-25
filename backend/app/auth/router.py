from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..database import get_db
from ..models.user import User
from ..schemas.auth import UserCreate, UserResponse, LoginRequest

router = APIRouter(tags=["认证"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/login", response_model=dict)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被禁用"
        )

    return {"message": "登录成功", "user_id": user.id}

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    user = User(
        username=user_data.username,
        password=get_password_hash(user_data.password),
        is_active=True,
        role="user",
        status="active",
        permissions=["basic_access"]
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user