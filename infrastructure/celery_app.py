"""
Celery Application Configuration

Настройка Celery для выполнения фоновых задач.
Используется для асинхронной обработки тяжелых операций.

Паттерны:
- Task Queue Pattern
- Producer-Consumer Pattern
- Background Job Pattern
"""

from celery import Celery
import structlog

from configs.config import load_configs

logger = structlog.get_logger(__name__)

config = load_configs()
redis_config = config.get("redis", {})

# URL для подключения к Redis
redis_url = (
    f"redis://{redis_config.get('host', 'localhost')}:"
    f"{redis_config.get('port', 6379)}"
)

# Создание Celery приложения
celery_app = Celery(
    "textguard_ai",
    broker=redis_url,
    backend=redis_url,
    include=["infrastructure.tasks"],
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут (soft limit)
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

logger.info("Celery app configured", broker=redis_url)

