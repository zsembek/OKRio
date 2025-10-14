"""Celery tasks for the Data Connectors module."""
from __future__ import annotations

from celery import shared_task


@shared_task
def example_task(payload: dict[str, str]) -> dict[str, str]:
    """Placeholder task that echoes the payload."""

    return {"module": "data_connectors", **payload}

