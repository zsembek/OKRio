"""PostgreSQL read-only connector implementation."""
from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .base import DataConnector, DataSelectionResult
from .exceptions import (
    DataConnectorConfigurationError,
    DataConnectorOperationalError,
    DataConnectorReadOnlyViolation,
)


class PostgresReadOnlyConnector(DataConnector):
    """Execute read-only SQL statements against PostgreSQL."""

    operation_name = "sql_select"

    def __init__(
        self,
        *,
        dsn: str | None = None,
        engine: Engine | None = None,
        journal=None,
    ) -> None:
        super().__init__(journal=journal)
        if engine is None and not dsn:
            raise DataConnectorConfigurationError("Either an Engine or DSN must be provided")
        self._engine: Engine = engine or create_engine(dsn, future=True, pool_pre_ping=True)  # type: ignore[arg-type]
        self._owns_engine = engine is None

    def close(self) -> None:
        if self._owns_engine:
            self._engine.dispose()

    def _ensure_read_only(self, sql: str) -> None:
        statement = sql.lstrip().lower()
        if not (statement.startswith("select") or statement.startswith("with")):
            raise DataConnectorReadOnlyViolation("Only SELECT/CTE statements are allowed")

    def execute_query(
        self,
        sql: str,
        *,
        parameters: dict[str, Any] | None = None,
        fail_safe_rows: list[dict[str, Any]] | None = None,
    ) -> DataSelectionResult:
        """Execute a read-only SQL query and journal the result."""

        self._ensure_read_only(sql)
        source = f"postgresql:{self._engine.url.render_as_string(hide_password=True)}"

        def _operation() -> DataSelectionResult:
            try:
                with self._engine.connect() as connection:
                    with connection.begin():
                        connection.execute(text("SET TRANSACTION READ ONLY"))
                        result = connection.execute(text(sql), parameters or {})
                        rows = [dict(row._mapping) for row in result]
            except SQLAlchemyError as exc:  # pragma: no cover - depends on DB
                raise DataConnectorOperationalError(str(exc)) from exc

            metadata = {
                "parameters": parameters or {},
                "statement": sql,
            }
            return DataSelectionResult(records=rows, metadata=metadata)

        fallback = (
            DataSelectionResult(
                records=fail_safe_rows or [],
                metadata={"statement": sql, "parameters": parameters or {}, "fail_safe": True},
            )
            if fail_safe_rows is not None
            else None
        )

        return self._execute(
            source=source,
            parameters=parameters,
            operation=_operation,
            fallback=fallback,
        )
