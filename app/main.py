from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine
from app.models.models import Base  # noqa: F401 — needed for metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if not exists (dev only — use Alembic in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## SGE Sports Store — API

Sistema de Gestão de Estoque para loja de roupas esportivas (NFL, NBA, MLB, NHL).

### Features
- 🛍️ Gestão de produtos por liga e time
- 📦 Controle de estoque com histórico de movimentações
- 🧾 Pedidos e vendas com atualização automática de estoque
- 👥 Cadastro e histórico de clientes
- 🤖 Assistente IA (LangChain) para análise de estoque
- 🔐 Autenticação JWT

### Desenvolvido por
Guilherme Donato — [github.com/guilhermedonato](https://github.com/guilhermedonato)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
