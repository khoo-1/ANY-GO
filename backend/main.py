from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.routers.packing import router as packing_router
from app.routers.dashboard import router as dashboard_router
from app.database import Base, engine

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="ANY-GO API",
    description="ANY-GO 后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:5174", "http://localhost:5175"],  # 允许多个前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加API前缀路由
api_app = FastAPI(title="ANY-GO API")
api_app.include_router(auth_router)
api_app.include_router(products_router)
api_app.include_router(packing_router)
api_app.include_router(dashboard_router)

# 将API应用挂载到主应用的/api路径下
app.mount("/api", api_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 