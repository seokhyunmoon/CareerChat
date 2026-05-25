from __future__ import annotations

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "careerchat_ai",
    broker=settings.redis_broker_url,
    backend=settings.redis_result_backend_url,
)

celery_app.conf.update(
    accept_content=["json"],
    enable_utc=True,
    result_serializer="json",
    task_serializer="json",
    timezone="UTC",
)
