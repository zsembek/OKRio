"""OKRio backend application package."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    # Import models so that metadata and RLS hooks are registered on startup.
    from . import models  # noqa: F401  pylint: disable=unused-import
except Exception as exc:  # pragma: no cover - defensive guard for partial envs
    logger.debug("Skipping models import during package init: %s", exc)
    models = None

__all__ = ["models"]
