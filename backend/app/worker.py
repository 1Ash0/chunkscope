"""
Celery Worker
Defines background tasks
"""
import time

from app.core.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    """Dummy task to verify Celery setup."""
    logger.info(f"Test task received: {word}")
    time.sleep(1)
    return f"test task return {word}"
