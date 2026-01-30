"""
Authentication Endpoints
Registration, login, token refresh
"""
from fastapi import APIRouter
from sqlalchemy import select

from app.core import (
    create_token_pair,
    hash_password,
    verify_password,
    decode_token,
)
from app.core.errors import AlreadyExistsError, InvalidCredentialsError
from app.dependencies import CurrentUser, DbSession
from app.models import User
from app.schemas import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(request: RegisterRequest, db: DbSession) -> AuthResponse:
    """Register a new user."""
    # Check if email already exists
    existing = await db.execute(
        select(User).where(User.email == request.email)
    )
    if existing.scalar_one_or_none():
        raise AlreadyExistsError("User", request.email)
    
    # Create user
    user = User(
        email=request.email,
        name=request.name,
        password_hash=hash_password(request.password),
    )
    db.add(user)
    await db.flush()
    
    # Generate tokens
    tokens = create_token_pair(str(user.id))
    
    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
        ),
        tokens=TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: DbSession) -> AuthResponse:
    """Authenticate user and return tokens."""
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash:
        raise InvalidCredentialsError()
    
    if not verify_password(request.password, user.password_hash):
        raise InvalidCredentialsError()
    
    # Generate tokens
    tokens = create_token_pair(str(user.id))
    
    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
        ),
        tokens=TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """Refresh access token using refresh token."""
    # Decode refresh token
    payload = decode_token(request.refresh_token, expected_type="refresh")
    
    # Generate new token pair
    tokens = create_token_pair(payload.sub)
    
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """Get current authenticated user info."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
    )
