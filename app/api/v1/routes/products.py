from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models import LeagueEnum, User
from app.schemas import ProductCreate, ProductListResponse, ProductResponse, ProductUpdate
from app.services.services import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Create a new product."""
    return await ProductService(session).create(data)


@router.get("/", response_model=list[ProductListResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    league: LeagueEnum | None = None,
    team: str | None = None,
    category_id: int | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List products with optional filters."""
    return await ProductService(session).list_all(
        skip=skip,
        limit=limit,
        league=league,
        team=team,
        category_id=category_id,
        is_active=is_active,
        search=search,
    )


@router.get("/low-stock", response_model=list[ProductListResponse])
async def get_low_stock(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get all products below minimum stock threshold."""
    return await ProductService(session).get_low_stock()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await ProductService(session).get(product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await ProductService(session).update(product_id, data)


@router.delete("/{product_id}", status_code=204)
async def deactivate_product(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Soft delete — deactivates the product."""
    await ProductService(session).delete(product_id)
