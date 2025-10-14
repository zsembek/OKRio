# OKRio

OKRio — корпоративная OKR-платформа уровня enterprise. Репозиторий содержит исходный код и документацию по реализации системы на стеке Python FastAPI + React.

## Структура репозитория

- `backend/` — заготовка монолита FastAPI с модульной организацией доменов (Auth, Accounts, Org, OKR, Workflow, Analytics, Notifications, Integrations, Data Connectors), конфигурацией окружения, базовыми роутерами и Celery.
- `frontend/` — план реализации SPA на React + TypeScript с Feature-Sliced Design и UX-требованиями.
- `docs/architecture.md` — архитектурный blueprint, агрегирующий требования по функциональности, интеграциям, безопасности и DevOps.
- `.env.example` — список обязательных переменных окружения (Azure OAuth, PostgreSQL, Redis и локальное файловое хранилище).

## Запуск backend-сервиса локально

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

Celery worker/beat:

```bash
poetry run celery -A app.core.celery_app.celery_app worker -l info
poetry run celery -A app.core.celery_app.celery_app beat -l info
```

## Дальнейшие шаги

1. ✅ Реализовать доменные модели (SQLAlchemy) с политиками RLS и миграциями Alembic.
2. ⬜ Подключить Azure AD OAuth 2.0 / SCIM, построить RBAC+ABAC+object roles, реализовать workflow согласований.
3. ⬜ Реализовать коннекторы данных (Microsoft Graph Excel, PostgreSQL read-only) с журналом выборок и fail-safe.
4. ⬜ Собрать фронтенд (Vite + React) с Feature-Sliced архитектурой, i18n, drag-and-drop, аналитическими дашбордами и PWA.
5. ⬜ Настроить CI/CD (GitHub Actions → ArgoCD), IaC (Terraform), observability (Prometheus/Grafana, OpenTelemetry), безопасность (rate limiting, audit trail, шифрование).
