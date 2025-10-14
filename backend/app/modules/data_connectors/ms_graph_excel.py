"""Microsoft Graph Excel connector implementation."""
from __future__ import annotations

from typing import Any, Callable

import httpx

from .base import DataConnector, DataSelectionResult
from .exceptions import (
    DataConnectorAuthenticationError,
    DataConnectorAuthorizationError,
    DataConnectorConfigurationError,
)


class MicrosoftGraphExcelConnector(DataConnector):
    """Query Excel workbooks exposed through Microsoft Graph."""

    operation_name = "excel_table_rows"

    def __init__(
        self,
        *,
        token_provider: Callable[[], str],
        base_url: str,
        journal=None,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(journal=journal)
        if not base_url:
            raise DataConnectorConfigurationError("Microsoft Graph base URL must be provided")
        self._token_provider = token_provider
        self._base_url = base_url.rstrip("/")
        self._client = http_client or httpx.Client(timeout=30.0)
        self._owns_client = http_client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def fetch_table_rows(
        self,
        *,
        drive_item_id: str,
        worksheet: str,
        table: str,
        select: str | None = None,
        filter_expression: str | None = None,
        top: int | None = None,
        fail_safe_rows: list[list[Any]] | None = None,
    ) -> DataSelectionResult:
        """Retrieve rows from an Excel table via Microsoft Graph."""

        if not drive_item_id:
            raise DataConnectorConfigurationError("drive_item_id is required")
        if not worksheet:
            raise DataConnectorConfigurationError("worksheet is required")
        if not table:
            raise DataConnectorConfigurationError("table is required")

        def _operation() -> DataSelectionResult:
            token = self._token_provider()
            if not token:
                raise DataConnectorAuthenticationError("Token provider returned an empty token")

            url = (
                f"{self._base_url}/me/drive/items/{drive_item_id}/workbook/worksheets/{worksheet}/"
                f"tables/{table}/rows"
            )
            params: dict[str, Any] = {}
            if select:
                params["$select"] = select
            if filter_expression:
                params["$filter"] = filter_expression
            if top is not None:
                params["$top"] = top

            response = self._client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params=params or None,
            )

            if response.status_code == 401:
                raise DataConnectorAuthenticationError("Microsoft Graph rejected the access token")
            if response.status_code == 403:
                raise DataConnectorAuthorizationError("Insufficient permissions to access workbook data")
            response.raise_for_status()

            payload = response.json()
            rows = payload.get("value", []) if isinstance(payload, dict) else []
            extracted_rows: list[list[Any]] = []
            for row in rows:
                values = row.get("values") if isinstance(row, dict) else None
                if isinstance(values, list):
                    extracted_rows.extend([v for v in values if isinstance(v, list)])
            metadata = {
                "drive_item_id": drive_item_id,
                "worksheet": worksheet,
                "table": table,
                "raw_row_count": len(rows),
            }
            return DataSelectionResult(records=extracted_rows, metadata=metadata)

        fallback = (
            DataSelectionResult(
                records=fail_safe_rows or [],
                metadata={
                    "drive_item_id": drive_item_id,
                    "worksheet": worksheet,
                    "table": table,
                    "fail_safe": True,
                },
            )
            if fail_safe_rows is not None
            else None
        )

        return self._execute(
            source=f"graph:excel:{drive_item_id}:{worksheet}:{table}",
            parameters={
                "select": select,
                "filter": filter_expression,
                "top": top,
            },
            operation=_operation,
            fallback=fallback,
        )
