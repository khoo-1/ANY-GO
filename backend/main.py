from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.database import engine, Base, DATABASE_URL
from app.routers import auth, products, packing
from init_users import init_users

# 加载环境变量
load_dotenv()

# 创建数据库表
try:
    Base.metadata.create_all(bind=engine)
    print(f"数据库表创建成功，使用连接: {DATABASE_URL}")
except Exception as e:
    print(f"创建数据库表时出错: {e}")
    # 如果使用PostgreSQL失败，尝试使用SQLite
    if not DATABASE_URL.startswith("sqlite"):
        print("尝试使用SQLite作为备用数据库...")
        from sqlalchemy import create_engine
        sqlite_engine = create_engine("sqlite:///./app.db", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=sqlite_engine)
        print("使用SQLite创建数据库表成功")

# 创建FastAPI应用
app = FastAPI(
    title="ANY-GO API",
    description="跨境电商平台API",
    version="0.1.0"
)

# 配置CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(packing.router)

@app.on_event("startup")
async def startup_event():
    # 初始化用户
    try:
        init_users()
    except Exception as e:
        print(f"初始化用户时出错: {e}")

@app.get("/")
async def root():
    return {"message": "欢迎使用ANY-GO API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    debug = os.getenv("DEBUG", "false").lower() == "true"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=debug) 