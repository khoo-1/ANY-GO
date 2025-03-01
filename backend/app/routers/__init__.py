# routers 包初始化文件
"""
路由模块包
""" 

# 导入所有路由模块
from .auth import router as auth_router
from .products import router as products_router
from .packing import router as packing_router

# 暂时注释掉packing_lists导入，直到依赖问题解决
# from app.routers.packing_lists import router as packing_lists_router

# 导出所有路由模块
auth = auth_router
products = products_router
packing = packing_router
# 暂时注释掉packing_lists导出
# packing_lists = packing_lists_router 

# 导出路由器
__all__ = ["auth_router", "products_router", "packing_router"] 