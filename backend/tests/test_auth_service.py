import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import register, login, refresh_tokens, get_current_user
from app.dtos.auth import UserCreate, Token
from app.models.user import User
from app.errors import ConflictException, UnauthorizedException, NotFoundException
from app.utils.security import create_access_token, create_refresh_token


class TestRegister:
    """Tests for the register function."""

    @pytest.mark.asyncio
    async def test_register_success(self, db_session: AsyncSession, user_create_data: UserCreate):
        """Test successful user registration."""
        result = await register(db_session, user_create_data)

        assert result.email == user_create_data.email
        assert result.username == user_create_data.username
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_register_email_already_exists(self, db_session: AsyncSession, user_create_data: UserCreate, sample_user: User):
        """Test registration fails when email already exists."""
        # sample_user already exists with email "test@example.com"
        user_create_data.email = sample_user.email

        with pytest.raises(ConflictException) as exc_info:
            await register(db_session, user_create_data)

        assert "Email already registered" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_username_already_exists(self, db_session: AsyncSession, user_create_data: UserCreate, sample_user: User):
        """Test registration fails when username already exists."""
        # sample_user already exists with username "testuser"
        # Use a different email to ensure username check is triggered
        user_create_data.email = "different@example.com"
        user_create_data.username = sample_user.username

        with pytest.raises(ConflictException) as exc_info:
            await register(db_session, user_create_data)

        assert "Username already taken" in str(exc_info.value.detail)


class TestLogin:
    """Tests for the login function."""

    @pytest.mark.asyncio
    async def test_login_success(self, db_session: AsyncSession, sample_user: User):
        """Test successful login."""
        result = await login(db_session, "test@example.com", "password123")

        assert isinstance(result, Token)
        assert result.access_token is not None
        assert result.refresh_token is not None

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, db_session: AsyncSession):
        """Test login fails when user doesn't exist."""
        with pytest.raises(UnauthorizedException) as exc_info:
            await login(db_session, "nonexistent@example.com", "password123")

        assert "Invalid email or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, db_session: AsyncSession, sample_user: User):
        """Test login fails with invalid password."""
        with pytest.raises(UnauthorizedException) as exc_info:
            await login(db_session, "test@example.com", "wrongpassword")

        assert "Invalid email or password" in str(exc_info.value.detail)


class TestRefreshTokens:
    """Tests for the refresh_tokens function."""

    @pytest.mark.asyncio
    async def test_refresh_tokens_success(self, db_session: AsyncSession, sample_user: User):
        """Test successful token refresh."""
        refresh_token = create_refresh_token(subject=sample_user.id)

        result = await refresh_tokens(db_session, refresh_token)

        assert isinstance(result, Token)
        assert result.access_token is not None
        assert result.refresh_token is not None

    @pytest.mark.asyncio
    async def test_refresh_tokens_invalid_token_type(self, db_session: AsyncSession, sample_user: User):
        """Test refresh fails with access token instead of refresh token."""
        access_token = create_access_token(subject=sample_user.id)

        with pytest.raises(UnauthorizedException) as exc_info:
            await refresh_tokens(db_session, access_token)

        assert "Invalid token type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_refresh_tokens_user_not_found(self, db_session: AsyncSession):
        """Test refresh fails when user doesn't exist."""
        # Create a refresh token for a non-existent user
        refresh_token = create_refresh_token(subject=999)

        with pytest.raises(NotFoundException) as exc_info:
            await refresh_tokens(db_session, refresh_token)

        assert "User not found" in str(exc_info.value.detail)


class TestGetCurrentUser:
    """Tests for the get_current_user function."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, db_session: AsyncSession, sample_user: User):
        """Test successfully getting current user."""
        access_token = create_access_token(subject=sample_user.id)

        result = await get_current_user(db_session, access_token)

        assert result.id == sample_user.id
        assert result.email == sample_user.email

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token_type(self, db_session: AsyncSession, sample_user: User):
        """Test fails with refresh token instead of access token."""
        refresh_token = create_refresh_token(subject=sample_user.id)

        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user(db_session, refresh_token)

        assert "Invalid token type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, db_session: AsyncSession):
        """Test fails when user doesn't exist."""
        # Create an access token for a non-existent user
        access_token = create_access_token(subject=999)

        with pytest.raises(NotFoundException) as exc_info:
            await get_current_user(db_session, access_token)

        assert "User not found" in str(exc_info.value.detail)
