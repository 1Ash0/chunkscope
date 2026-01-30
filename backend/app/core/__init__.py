"""
Core module exports
"""
from app.core.database import async_session_maker, close_db, engine, get_db, init_db
from app.core.errors import (
    AlreadyExistsError,
    AppException,
    AuthenticationError,
    BadRequestError,
    DatabaseError,
    ExternalServiceError,
    InvalidCredentialsError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitExceededError,
    TokenExpiredError,
    ValidationError,
)
from app.core.logging import configure_logging, get_logger
from app.core.middleware import configure_middleware
from app.core.rate_limit import limiter
from app.core.security import (
    TokenPair,
    TokenPayload,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)

__all__ = [
    # Database
    "engine",
    "async_session_maker",
    "get_db",
    "init_db",
    "close_db",
    # Errors
    "AppException",
    "AuthenticationError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "PermissionDeniedError",
    "NotFoundError",
    "AlreadyExistsError",
    "ValidationError",
    "BadRequestError",
    "RateLimitExceededError",
    "ExternalServiceError",
    "DatabaseError",
    # Logging
    "configure_logging",
    "get_logger",
    # Middleware
    "configure_middleware",
    # Rate limiting
    "limiter",
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "decode_token",
    "TokenPayload",
    "TokenPair",
]
