# OKRio

OKRio — корпоративная OKR-платформа уровня enterprise. Репозиторий содержит исходный код, документацию и инфраструктурные шаблоны для реализации системы на стеке Python FastAPI + React.

## Структура монорепозитория

- `backend/` — FastAPI-монолит с модульной организацией доменов (Auth, Accounts, Org, OKR, Workflow, Analytics, Notifications, Integrations, Data Connectors), конфигурацией окружения, базовыми роутерами и Celery.
- `frontend/` — SPA на React + TypeScript (Vite) с Redux Toolkit и Chakra UI. Включает стартовый дашборд рабочего пространства с локализацией RU/EN.
- `docs/architecture.md` — архитектурный blueprint, агрегирующий требования по функциональности, интеграциям, безопасности и DevOps.
- `.env.example` — список обязательных переменных окружения (Azure OAuth, PostgreSQL, Redis, S3 и пр.).
- `docker-compose.yml.example` и `Dockerfile.example` — шаблоны контейнеризации и локального запуска полного стека.

## Быстрый старт локально

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Celery worker/beat:

```bash
celery -A app.core.celery_app.celery_app worker -l info
celery -A app.core.celery_app.celery_app beat -l info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Приложение будет доступно на `http://localhost:5173` и подключается к backend через REST/WebSocket (после реализации API-клиента).

### Docker Compose (пример)

Скопируйте `.env.example` в `.env`, `docker-compose.yml.example` в `docker-compose.yml`, `Dockerfile.example` в `Dockerfile` и запустите:

```bash
docker compose up --build
```

Шаблон поднимает PostgreSQL, Redis, backend (uvicorn) и frontend (Nginx со статическим билдом) в единой сети.

## Дальнейшие шаги

1. Реализовать доменные модели (SQLAlchemy) с политиками RLS и миграциями Alembic.
2. Подключить Azure AD OAuth 2.0 / SCIM, построить RBAC+ABAC+object roles, реализовать workflow согласований.
3. Реализовать коннекторы данных (Microsoft Graph Excel, PostgreSQL read-only) с журналом выборок и fail-safe.
4. Расширить фронтенд страницами Alignment, Workspace OKR, Settings, Notifications и аналитическими дашбордами.
5. Настроить CI/CD (GitHub Actions → ArgoCD), IaC (Terraform), observability (Prometheus/Grafana, OpenTelemetry), безопасность (rate limiting, audit trail, шифрование).
