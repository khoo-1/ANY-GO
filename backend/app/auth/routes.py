from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.auth.router import router, verify_password

# 使用router.py中定义的路由