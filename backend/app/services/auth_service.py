from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.dtos.auth import UserCreate, Token
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.errors import ConflictException, UnauthorizedException, NotFoundException


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Get user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def register(db: AsyncSession, user_data: UserCreate) -> User:
    """Register a new user."""
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise ConflictException(detail="Email already registered")

    existing_username = await get_user_by_username(db, user_data.username)
    if existing_username:
        raise ConflictException(detail="Username already taken")

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def login(db: AsyncSession, email: str, password: str) -> Token:
    """Authenticate user and return tokens."""
    user = await get_user_by_email(db, email)

    if not user:
        raise UnauthorizedException(detail="Invalid email or password")

    if not verify_password(password, user.hashed_password):
        raise UnauthorizedException(detail="Invalid email or password")

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> Token:
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise UnauthorizedException(detail="Invalid token type")

    user_id = payload.get("sub")
    user = await get_user_by_id(db, int(user_id))

    if not user:
        raise NotFoundException(detail="User not found")

    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


async def get_current_user(db: AsyncSession, token: str) -> User:
    """Get current user from access token."""
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise UnauthorizedException(detail="Invalid token type")

    user_id = payload.get("sub")
    user = await get_user_by_id(db, int(user_id))

    if not user:
        raise NotFoundException(detail="User not found")

    return user
