"""OKRio backend application package."""

# Import models so that metadata and RLS hooks are registered on startup.
from . import models  # noqa: F401  pylint: disable=unused-import

__all__ = ["models"]
