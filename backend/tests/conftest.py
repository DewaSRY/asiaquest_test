import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, UTC

from app.models.user import User, UserRole
from app.dtos.auth import UserCreate


@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    return AsyncMock()


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = MagicMock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.username = "testuser"
    user.hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S3mD4.K9rRfYZO"  # hashed "password123"
    user.role = UserRole.USER
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)
    return user


@pytest.fixture
def user_create_data():
    """Create sample user registration data."""
    return UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="securepassword123",
    )
