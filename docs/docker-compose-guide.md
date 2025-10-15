# Запуск OKRio в Docker Compose

Эта инструкция поможет поднять полный стек (frontend, backend, Celery, PostgreSQL, Redis и RabbitMQ) локально при помощи Docker Compose.

## 1. Подготовьте окружение

1. Установите [Docker Engine](https://docs.docker.com/engine/install/) и убедитесь, что демон Docker запущен.
2. Убедитесь, что доступен Docker Compose v2 (плагин `docker compose`). Проверить версию можно командой:
   ```bash
   docker compose version
   ```

## 2. Клонируйте репозиторий

```bash
git clone https://github.com/<your-org>/OKRio.git
cd OKRio
```

Если вы уже находитесь в каталоге проекта, убедитесь, что находитесь в корне (`Dockerfile`, `docker-compose.yml`).

## 3. Подготовьте файл окружения

1. Скопируйте шаблон `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```
2. Откройте `.env` в редакторе и задайте необходимые значения:
   - `ADMIN_EMAIL`, `FRONTEND_URL`, `BACKEND_URL` — адреса вашего окружения.
   - `POSTGRES_URL`, `REDIS_URL`, `RABBITMQ_URL` — строки подключения, соответствующие сервисам из docker-compose.
   - `JWT_SECRET` — задайте случайную строку.
   - `AZURE_*` и `MS_GRAPH_*` — заполните, если интеграция с Azure AD нужна. Для локального теста можно оставить значения-заглушки.
   - `STORAGE_ROOT` — путь внутри контейнера для локальных файлов (значение по умолчанию уже подходит).

> ⚠️ Значения `POSTGRES_URL`, `REDIS_URL` и `RABBITMQ_URL` в шаблоне уже синхронизированы с сервисами из `docker-compose.yml`, поэтому менять их не нужно, если вы запускаете всё в локальном Docker.

## 4. Запустите контейнеры

В корне репозитория выполните:

```bash
docker compose up --build
```

- Флаг `--build` гарантирует пересборку backend-образа при первом запуске или после изменения кода.
- Docker Compose автоматически поднимет сервисы `frontend`, `backend`, `celery_worker`, `celery_beat`, `postgres`, `redis` и `rabbitmq`. База данных `postgres` снабжена healthcheck’ом, поэтому backend стартует только после готовности БД.
- Для остановки сервисов нажмите `Ctrl+C`. Чтобы удалить контейнеры, выполните `docker compose down`, а для очистки данных PostgreSQL добавьте `-v`.

## 5. Проверка доступности

После успешного запуска сервисы доступны по следующим адресам:

- Frontend (Vite dev server): http://localhost:5173
- Backend FastAPI: http://localhost:8070
- Redis: localhost:6379
- RabbitMQ (AMQP): localhost:5672
- RabbitMQ Management UI: http://localhost:15672 (логин/пароль по умолчанию `guest`/`guest`)

## 6. Дополнительные команды

- Просмотр логов всех сервисов:
  ```bash
  docker compose logs -f
  ```
- Перезапуск только backend без пересборки:
  ```bash
  docker compose restart backend
  ```
- Запуск в фоне (detached mode):
  ```bash
  docker compose up -d
  ```

## 7. Обновление зависимостей backend

Если вы изменили Python-зависимости в `backend/pyproject.toml`, пересоберите образ:

```bash
docker compose build backend celery_worker celery_beat
```

После сборки перезапустите нужные сервисы.

Теперь весь стек OKRio должен быть доступен локально через Docker Compose.
