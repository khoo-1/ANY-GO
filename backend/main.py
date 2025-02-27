from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from app.database import engine, Base, DATABASE_URL
from app.routers import auth_router, products_router, packing_router
# 暂时注释掉packing_lists导入，直到依赖问题解决
# from app.routers import packing_lists
from init_users import init_users
from app.routers.dashboard import router as dashboard_router

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
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时运行
    init_users()
    yield
    # 关闭时运行
    pass

app = FastAPI(
    title="ANY-GO API",
    description="跨境电商平台API",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"CORS配置: 允许的源 = {['http://localhost:5174']}")

# 注册路由 - 移除prefix，因为已经在router中定义
app.include_router(auth_router)
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(packing_router)
# 暂时注释掉packing_lists路由注册
# app.include_router(packing_lists.router, prefix="/api/packing-lists", tags=["packing-lists"])

# 添加调试信息
@app.middleware("http")
async def debug_middleware(request, call_next):
    print(f"收到请求: {request.method} {request.url}")
    print(f"请求头: {request.headers}")
    
    response = await call_next(request)
    
    print(f"响应状态: {response.status_code}")
    print(f"响应头: {response.headers}")
    
    return response

@app.get("/")
async def root():
    return {"message": "Welcome to ANY-GO API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    debug = os.getenv("DEBUG", "false").lower() == "true"
    # 打印启动信息
    print(f"启动服务器: host=0.0.0.0, port=8000, debug={debug}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=debug) 