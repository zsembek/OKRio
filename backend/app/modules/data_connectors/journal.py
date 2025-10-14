"""Utilities for persisting connector execution logs."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, ContextManager
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.database import db

from .models import DataSelectionLog, DataSelectionStatus

SessionFactory = Callable[[], ContextManager[Session]]


@dataclass
class JournalRecordContext:
    """Mutable context passed to connector operations for logging."""

    journal: "DataSelectionJournal"
    entry_id: UUID
    completed: bool = field(default=False, init=False)

    def succeed(
        self,
        *,
        row_count: int | None = None,
        details: dict[str, Any] | None = None,
        fail_safe: bool = False,
        error: Exception | str | None = None,
    ) -> None:
        """Mark the execution as successful (optionally via fail-safe)."""

        self.journal.finalise(
            self.entry_id,
            DataSelectionStatus.FAIL_SAFE if fail_safe else DataSelectionStatus.SUCCESS,
            row_count=row_count,
            details=details,
            error_message=str(error) if error else None,
            fail_safe_triggered=fail_safe,
        )
        self.completed = True

    def fail(self, error: Exception | str, *, details: dict[str, Any] | None = None) -> None:
        """Mark the execution as failed."""

        self.journal.finalise(
            self.entry_id,
            DataSelectionStatus.FAILURE,
            row_count=None,
            details=details,
            error_message=str(error),
            fail_safe_triggered=False,
        )
        self.completed = True


class DataSelectionJournal:
    """Persist execution metadata for connector data selections."""

    def __init__(self, session_factory: SessionFactory | None = None) -> None:
        self._session_factory = session_factory or db.session

    @contextmanager
    def record(
        self,
        *,
        connector_type: str,
        operation: str,
        source: str,
        parameters: dict[str, Any] | None = None,
    ) -> JournalRecordContext:
        """Create a log entry and yield a context for completion updates."""

        entry = DataSelectionLog(
            connector_type=connector_type,
            operation=operation,
            source=source,
            parameters=parameters,
        )
        with self._session_factory() as session:
            session.add(entry)

        context = JournalRecordContext(self, entry.id)
        try:
            yield context
        except Exception as exc:  # pragma: no cover - defensive branch
            if not context.completed:
                context.fail(exc)
            raise
        finally:
            if not context.completed:
                context.succeed()

    def finalise(
        self,
        entry_id: UUID,
        status: DataSelectionStatus,
        *,
        row_count: int | None,
        details: dict[str, Any] | None,
        error_message: str | None,
        fail_safe_triggered: bool,
    ) -> None:
        """Update the stored entry with execution outcome."""

        with self._session_factory() as session:
            log_entry = session.get(DataSelectionLog, entry_id)
            if log_entry is None:  # pragma: no cover - data corruption guard
                raise LookupError(f"DataSelectionLog {entry_id} not found")
            log_entry.complete(
                status,
                row_count,
                error_message=error_message,
                details=details,
                fail_safe_triggered=fail_safe_triggered,
            )
            session.add(log_entry)
