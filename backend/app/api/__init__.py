from .stock_timeline import router as stock_timeline_router

api_router.include_router(
    stock_timeline_router,
    prefix="/stock",
    tags=["stock"]
) 