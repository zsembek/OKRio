FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/pyproject.toml ./
COPY backend/poetry.lock ./

RUN pip install --upgrade pip \
    && pip install "poetry>=1.7" \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-ansi --no-interaction

COPY backend/app ./app

ENV PYTHONPATH=/app

EXPOSE 8070

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8070"]
