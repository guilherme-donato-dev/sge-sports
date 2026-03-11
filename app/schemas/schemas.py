from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import LeagueEnum, OrderStatusEnum, SizeEnum, StockMovementTypeEnum


# ──────────────────────────────────────────────
# Base helpers
# ──────────────────────────────────────────────

class OrmBase(BaseModel):
    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Auth / User
# ──────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(OrmBase):
    id: int
    name: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None


# ──────────────────────────────────────────────
# Category
# ──────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None


class CategoryResponse(OrmBase):
    id: int
    name: str
    description: str | None
    created_at: datetime


# ──────────────────────────────────────────────
# Product
# ──────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    sku: str = Field(..., min_length=3, max_length=50)
    description: str | None = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    cost_price: Decimal = Field(..., gt=0, decimal_places=2)
    league: LeagueEnum
    team: str = Field(..., min_length=2, max_length=100)
    size: SizeEnum
    quantity_in_stock: int = Field(0, ge=0)
    min_stock_alert: int = Field(10, ge=0)
    category_id: int


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(None, gt=0, decimal_places=2)
    cost_price: Decimal | None = Field(None, gt=0, decimal_places=2)
    league: LeagueEnum | None = None
    team: str | None = Field(None, min_length=2, max_length=100)
    size: SizeEnum | None = None
    min_stock_alert: int | None = Field(None, ge=0)
    is_active: bool | None = None
    category_id: int | None = None


class ProductResponse(OrmBase):
    id: int
    name: str
    sku: str
    description: str | None
    price: Decimal
    cost_price: Decimal
    league: LeagueEnum
    team: str
    size: SizeEnum
    quantity_in_stock: int
    min_stock_alert: int
    is_active: bool
    category_id: int
    created_at: datetime


class ProductListResponse(OrmBase):
    id: int
    name: str
    sku: str
    league: LeagueEnum
    team: str
    size: SizeEnum
    price: Decimal
    quantity_in_stock: int
    is_active: bool


# ──────────────────────────────────────────────
# Client
# ──────────────────────────────────────────────

class ClientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: str | None = Field(None, max_length=30)
    cpf: str | None = Field(None, max_length=14)
    address: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str | None = None
    cpf: str | None = None
    address: str | None = None
    is_active: bool | None = None


class ClientResponse(OrmBase):
    id: int
    name: str
    email: str
    phone: str | None
    cpf: str | None
    address: str | None
    is_active: bool
    created_at: datetime


# ──────────────────────────────────────────────
# Order
# ──────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    client_id: int
    items: list[OrderItemCreate] = Field(..., min_length=1)
    notes: str | None = None


class OrderItemResponse(OrmBase):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(OrmBase):
    id: int
    order_number: str
    status: OrderStatusEnum
    total_amount: Decimal
    notes: str | None
    client_id: int
    items: list[OrderItemResponse]
    created_at: datetime


class OrderUpdateStatus(BaseModel):
    status: OrderStatusEnum


# ──────────────────────────────────────────────
# Stock
# ──────────────────────────────────────────────

class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: StockMovementTypeEnum
    quantity: int = Field(..., gt=0)
    reason: str | None = Field(None, max_length=255)


class StockMovementResponse(OrmBase):
    id: int
    product_id: int
    movement_type: StockMovementTypeEnum
    quantity: int
    quantity_before: int
    quantity_after: int
    reason: str | None
    created_at: datetime


class StockAlertResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    league: LeagueEnum
    team: str
    current_stock: int
    min_stock_alert: int


# ──────────────────────────────────────────────
# AI
# ──────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    used_context: bool = False


class StockAlertAIResponse(BaseModel):
    alerts: list[StockAlertResponse]
    ai_analysis: str
    total_low_stock: int


# ──────────────────────────────────────────────
# Pagination
# ──────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list
