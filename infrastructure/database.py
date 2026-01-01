"""
Database Configuration and Session Management

Конфигурация SQLAlchemy и управление сессиями БД.
Использует async SQLAlchemy для работы с PostgreSQL.

Паттерны:
- Connection Pool Pattern
- Session Factory Pattern
- Dependency Injection для сессий
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
import structlog

from configs.config import load_configs

logger = structlog.get_logger(__name__)

# Base класс для всех ORM моделей
Base = declarative_base()

# Глобальный объект для управления подключениями
_engine = None
_session_factory = None


class Database:
    """
    Класс для управления подключением к БД.
    
    Использует Singleton Pattern для единого подключения.
    Управляет lifecycle подключения к PostgreSQL.
    """
    
    def __init__(self):
        """Инициализация Database с настройками из конфига."""
        self._engine = None
        self._session_factory = None
    
    async def connect(self):
        """
        Установить подключение к БД.
        
        Создает async engine и session factory для работы с PostgreSQL.
        """
        config = load_configs()
        db_config = config.get("database", {})
        
        # Формирование DSN для async SQLAlchemy (использует asyncpg драйвер)
        user = db_config.get("user", "nlp_user")
        password = db_config.get("password", "nlp_password")
        host = db_config.get("host", "localhost")
        port = db_config.get("port", 5432)
        db_name = db_config.get("db", "nlp_db")
        
        # Async SQLAlchemy использует postgresql+asyncpg://
        database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
        
        logger.info("Connecting to database", host=host, port=port, db=db_name)
        
        self._engine = create_async_engine(
            database_url,
            echo=False,  # Включить для отладки SQL запросов
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Проверка соединения перед использованием
        )
        
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        logger.info("Database connection established")
    
    async def disconnect(self):
        """
        Закрыть подключение к БД.
        
        Корректно закрывает все соединения из пула.
        """
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connection closed")
    
    def get_session_factory(self) -> async_sessionmaker:
        """
        Получить фабрику сессий.
        
        Returns:
            async_sessionmaker: Фабрика для создания async сессий
        """
        if not self._session_factory:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._session_factory
    
    async def create_tables(self):
        """
        Создать все таблицы в БД.
        
        Используется для инициализации БД или тестирования.
        Для production рекомендуется использовать Alembic migrations.
        """
        if not self._engine:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created")


# Глобальный экземпляр Database
_db = Database()


def get_database() -> Database:
    """
    Получить глобальный экземпляр Database.
    
    Используется для dependency injection.
    
    Returns:
        Database: Глобальный экземпляр Database
    """
    return _db


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения async сессии БД.
    
    Используется в FastAPI dependency injection.
    Автоматически закрывает сессию после использования.
    
    Yields:
        AsyncSession: Async сессия SQLAlchemy
        
    Example:
        ```python
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            # Использование сессии
            pass
        ```
    """
    session_factory = _db.get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

