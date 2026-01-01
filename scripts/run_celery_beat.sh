#!/bin/bash
# Скрипт для запуска Celery beat
# Используется для локальной разработки

# Активация виртуального окружения (если используется)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запуск Celery beat
celery -A infrastructure.celery_app beat --loglevel=info

