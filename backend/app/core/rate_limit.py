"""
Rate Limiting with SlowAPI
Uses Redis if available, falls back to in-memory storage
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


def get_user_id_or_ip(request) -> str:
    """
    Rate limit key function.
    Uses user_id if authenticated, otherwise IP address.
    """
    # Check if user is authenticated
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"
    return f"ip:{get_remote_address(request)}"


def _create_limiter() -> Limiter:
    """Create limiter with Redis or fallback to memory."""
    try:
        # Try Redis first
        limiter = Limiter(
            key_func=get_user_id_or_ip,
            default_limits=[f"{settings.rate_limit_per_minute}/minute"],
            storage_uri=settings.redis_url,
        )
        return limiter
    except Exception:
        # Fallback to in-memory storage
        return Limiter(
            key_func=get_user_id_or_ip,
            default_limits=[f"{settings.rate_limit_per_minute}/minute"],
            storage_uri="memory://",
        )


# Global rate limiter instance
limiter = _create_limiter()
