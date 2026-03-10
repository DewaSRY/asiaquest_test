from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User role enum."""
    USER = "user"
    VERIFIER = "verifier"
    APPROVER = "approver"


class UserCreate(BaseModel):
    """DTO for user registration."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """DTO for user login."""
    
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """DTO for user response."""
    
    id: int
    email: str
    username: str
    role: UserRole
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """DTO for JWT token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """DTO for JWT token payload."""
    
    sub: str
    exp: int
    type: str  # "access" or "refresh"
