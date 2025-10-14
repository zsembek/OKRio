"""Exception hierarchy for data connector adapters."""
from __future__ import annotations


class DataConnectorError(Exception):
    """Base error raised by data connector adapters."""


class DataConnectorConfigurationError(DataConnectorError):
    """Raised when connector configuration is invalid or incomplete."""


class DataConnectorAuthenticationError(DataConnectorError):
    """Raised when authentication or token acquisition fails."""


class DataConnectorAuthorizationError(DataConnectorError):
    """Raised when the caller lacks permissions to access a resource."""


class DataConnectorOperationalError(DataConnectorError):
    """Raised when an unexpected runtime failure occurs."""


class DataConnectorReadOnlyViolation(DataConnectorError):
    """Raised when a read-only connector detects a mutating query."""
