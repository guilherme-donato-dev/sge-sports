from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import Token, UserCreate, UserResponse
from app.services.services import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, session: AsyncSession = Depends(get_db)):
    """Register a new user."""
    service = AuthService(session)
    return await service.register(data)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    """Login and receive JWT token."""
    service = AuthService(session)
    token = await service.authenticate(form_data.username, form_data.password)
    return Token(access_token=token)
