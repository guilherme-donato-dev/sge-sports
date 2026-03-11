import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@test.com", "password": "123456"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@test.com", "password": "123456"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"name": "Guilherme", "email": "gui@test.com", "password": "senha123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "gui@test.com"


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/categories/",
        json={"name": "Camisetas", "description": "Camisetas oficiais"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Camisetas"


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, auth_headers: dict):
    # Create category first
    cat_resp = await client.post(
        "/api/v1/categories/",
        json={"name": "Jerseys"},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]

    resp = await client.post(
        "/api/v1/products/",
        json={
            "name": "Jersey Kansas City Chiefs",
            "sku": "NFL-KC-001",
            "price": "299.99",
            "cost_price": "150.00",
            "league": "NFL",
            "team": "Kansas City Chiefs",
            "size": "G",
            "quantity_in_stock": 50,
            "min_stock_alert": 10,
            "category_id": cat_id,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["sku"] == "NFL-KC-001"
    assert data["league"] == "NFL"
