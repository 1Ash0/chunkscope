"""
V1 Router Exports
"""
from app.api.v1.auth import router as auth_router
from app.api.v1.chunks import router as chunks_router
from app.api.v1.config import router as config_router
from app.api.v1.documents import router as documents_router
from app.api.v1.evaluations import router as evaluations_router
from app.api.v1.health import router as health_router
from app.api.v1.pipelines import router as pipelines_router
from app.api.v1.websockets import router as websockets_router

__all__ = [
    "auth_router",
    "chunks_router",
    "config_router",
    "documents_router",
    "evaluations_router",
    "health_router",
    "pipelines_router",
    "websockets_router",
]

