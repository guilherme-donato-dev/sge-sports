"""
Remaining routers: categories, clients, orders, stock, AI.
"""
# ── categories.py ──────────────────────────────────────────────
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.services import CategoryService

categories_router = APIRouter(prefix="/categories", tags=["Categories"])


@categories_router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await CategoryService(session).create(data)


@categories_router.get("/", response_model=list[CategoryResponse])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await CategoryService(session).list_all(skip, limit)


@categories_router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await CategoryService(session).get(category_id)


@categories_router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await CategoryService(session).update(category_id, data)


@categories_router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    await CategoryService(session).delete(category_id)


# ── clients.py ────────────────────────────────────────────────
from app.schemas import ClientCreate, ClientResponse, ClientUpdate
from app.services.services import ClientService

clients_router = APIRouter(prefix="/clients", tags=["Clients"])


@clients_router.post("/", response_model=ClientResponse, status_code=201)
async def create_client(
    data: ClientCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await ClientService(session).create(data)


@clients_router.get("/", response_model=list[ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await ClientService(session).list_all(skip, limit)


@clients_router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await ClientService(session).get(client_id)


@clients_router.get("/{client_id}/orders")
async def get_client_with_orders(
    client_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await ClientService(session).get_with_orders(client_id)


@clients_router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await ClientService(session).update(client_id, data)


# ── orders.py ─────────────────────────────────────────────────
from app.schemas import OrderCreate, OrderResponse, OrderUpdateStatus
from app.services.services import OrderService

orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Create a sale order. Automatically deducts stock."""
    return await OrderService(session).create(data)


@orders_router.get("/", response_model=list[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await OrderService(session).list_all(skip, limit)


@orders_router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await OrderService(session).get(order_id)


@orders_router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    data: OrderUpdateStatus,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await OrderService(session).update_status(order_id, data)


# ── stock.py ──────────────────────────────────────────────────
from app.schemas import StockMovementCreate, StockMovementResponse
from app.services.services import StockService

stock_router = APIRouter(prefix="/stock", tags=["Stock"])


@stock_router.post("/movements", response_model=StockMovementResponse, status_code=201)
async def add_stock_movement(
    data: StockMovementCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Register a manual stock movement (IN, OUT, or ADJUST)."""
    return await StockService(session).add_movement(data)


@stock_router.get("/movements/{product_id}", response_model=list[StockMovementResponse])
async def get_product_movements(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get stock movement history for a specific product."""
    return await StockService(session).get_product_movements(product_id, skip, limit)


# ── ai.py ─────────────────────────────────────────────────────
from app.ai.chatbot import get_chat_response, get_stock_alert_analysis
from app.schemas import ChatMessage, ChatResponse, StockAlertAIResponse, StockAlertResponse
from app.services.services import ProductService

ai_router = APIRouter(prefix="/ai", tags=["AI"])


@ai_router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    data: ChatMessage,
    _: User = Depends(get_current_user),
):
    """Chat with the AI stock assistant powered by LangChain."""
    reply = await get_chat_response(data.message)
    return ChatResponse(reply=reply, used_context=True)


@ai_router.get("/alerts/stock", response_model=StockAlertAIResponse)
async def get_ai_stock_alerts(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get AI-powered analysis of products with low stock."""
    low_products = await ProductService(session).get_low_stock()
    alerts = [
        StockAlertResponse(
            product_id=p.id,
            sku=p.sku,
            name=p.name,
            league=p.league,
            team=p.team,
            current_stock=p.quantity_in_stock,
            min_stock_alert=p.min_stock_alert,
        )
        for p in low_products
    ]
    analysis = await get_stock_alert_analysis(alerts)
    return StockAlertAIResponse(
        alerts=alerts,
        ai_analysis=analysis,
        total_low_stock=len(alerts),
    )
