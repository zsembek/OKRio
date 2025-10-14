"""API router for the Analytics domain."""
from __future__ import annotations

from fastapi import APIRouter, status

from ...schemas.health import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
def healthcheck() -> HealthStatus:
    """Return a simple status payload for liveness probes."""

    return HealthStatus(status="ok", module="analytics")
