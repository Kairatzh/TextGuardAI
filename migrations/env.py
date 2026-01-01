"""
Alembic Environment Configuration

Настройка Alembic для работы с async SQLAlchemy и PostgreSQL.
Использует async engine для миграций.

Паттерны:
- Migration Pattern
- Database Schema Versioning
"""

"""
Alembic Environment Configuration

Настройка Alembic для работы с SQLAlchemy и PostgreSQL.
Использует sync SQLAlchemy для миграций (Alembic требует sync).

Паттерны:
- Migration Pattern
- Database Schema Versioning
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool

from alembic import context

# Импорт Base и всех моделей для autogenerate
from infrastructure.database import Base
from infrastructure.models import PredictionORM  # noqa

# this is the Alembic Config object
config = context.config

# Интерпретация конфигурационного файла для Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для autogenerate
target_metadata = Base.metadata


def get_url() -> str:
    """
    Получить URL БД из переменных окружения или конфига.
    
    Returns:
        str: Database URL для подключения
    """
    from configs.config import load_configs
    
    cfg = load_configs()
    db_config = cfg.get("database", {})
    
    user = db_config.get("user", "nlp_user")
    password = db_config.get("password", "nlp_password")
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 5432)
    db_name = db_config.get("db", "nlp_db")
    
    # Alembic работает с sync SQLAlchemy, используем psycopg2
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def run_migrations_offline() -> None:
    """
    Запуск миграций в 'offline' режиме.
    
    Это настраивает контекст только с URL и не использует Engine,
    хотя Engine здесь тоже приемлем. Пропуская создание Engine,
    мы даже не нуждаемся в DBAPI.
    
    Вызовы context.execute() здесь эмитируют заданную строку в stdout.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Запуск миграций в 'online' режиме.
    
    В этом сценарии нам нужно создать Engine и связать его с контекстом миграции.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

