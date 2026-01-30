"""
ChunkScope FastAPI Application Factory
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api import api_router
from app.config import settings
from app.core import close_db, configure_logging, configure_middleware, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    configure_logging()
    await init_db()
    yield
    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Visual RAG pipeline builder and evaluator",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    
    # Configure middleware (CORS, error handling, logging)
    configure_middleware(app)
    
    # Include API routers
    app.include_router(api_router)
    
    @app.get("/")
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "online",
            "docs": "/api/docs"
        }

    return app


# Application instance
app = create_app()
