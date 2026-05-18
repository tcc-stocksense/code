from fastapi import FastAPI

from app.routers import health_router, predict_router

app = FastAPI(
    title="StockSense ML Service",
    version="1.0.0",
)

app.include_router(health_router.router)
app.include_router(predict_router.router)
