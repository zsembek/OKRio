"""Shared primitives for implementing data connector adapters."""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Callable

from .exceptions import DataConnectorError, DataConnectorOperationalError
from .journal import DataSelectionJournal


@dataclass
class DataSelectionResult:
    """Normalized payload returned by connector queries."""

    records: list[Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def row_count(self) -> int:
        return len(self.records)


class DataConnector(ABC):
    """Base helper offering journal-aware execution semantics."""

    operation_name: str = "query"

    def __init__(self, *, journal: DataSelectionJournal | None = None) -> None:
        self._journal = journal or DataSelectionJournal()

    @property
    def connector_type(self) -> str:
        return self.__class__.__name__

    def _execute(
        self,
        *,
        source: str,
        parameters: dict[str, Any] | None,
        operation: Callable[[], DataSelectionResult],
        fallback: DataSelectionResult | None = None,
    ) -> DataSelectionResult:
        """Run an operation and store audit logs with fail-safe support."""

        with self._journal.record(
            connector_type=self.connector_type,
            operation=self.operation_name,
            source=source,
            parameters=parameters,
        ) as context:
            try:
                result = operation()
            except DataConnectorError as exc:
                context.fail(exc)
                raise
            except Exception as exc:
                if fallback is not None:
                    context.succeed(
                        row_count=fallback.row_count,
                        details=fallback.metadata,
                        fail_safe=True,
                        error=exc,
                    )
                    return fallback
                context.fail(exc)
                raise DataConnectorOperationalError(str(exc)) from exc
            else:
                context.succeed(row_count=result.row_count, details=result.metadata)
                return result
