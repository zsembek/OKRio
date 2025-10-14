"""FastAPI application factory for OKRio."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import Settings, get_settings
from .modules.analytics.router import router as analytics_router
from .modules.auth.router import router as auth_router
from .modules.integrations.router import router as integrations_router
from .modules.notifications.router import router as notifications_router
from .modules.okr.router import router as okr_router
from .modules.org.router import router as org_router
from .modules.workflow.router import router as workflow_router
from .modules.data_connectors.router import router as data_connectors_router
from .modules.accounts.router import router as accounts_router


def create_application(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(title=settings.project_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_origins] or [str(settings.frontend_url)],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(accounts_router, prefix="/api/v1/accounts", tags=["accounts"])
    app.include_router(org_router, prefix="/api/v1/org", tags=["org"])
    app.include_router(okr_router, prefix="/api/v1/okr", tags=["okr"])
    app.include_router(workflow_router, prefix="/api/v1/workflows", tags=["workflow"])
    app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
    app.include_router(integrations_router, prefix="/api/v1/integrations", tags=["integrations"])
    app.include_router(
        data_connectors_router, prefix="/api/v1/data-connectors", tags=["data-connectors"]
    )

    return app


app = create_application()
