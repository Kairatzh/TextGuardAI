#!/bin/bash
# Скрипт для инициализации БД
# Применяет миграции Alembic

# Активация виртуального окружения (если используется)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Создание начальной миграции (если еще не создана)
# alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head

echo "Database initialized successfully"

