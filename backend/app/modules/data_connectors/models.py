"""Persistence models for data connector operations."""
from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, JSON, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DataSelectionStatus(str, enum.Enum):
    """Lifecycle status of a connector data selection."""

    RUNNING = "running"
    SUCCESS = "success"
    FAIL_SAFE = "fail_safe"
    FAILURE = "failure"


class DataSelectionLog(Base):
    """Audit log entry for data extractions performed by connectors."""

    __tablename__ = "data_selection_logs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    connector_type: Mapped[str] = mapped_column(String(100), nullable=False)
    operation: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(500), nullable=False)
    parameters: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[DataSelectionStatus] = mapped_column(
        Enum(DataSelectionStatus), nullable=False, default=DataSelectionStatus.RUNNING
    )
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    fail_safe_triggered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def complete(
        self,
        status: DataSelectionStatus,
        row_count: int | None = None,
        *,
        error_message: str | None = None,
        details: dict[str, Any] | None = None,
        fail_safe_triggered: bool | None = None,
    ) -> None:
        """Mark the log entry as finished with computed metadata."""

        finished = datetime.now(timezone.utc)
        self.status = status
        self.finished_at = finished
        self.duration_ms = int((finished - self.started_at).total_seconds() * 1000)
        self.row_count = row_count
        self.error_message = error_message
        if details is not None:
            self.details = details
        if fail_safe_triggered is not None:
            self.fail_safe_triggered = fail_safe_triggered
