import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.auth_service import register, login, refresh_tokens, get_current_user
from app.dtos.auth import UserCreate, Token
from app.models.user import User
from app.errors import ConflictException, UnauthorizedException, NotFoundException


class TestRegister:
    """Tests for the register function."""

    @pytest.mark.asyncio
    async def test_register_success(self, mock_db, user_create_data):
        """Test successful user registration."""
        with patch("app.services.auth_service.get_user_by_email", new_callable=AsyncMock) as mock_get_email, \
             patch("app.services.auth_service.get_user_by_username", new_callable=AsyncMock) as mock_get_username, \
             patch("app.services.auth_service.hash_password") as mock_hash:
            
            mock_get_email.return_value = None
            mock_get_username.return_value = None
            mock_hash.return_value = "hashed_password"
            
            # Mock db operations
            mock_db.add = MagicMock()
            mock_db.flush = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await register(mock_db, user_create_data)

            assert result.email == user_create_data.email
            assert result.username == user_create_data.username
            mock_get_email.assert_called_once_with(mock_db, user_create_data.email)
            mock_get_username.assert_called_once_with(mock_db, user_create_data.username)
            mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_email_already_exists(self, mock_db, user_create_data, sample_user):
        """Test registration fails when email already exists."""
        with patch("app.services.auth_service.get_user_by_email", new_callable=AsyncMock) as mock_get_email:
            mock_get_email.return_value = sample_user

            with pytest.raises(ConflictException) as exc_info:
                await register(mock_db, user_create_data)

            assert "Email already registered" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_username_already_exists(self, mock_db, user_create_data, sample_user):
        """Test registration fails when username already exists."""
        with patch("app.services.auth_service.get_user_by_email", new_callable=AsyncMock) as mock_get_email, \
             patch("app.services.auth_service.get_user_by_username", new_callable=AsyncMock) as mock_get_username:
            
            mock_get_email.return_value = None
            mock_get_username.return_value = sample_user

            with pytest.raises(ConflictException) as exc_info:
                await register(mock_db, user_create_data)

            assert "Username already taken" in str(exc_info.value.detail)


class TestLogin:
    """Tests for the login function."""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_db, sample_user):
        """Test successful login."""
        with patch("app.services.auth_service.get_user_by_email", new_callable=AsyncMock) as mock_get_email, \
             patch("app.services.auth_service.verify_password") as mock_verify, \
             patch("app.services.auth_service.create_access_token") as mock_access, \
             patch("app.services.auth_service.create_refresh_token") as mock_refresh:
            
            mock_get_email.return_value = sample_user
            mock_verify.return_value = True
            mock_access.return_value = "access_token"
            mock_refresh.return_value = "refresh_token"

            result = await login(mock_db, "test@example.com", "password123")

            assert isinstance(result, Token)
            assert result.access_token == "access_token"
            assert result.refresh_token == "refresh_token"
            mock_verify.assert_called_once_with("password123", sample_user.hashed_password)

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, mock_db):
        """Test login fails when user doesn't exist."""
        with patch("app.services.auth_service.get_user_by_email", new_callable=AsyncMock) as mock_get_email:
            mock_get_email.return_value = None

            with pytest.raises(UnauthorizedException) as exc_info:
                await login(mock_db, "nonexistent@example.com", "password123")

            assert "Invalid email or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, mock_db, sample_user):
        """Test login fails with invalid password."""
        with patch("app.services.auth_service.get_user_by_email", new_callable=AsyncMock) as mock_get_email, \
             patch("app.services.auth_service.verify_password") as mock_verify:
            
            mock_get_email.return_value = sample_user
            mock_verify.return_value = False

            with pytest.raises(UnauthorizedException) as exc_info:
                await login(mock_db, "test@example.com", "wrongpassword")

            assert "Invalid email or password" in str(exc_info.value.detail)


class TestRefreshTokens:
    """Tests for the refresh_tokens function."""

    @pytest.mark.asyncio
    async def test_refresh_tokens_success(self, mock_db, sample_user):
        """Test successful token refresh."""
        with patch("app.services.auth_service.decode_token") as mock_decode, \
             patch("app.services.auth_service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
             patch("app.services.auth_service.create_access_token") as mock_access, \
             patch("app.services.auth_service.create_refresh_token") as mock_refresh:
            
            mock_decode.return_value = {"type": "refresh", "sub": "1"}
            mock_get_user.return_value = sample_user
            mock_access.return_value = "new_access_token"
            mock_refresh.return_value = "new_refresh_token"

            result = await refresh_tokens(mock_db, "valid_refresh_token")

            assert isinstance(result, Token)
            assert result.access_token == "new_access_token"
            assert result.refresh_token == "new_refresh_token"

    @pytest.mark.asyncio
    async def test_refresh_tokens_invalid_token_type(self, mock_db):
        """Test refresh fails with access token instead of refresh token."""
        with patch("app.services.auth_service.decode_token") as mock_decode:
            mock_decode.return_value = {"type": "access", "sub": "1"}

            with pytest.raises(UnauthorizedException) as exc_info:
                await refresh_tokens(mock_db, "access_token")

            assert "Invalid token type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_refresh_tokens_user_not_found(self, mock_db):
        """Test refresh fails when user doesn't exist."""
        with patch("app.services.auth_service.decode_token") as mock_decode, \
             patch("app.services.auth_service.get_user_by_id", new_callable=AsyncMock) as mock_get_user:
            
            mock_decode.return_value = {"type": "refresh", "sub": "999"}
            mock_get_user.return_value = None

            with pytest.raises(NotFoundException) as exc_info:
                await refresh_tokens(mock_db, "valid_refresh_token")

            assert "User not found" in str(exc_info.value.detail)


class TestGetCurrentUser:
    """Tests for the get_current_user function."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_db, sample_user):
        """Test successfully getting current user."""
        with patch("app.services.auth_service.decode_token") as mock_decode, \
             patch("app.services.auth_service.get_user_by_id", new_callable=AsyncMock) as mock_get_user:
            
            mock_decode.return_value = {"type": "access", "sub": "1"}
            mock_get_user.return_value = sample_user

            result = await get_current_user(mock_db, "valid_access_token")

            assert result == sample_user
            mock_get_user.assert_called_once_with(mock_db, 1)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token_type(self, mock_db):
        """Test fails with refresh token instead of access token."""
        with patch("app.services.auth_service.decode_token") as mock_decode:
            mock_decode.return_value = {"type": "refresh", "sub": "1"}

            with pytest.raises(UnauthorizedException) as exc_info:
                await get_current_user(mock_db, "refresh_token")

            assert "Invalid token type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, mock_db):
        """Test fails when user doesn't exist."""
        with patch("app.services.auth_service.decode_token") as mock_decode, \
             patch("app.services.auth_service.get_user_by_id", new_callable=AsyncMock) as mock_get_user:
            
            mock_decode.return_value = {"type": "access", "sub": "999"}
            mock_get_user.return_value = None

            with pytest.raises(NotFoundException) as exc_info:
                await get_current_user(mock_db, "valid_access_token")

            assert "User not found" in str(exc_info.value.detail)
