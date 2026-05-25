from __future__ import annotations

from app.workers.celery_app import celery_app


def test_celery_app_uses_configured_redis_urls() -> None:
    assert celery_app.main == "careerchat_ai"
    assert celery_app.conf.broker_url == "redis://localhost:6379/0"
    assert celery_app.conf.result_backend == "redis://localhost:6379/1"


def test_celery_app_uses_json_serialization() -> None:
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.result_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.timezone == "UTC"
    assert celery_app.conf.enable_utc is True
