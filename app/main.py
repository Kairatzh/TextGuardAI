"""
FastAPI Application Entry Point

Главный файл приложения FastAPI.
Инициализирует все компоненты и настраивает middleware.

Паттерны:
- Application Factory Pattern
- Dependency Injection Setup
- Lifecycle Management
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from infrastructure.database import get_database
from infrastructure.dependency_injection import Container
import structlog.stdlib

# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Глобальный контейнер для dependency injection
container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle management для приложения.
    
    Управляет инициализацией и очисткой ресурсов:
    - Подключение к БД
    - Инициализация контейнера зависимостей
    
    Args:
        app: FastAPI приложение
        
    Yields:
        None
    """
    # Startup
    logger.info("Starting application")
    
    # Подключение к БД
    database = get_database()
    await database.connect()
    
    # Инициализация контейнера зависимостей
    container.database.override(database)
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await database.disconnect()
    logger.info("Application stopped")


# Создание FastAPI приложения
app = FastAPI(
    title="TextGuard AI API",
    description="Advanced ML/NLP service for text toxicity classification",
    version="1.0.0",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(router)


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Используется для проверки работоспособности сервиса
    (например, в Kubernetes liveness/readiness probes).
    
    Returns:
        dict: Статус сервиса
    """
    return {
        "status": "healthy",
        "service": "textguard-ai",
        "version": "1.0.0",
    }


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: Информация о сервисе
    """
    return {
        "name": "TextGuard AI",
        "description": "Advanced ML/NLP service for text toxicity classification",
        "version": "1.0.0",
        "docs": "/docs",
    }


# Установка контейнера в модуль routes для доступа к зависимостям
import app.api.routes as routes_module
routes_module.container = container

if __name__ == "__main__":
    import uvicorn
    from configs.config import load_configs
    
    config = load_configs()
    app_config = config.get("app", {})
    
    uvicorn.run(
        "app.main:app",
        host=app_config.get("host", "0.0.0.0"),
        port=app_config.get("port", 8000),
        reload=app_config.get("env") == "development",
    )
