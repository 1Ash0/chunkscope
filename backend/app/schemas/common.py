"""
Common Pydantic Schemas
Shared request/response models
"""
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# Generic type for pagination
T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at fields."""
    created_at: datetime
    updated_at: Optional[datetime] = None


class IDMixin(BaseModel):
    """Mixin for UUID primary key."""
    id: UUID


# ============================================
# Pagination
# ============================================

class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int


def paginate(items: list[T], total: int, params: PaginationParams) -> PaginatedResponse[T]:
    """Create a paginated response."""
    pages = (total + params.per_page - 1) // params.per_page
    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        per_page=params.per_page,
        pages=pages
    )


# ============================================
# API Responses
# ============================================

class SuccessResponse(BaseModel):
    """Generic success response."""
    message: str = "Success"
    data: Optional[dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response format."""
    error: str
    code: str
    details: Optional[dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    environment: str
    database: str = "connected"
