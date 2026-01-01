# Dockerfile для TextGuard AI
# Многоступенчатая сборка с Poetry
# Используем Python 3.11 slim образ для меньшего размера
FROM python:3.11-slim as builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
ENV POETRY_VERSION=1.6.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* ./

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only=main

# Production образ
FROM python:3.11-slim

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Создание non-root пользователя
RUN useradd -m -u 1000 appuser

# Копирование установленных пакетов из builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Рабочая директория
WORKDIR /app

# Копирование кода приложения
COPY --chown=appuser:appuser . .

# Переключение на non-root пользователя
USER appuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Порт приложения
EXPOSE 8000

# Команда запуска (будет переопределена в docker-compose при необходимости)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

