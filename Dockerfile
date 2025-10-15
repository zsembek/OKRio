FROM alpine/git AS fetcher

WORKDIR /src

RUN git clone --branch main --single-branch --depth 1 \
    https://github.com/zsembek/OKRio.git .

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=fetcher /src/backend/requirements.locked.txt ./requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-compile --no-cache-dir -r requirements.txt

COPY --from=fetcher /src/backend/app ./app

ENV PYTHONPATH=/app

EXPOSE 8070

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8070"]
