# OKRio

OKRio — корпоративная OKR-платформа уровня enterprise. Репозиторий включает рабочий backend на FastAPI и фронтенд на React + TypeScript, а также архитектурную документацию, описывающую требования платформы.

## Структура репозитория

- `backend/` — монолит FastAPI с модульной организацией доменов (Auth, Accounts, Org, OKR, Workflow, Analytics, Notifications, Integrations, Data Connectors), конфигурацией окружения на Pydantic `BaseSettings`, Celery и сервисами уровня enterprise (RBAC/ABAC движок, workflow-оркестратор, локальное файловое хранилище, коннекторы данных, SCIM-хендлеры).
- `frontend/` — SPA на React 18 + TypeScript, собранная по принципам Feature-Sliced Design и оснащенная i18n, drag-and-drop выравниванием целей, аналитическими дашбордами и PWA-конфигурацией.
- `docs/architecture.md` — архитектурный blueprint, агрегирующий функциональные, интеграционные, безопасностные и DevOps-требования.
- `.env.example` — перечень обязательных переменных окружения (Azure OAuth, PostgreSQL, Redis, RabbitMQ и локальное файловое хранилище).

## Реализованный функционал

### Backend

- Доменные модели (тенанты, рабочие пространства, пользователи, OKR) с политиками PostgreSQL RLS и миграциями Alembic.
- Конфигурация окружения с валидацией Azure AD OAuth и Microsoft Graph, а также фабрика Celery, подключающая рабочие очереди (Redis/RabbitMQ).
- RBAC + ABAC + object roles через `AccessPolicyEngine`, используемый в auth-роутерах и workflow-сервисе.
- Интеграция с Azure AD: OAuth 2.0 Authorization Code + PKCE, refresh/logout хелперы и in-memory SCIM 2.0 каталог.
- Workflow-движок, управляемый политиками доступа, и коннекторы данных (Microsoft Graph Excel, PostgreSQL read-only) с журналом выборок и fail-safe режимом.

### Frontend

- Feature-Sliced структура директорий (app, entities, features, pages, processes, shared, widgets).
- Поддержка i18n (EN/RU), Redux Toolkit для состояния, Chakra UI для темизации и drag-and-drop выравнивание OKR через `@dnd-kit`.
- Аналитические дашборды на Recharts и сервис-воркер через `vite-plugin-pwa`.

## Быстрый старт через Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Команда поднимет фронтенд, API, Celery worker/beat, PostgreSQL, Redis и RabbitMQ. После успешного запуска SPA доступно на http://localhost:5173, а backend — на http://localhost:8070. Если требуется запустить фронтенд вручную, перейдите в каталог `frontend/` и выполните `npm run dev` или соберите продакшн-версию через `npm run build`.

> ℹ️ Dockerfile backend-сервиса автоматически выполняет `git clone` репозитория, поэтому при сборке образа всегда используется свежая версия кода из ветки `main`. Локальные файлы нужны только для `docker-compose.yml` и `.env`.

## Локальный запуск компонентов

### Backend

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

Тесты:

```bash
poetry run pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Сборка и предпросмотр:

```bash
npm run build
npm run preview
```

## Дальнейшие шаги

1. ✅ Реализовать доменные модели (SQLAlchemy) с политиками RLS и миграциями Alembic.
2. ✅ Подключить Azure AD OAuth 2.0 / SCIM, построить RBAC+ABAC+object roles и workflow согласований.
3. ✅ Реализовать коннекторы данных (Microsoft Graph Excel, PostgreSQL read-only) с журналом выборок и fail-safe.
4. ✅ Собрать фронтенд (Vite + React) с Feature-Sliced архитектурой, i18n, drag-and-drop, аналитическими дашбордами и PWA.
5. ⬜ Настроить CI/CD (GitHub Actions → ArgoCD), IaC (Terraform), observability (Prometheus/Grafana, OpenTelemetry), безопасность (rate limiting, audit trail, шифрование).

