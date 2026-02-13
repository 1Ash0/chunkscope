"""
FastAPI Middleware Configuration
Error handling, CORS, request logging
"""
import time
from typing import Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.core.errors import AppException
from app.core.logging import get_logger
from app.core.rate_limit import limiter

logger = get_logger(__name__)


def configure_middleware(app: FastAPI) -> None:
    """Configure all middleware for the FastAPI app."""
    
    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Custom exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    # Request logging and timing
    app.add_middleware(RequestLoggingMiddleware)
    
    # CORS - MUST be added LAST so it's the outermost middleware
    # This ensures CORS headers are added to ALL responses, including errors
    logger.info("cors_origins_configured", origins=settings.cors_origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing information."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID for tracing
        request_id = str(uuid4())[:8]
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.perf_counter()
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log unhandled errors
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(e)
            )
            raise
        
        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Log request
        log_method = logger.info if response.status_code < 400 else logger.warning
        log_method(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )
        
        # Add request ID header
        response.headers["X-Request-ID"] = request_id
        
        return response


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.warning(
        "app_exception",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        request_id=getattr(request.state, "request_id", None)
    )
    
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details,
        }
    )
    
    # Explicitly add CORS headers to error responses
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    import traceback
    print(f"\n!!! UNHANDLED EXCEPTION !!!\n{str(exc)}\n{traceback.format_exc()}\n", flush=True)
    logger.exception(
        "unhandled_exception",
        error=str(exc),
        request_id=getattr(request.state, "request_id", None)
    )
    
    # Don't expose internal errors in production
    if settings.debug:
        message = str(exc)
    else:
        message = "An unexpected error occurred"
    
    response = JSONResponse(
        status_code=500,
        content={
            "error": message,
            "code": "INTERNAL_ERROR",
        }
    )
    
    # Explicitly add CORS headers to error responses
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response
