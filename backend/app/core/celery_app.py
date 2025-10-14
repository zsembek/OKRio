"""Celery application definition for asynchronous workloads."""
from __future__ import annotations

from celery import Celery

from .config import get_settings


def create_celery() -> Celery:
    settings = get_settings()

    broker_url = settings.rabbitmq_url or settings.redis_url
    backend_url = settings.redis_url

    celery_app = Celery(
        "okrio",
        broker=broker_url,
        backend=backend_url,
        include=[
            "app.modules.notifications.tasks",
            "app.modules.analytics.tasks",
            "app.modules.data_connectors.tasks",
        ],
    )

    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        worker_max_tasks_per_child=100,
        beat_scheduler="celery.beat:PersistentScheduler",
    )

    return celery_app


celery_app = create_celery()
