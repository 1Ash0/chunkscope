"""
Celery Application Configuration
Background task processing
"""
from celery import Celery

from app.config import settings

celery_app = Celery(
    "chunkscope",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker"]  # Tasks will be defined here
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Rate limits
    task_default_rate_limit="10/s",
)

if __name__ == "__main__":
    celery_app.start()
