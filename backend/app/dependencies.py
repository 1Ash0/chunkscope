"""
FastAPI Dependencies (Dependency Injection)
Provides reusable dependencies for routes
"""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.errors import AuthenticationError, NotFoundError
from app.core.security import decode_token
from app.models import User


# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Optional[User]:
    """
    Get current user from JWT token, or None if not authenticated.
    Use this for endpoints that work with or without auth.
    """
    if not credentials:
        return None
    
    try:
        token_payload = decode_token(credentials.credentials)
        user_id = UUID(token_payload.sub)
    except Exception:
        return None
    
    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current user from JWT token.
    Raises AuthenticationError if not authenticated.
    """
    if not credentials:
        raise AuthenticationError("Bearer token required")
    
    token_payload = decode_token(credentials.credentials)
    user_id = UUID(token_payload.sub)
    
    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User", user_id)
    
    return user


# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[Optional[User], Depends(get_current_user_optional)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
