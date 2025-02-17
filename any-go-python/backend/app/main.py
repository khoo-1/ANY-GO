from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.v1 import auth, users
from .database import init_db

app = FastAPI(
    title="ANY-GO API",
    description="跨境电商团队协作平台 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["认证"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["用户"])

@app.on_event("startup")
async def startup_event():
    """应用启动时运行"""
    init_db()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 