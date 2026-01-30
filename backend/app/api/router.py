"""
Main API Router Aggregator
Combines all API routers under /api/v1 prefix
"""
from fastapi import APIRouter

# Import direct endpoint modules if __init__ aggregation is messy
from app.api.v1 import (
    health_router,
    auth_router,
    documents_router,
    chunks_router,
    evaluations_router,
    config_router,
    pipelines_router
)

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include all v1 routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(pipelines_router)
api_router.include_router(documents_router, tags=["documents"])
api_router.include_router(chunks_router, tags=["chunks"])
api_router.include_router(evaluations_router, tags=["evaluations"])
api_router.include_router(config_router, tags=["config"])
# api_router.include_router(websockets_router)
