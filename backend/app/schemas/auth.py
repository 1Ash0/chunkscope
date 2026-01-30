"""
Authentication Schemas
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============================================
# Request Schemas
# ============================================

class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: Optional[str] = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ============================================
# Response Schemas
# ============================================

class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User data response."""
    id: str
    email: str
    name: Optional[str]
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Login/register response with user and tokens."""
    user: UserResponse
    tokens: TokenResponse
