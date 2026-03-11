import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.models import (
    Category,
    Client,
    Order,
    OrderItem,
    OrderStatusEnum,
    Product,
    StockMovement,
    StockMovementTypeEnum,
    User,
)
from app.repositories.repositories import (
    CategoryRepository,
    ClientRepository,
    OrderRepository,
    ProductRepository,
    StockMovementRepository,
    UserRepository,
)
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    ClientCreate,
    ClientUpdate,
    OrderCreate,
    OrderUpdateStatus,
    ProductCreate,
    ProductUpdate,
    StockMovementCreate,
    UserCreate,
)


# ──────────────────────────────────────────────
# Auth Service
# ──────────────────────────────────────────────

class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def register(self, data: UserCreate) -> User:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )
        user = User(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return await self.repo.create(user)

    async def authenticate(self, email: str, password: str) -> str:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user.",
            )
        return create_access_token({"sub": str(user.id)})

    async def get_current_user(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive.",
            )
        return user


# ──────────────────────────────────────────────
# Category Service
# ──────────────────────────────────────────────

class CategoryService:
    def __init__(self, session: AsyncSession):
        self.repo = CategoryRepository(session)

    async def create(self, data: CategoryCreate) -> Category:
        if await self.repo.get_by_name(data.name):
            raise HTTPException(status_code=400, detail="Category already exists.")
        cat = Category(**data.model_dump())
        return await self.repo.create(cat)

    async def list_all(self, skip: int = 0, limit: int = 20) -> list[Category]:
        return await self.repo.get_all(skip, limit)

    async def get(self, id: int) -> Category:
        cat = await self.repo.get_by_id(id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found.")
        return cat

    async def update(self, id: int, data: CategoryUpdate) -> Category:
        cat = await self.get(id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cat, field, value)
        return cat

    async def delete(self, id: int) -> None:
        cat = await self.get(id)
        await self.repo.delete(cat)


# ──────────────────────────────────────────────
# Product Service
# ──────────────────────────────────────────────

class ProductService:
    def __init__(self, session: AsyncSession):
        self.repo = ProductRepository(session)
        self.stock_repo = StockMovementRepository(session)

    async def create(self, data: ProductCreate) -> Product:
        if await self.repo.get_by_sku(data.sku):
            raise HTTPException(status_code=400, detail="SKU already exists.")
        product = Product(**data.model_dump())
        created = await self.repo.create(product)
        # Register initial stock movement if stock > 0
        if data.quantity_in_stock > 0:
            movement = StockMovement(
                product_id=created.id,
                movement_type=StockMovementTypeEnum.IN,
                quantity=data.quantity_in_stock,
                quantity_before=0,
                quantity_after=data.quantity_in_stock,
                reason="Initial stock",
            )
            await self.stock_repo.create(movement)
        return created

    async def get(self, id: int) -> Product:
        product = await self.repo.get_by_id(id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        return product

    async def list_all(self, skip=0, limit=20, **filters) -> list[Product]:
        return await self.repo.get_all_filtered(skip=skip, limit=limit, **filters)

    async def update(self, id: int, data: ProductUpdate) -> Product:
        product = await self.get(id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        return product

    async def delete(self, id: int) -> None:
        product = await self.get(id)
        product.is_active = False

    async def get_low_stock(self) -> list[Product]:
        return await self.repo.get_low_stock_products()


# ──────────────────────────────────────────────
# Client Service
# ──────────────────────────────────────────────

class ClientService:
    def __init__(self, session: AsyncSession):
        self.repo = ClientRepository(session)

    async def create(self, data: ClientCreate) -> Client:
        if await self.repo.get_by_email(data.email):
            raise HTTPException(status_code=400, detail="Email already registered.")
        client = Client(**data.model_dump())
        return await self.repo.create(client)

    async def get(self, id: int) -> Client:
        client = await self.repo.get_by_id(id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found.")
        return client

    async def list_all(self, skip=0, limit=20) -> list[Client]:
        return await self.repo.get_all(skip, limit)

    async def update(self, id: int, data: ClientUpdate) -> Client:
        client = await self.get(id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(client, field, value)
        return client

    async def get_with_orders(self, id: int) -> Client:
        client = await self.repo.get_with_orders(id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found.")
        return client


# ──────────────────────────────────────────────
# Order Service
# ──────────────────────────────────────────────

class OrderService:
    def __init__(self, session: AsyncSession):
        self.repo = OrderRepository(session)
        self.product_repo = ProductRepository(session)
        self.stock_repo = StockMovementRepository(session)

    def _generate_order_number(self) -> str:
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"

    async def create(self, data: OrderCreate) -> Order:
        items = []
        total = Decimal("0")

        for item_data in data.items:
            product = await self.product_repo.get_by_id(item_data.product_id)
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {item_data.product_id} not found.",
                )
            if product.quantity_in_stock < item_data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product '{product.name}'. "
                           f"Available: {product.quantity_in_stock}.",
                )
            subtotal = product.price * item_data.quantity
            total += subtotal
            items.append((product, item_data.quantity, subtotal))

        order = Order(
            order_number=self._generate_order_number(),
            client_id=data.client_id,
            total_amount=total,
            notes=data.notes,
        )
        created_order = await self.repo.create(order)

        for product, qty, subtotal in items:
            before = product.quantity_in_stock
            product.quantity_in_stock -= qty
            after = product.quantity_in_stock

            order_item = OrderItem(
                order_id=created_order.id,
                product_id=product.id,
                quantity=qty,
                unit_price=product.price,
                subtotal=subtotal,
            )
            self.repo.session.add(order_item)

            movement = StockMovement(
                product_id=product.id,
                movement_type=StockMovementTypeEnum.OUT,
                quantity=qty,
                quantity_before=before,
                quantity_after=after,
                order_id=created_order.id,
                reason=f"Sale order {created_order.order_number}",
            )
            await self.stock_repo.create(movement)

        return created_order

    async def get(self, id: int) -> Order:
        order = await self.repo.get_with_items(id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")
        return order

    async def list_all(self, skip=0, limit=20) -> list[Order]:
        return await self.repo.get_all(skip, limit)

    async def update_status(self, id: int, data: OrderUpdateStatus) -> Order:
        order = await self.get(id)
        if order.status == OrderStatusEnum.CANCELLED:
            raise HTTPException(status_code=400, detail="Cannot update a cancelled order.")
        order.status = data.status
        return order


# ──────────────────────────────────────────────
# Stock Service
# ──────────────────────────────────────────────

class StockService:
    def __init__(self, session: AsyncSession):
        self.repo = StockMovementRepository(session)
        self.product_repo = ProductRepository(session)

    async def add_movement(self, data: StockMovementCreate) -> StockMovement:
        product = await self.product_repo.get_by_id(data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")

        before = product.quantity_in_stock

        if data.movement_type == StockMovementTypeEnum.IN:
            product.quantity_in_stock += data.quantity
        elif data.movement_type == StockMovementTypeEnum.OUT:
            if product.quantity_in_stock < data.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock.")
            product.quantity_in_stock -= data.quantity
        elif data.movement_type == StockMovementTypeEnum.ADJUST:
            product.quantity_in_stock = data.quantity

        after = product.quantity_in_stock

        movement = StockMovement(
            product_id=product.id,
            movement_type=data.movement_type,
            quantity=data.quantity,
            quantity_before=before,
            quantity_after=after,
            reason=data.reason,
        )
        return await self.repo.create(movement)

    async def get_product_movements(
        self, product_id: int, skip=0, limit=50
    ) -> list[StockMovement]:
        return await self.repo.get_by_product(product_id, skip, limit)
