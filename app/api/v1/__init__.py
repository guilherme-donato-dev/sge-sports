from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.products import router as products_router
from app.api.v1.routes.other_routes import (
    categories_router,
    clients_router,
    orders_router,
    stock_router,
    ai_router,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(categories_router)
api_router.include_router(clients_router)
api_router.include_router(orders_router)
api_router.include_router(stock_router)
api_router.include_router(ai_router)
