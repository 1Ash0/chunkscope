"""
Custom Exception Classes for ChunkScope
Provides consistent error handling across the application
"""
from typing import Any, Optional


class AppException(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: str = "INTERNAL_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


# ============================================
# Authentication Errors (401, 403)
# ============================================

class AuthenticationError(AppException):
    """User is not authenticated."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            code="AUTHENTICATION_REQUIRED"
        )


class InvalidCredentialsError(AppException):
    """Invalid username or password."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            message=message,
            status_code=401,
            code="INVALID_CREDENTIALS"
        )


class TokenExpiredError(AppException):
    """JWT token has expired."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            message=message,
            status_code=401,
            code="TOKEN_EXPIRED"
        )


class PermissionDeniedError(AppException):
    """User lacks permission for this action."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=403,
            code="PERMISSION_DENIED"
        )


# ============================================
# Resource Errors (404, 409)
# ============================================

class NotFoundError(AppException):
    """Requested resource not found."""
    
    def __init__(self, resource: str, resource_id: str = ""):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=message,
            status_code=404,
            code="NOT_FOUND",
            details={"resource": resource, "id": resource_id}
        )


class AlreadyExistsError(AppException):
    """Resource already exists."""
    
    def __init__(self, resource: str, identifier: str = ""):
        message = f"{resource} already exists"
        if identifier:
            message = f"{resource} '{identifier}' already exists"
        super().__init__(
            message=message,
            status_code=409,
            code="ALREADY_EXISTS",
            details={"resource": resource}
        )


# ============================================
# Validation Errors (400, 422)
# ============================================

class ValidationError(AppException):
    """Input validation failed."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=422,
            code="VALIDATION_ERROR",
            details=details
        )


class BadRequestError(AppException):
    """Malformed request."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            code="BAD_REQUEST"
        )


# ============================================
# Rate Limiting (429)
# ============================================

class RateLimitExceededError(AppException):
    """Too many requests."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds",
            status_code=429,
            code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )


# ============================================
# External Service Errors (502, 503)
# ============================================

class ExternalServiceError(AppException):
    """External API call failed."""
    
    def __init__(self, service: str, message: str = "Service unavailable"):
        super().__init__(
            message=f"{service}: {message}",
            status_code=502,
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


class DatabaseError(AppException):
    """Database operation failed."""
    
    def __init__(self, message: str = "Database error"):
        super().__init__(
            message=message,
            status_code=503,
            code="DATABASE_ERROR"
        )


# ============================================
# PDF Extraction Errors (400, 422)
# ============================================

class PDFExtractionError(AppException):
    """Base error for PDF extraction failures."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            status_code=422,
            code="PDF_EXTRACTION_ERROR",
            details=details
        )


class CorruptedPDFError(PDFExtractionError):
    """PDF file is corrupted or invalid."""
    
    def __init__(self, message: str = "PDF file is corrupted or cannot be read"):
        super().__init__(
            message=message,
            details={"reason": "corrupted"}
        )


class PasswordProtectedError(PDFExtractionError):
    """PDF requires a password to open."""
    
    def __init__(self, message: str = "PDF is password-protected"):
        super().__init__(
            message=message,
            details={"reason": "password_protected"}
        )


class ExtractionTimeoutError(PDFExtractionError):
    """PDF extraction exceeded time limit."""
    
    def __init__(self, timeout_seconds: int = 300):
        super().__init__(
            message=f"PDF extraction timed out after {timeout_seconds} seconds",
            details={"reason": "timeout", "timeout_seconds": timeout_seconds}
        )
