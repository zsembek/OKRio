# OKRio Backend

This directory hosts the FastAPI-based monolith that powers the OKRio enterprise OKR platform. The implementation follows the architectural principles outlined in the product requirements and is organised by business domains (Auth, Accounts, Org, OKR, Workflow, Analytics, Notifications, Integrations, Data Connectors).

## Highlights

- **FastAPI application factory** with CORS configuration and modular routers per domain.
- **Environment configuration** via Pydantic `BaseSettings`, including validation for Azure AD / Microsoft Graph credentials and core infrastructure endpoints (PostgreSQL, Redis, локальное файловое хранилище, RabbitMQ).
- **SQLAlchemy bootstrap** exposing a declarative base and session context manager for future models.
- **Domain models with RLS** implementing tenants, workspaces, users, objectives, key results и вложения, включая политики PostgreSQL Row-Level Security и Alembic-миграцию.
- **Local file storage service** обеспечивающий безопасную работу с вложениями на файловой системе сервера (без S3).
- **Celery application** preconfigured to use Redis or RabbitMQ as broker and Redis as result backend. Domain task modules are registered for asynchronous workloads such as notifications, analytics computations, and connector refreshes.
- **Data connectors** for Microsoft Graph Excel and PostgreSQL (read-only) with an auditable selection journal and configurable fail-safe fallbacks.
- **Access policy helpers** that codify the RBAC + ABAC rules described in the specification and can be extended to enforce row-level security and object roles.
- **Azure AD integration** with helpers for OAuth 2.0 Authorization Code + PKCE flows, refresh, and logout plus in-memory SCIM 2.0 provisioning endpoints for users and groups.
- **Workflow engine** capturing the multi-stage OKR approval lifecycle with RBAC/ABAC enforcement and object-role overrides.
- **Shared schemas** (e.g., health endpoints) to encourage consistency across routers.

## Local development

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

Celery worker example:

```bash
poetry run celery -A app.core.celery_app.celery_app worker -l info
poetry run celery -A app.core.celery_app.celery_app beat -l info
```

Environment variables are sourced from `.env`; see the repository-level `.env.example` for required keys. Для локального хранения файлов задайте `STORAGE_ROOT` — путь к директории, где будут сохраняться вложения и экспортированные данные.

### Database migrations

После внесения изменений в модели используйте Alembic:

```bash
poetry run alembic upgrade head  # применить миграции
poetry run alembic revision --autogenerate -m "описание"  # создать новую миграцию
```

## Next steps

- Implement domain models (SQLAlchemy) and Alembic migrations with row-level security policies.
- Flesh out API endpoints, workflow logic, and data connector adapters (Excel via Microsoft Graph, PostgreSQL read-only bindings).
- Integrate authentication with Azure AD (OAuth2 Authorization Code + PKCE) and build SCIM provisioning endpoints.
- Expand unit, integration, and contract tests alongside linters configured in CI/CD pipelines.
