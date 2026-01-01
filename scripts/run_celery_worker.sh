#!/bin/bash
# Скрипт для запуска Celery worker
# Используется для локальной разработки

# Активация виртуального окружения (если используется)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запуск Celery worker
celery -A infrastructure.celery_app worker --loglevel=info

