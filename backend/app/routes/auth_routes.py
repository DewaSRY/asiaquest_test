from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dtos.auth import UserCreate, UserResponse, UserLogin, Token
from app.models.user import User
from app.services.auth_service import register, login, refresh_tokens
from app.utils.auth import require_auth

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    description="Create a new user account with email, username, and password.",
)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user."""
    user = await register(db, user_data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate user with email and password, returns JWT tokens.",
)
async def login_user(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Login user and return tokens."""
    return await login(db, user_data.email, user_data.password)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh tokens",
    description="Get new access and refresh tokens using a valid refresh token.",
)
async def refresh(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Refresh access token."""
    return await refresh_tokens(db, refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the profile of the currently authenticated user.",
)
async def me(
    current_user: User = Depends(require_auth),
) -> UserResponse:
    """Get current user profile."""
    return UserResponse.model_validate(current_user)
