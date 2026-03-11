from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Category,
    Client,
    LeagueEnum,
    Order,
    OrderStatusEnum,
    Product,
    StockMovement,
    User,
)
from app.repositories.base import BaseRepository


# ──────────────────────────────────────────────
# User Repository
# ──────────────────────────────────────────────

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()


# ──────────────────────────────────────────────
# Category Repository
# ──────────────────────────────────────────────

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()


# ──────────────────────────────────────────────
# Product Repository
# ──────────────────────────────────────────────

class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_by_sku(self, sku: str) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none()

    async def get_all_filtered(
        self,
        skip: int = 0,
        limit: int = 20,
        league: LeagueEnum | None = None,
        team: str | None = None,
        category_id: int | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> list[Product]:
        query = select(Product)
        filters = []
        if league:
            filters.append(Product.league == league)
        if team:
            filters.append(Product.team.ilike(f"%{team}%"))
        if category_id:
            filters.append(Product.category_id == category_id)
        if is_active is not None:
            filters.append(Product.is_active == is_active)
        if search:
            filters.append(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                )
            )
        if filters:
            query = query.where(and_(*filters))
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_low_stock_products(self) -> list[Product]:
        result = await self.session.execute(
            select(Product).where(
                and_(
                    Product.quantity_in_stock <= Product.min_stock_alert,
                    Product.is_active == True,
                )
            )
        )
        return list(result.scalars().all())


# ──────────────────────────────────────────────
# Client Repository
# ──────────────────────────────────────────────

class ClientRepository(BaseRepository[Client]):
    def __init__(self, session: AsyncSession):
        super().__init__(Client, session)

    async def get_by_email(self, email: str) -> Client | None:
        result = await self.session.execute(
            select(Client).where(Client.email == email)
        )
        return result.scalar_one_or_none()

    async def get_with_orders(self, client_id: int) -> Client | None:
        result = await self.session.execute(
            select(Client)
            .options(selectinload(Client.orders))
            .where(Client.id == client_id)
        )
        return result.scalar_one_or_none()


# ──────────────────────────────────────────────
# Order Repository
# ──────────────────────────────────────────────

class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_with_items(self, order_id: int) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_by_client(self, client_id: int, skip: int = 0, limit: int = 20) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.client_id == client_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(self, status: OrderStatusEnum) -> list[Order]:
        result = await self.session.execute(
            select(Order).where(Order.status == status)
        )
        return list(result.scalars().all())


# ──────────────────────────────────────────────
# StockMovement Repository
# ──────────────────────────────────────────────

class StockMovementRepository(BaseRepository[StockMovement]):
    def __init__(self, session: AsyncSession):
        super().__init__(StockMovement, session)

    async def get_by_product(
        self, product_id: int, skip: int = 0, limit: int = 50
    ) -> list[StockMovement]:
        result = await self.session.execute(
            select(StockMovement)
            .where(StockMovement.product_id == product_id)
            .order_by(StockMovement.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
