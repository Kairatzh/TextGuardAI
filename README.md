# TextGuard AI

Продвинутый ML/NLP сервис для классификации токсичности текста с enterprise архитектурой.

## 🏗️ Архитектура

Проект построен на принципах Clean Architecture и Domain-Driven Design (DDD) с четким разделением на слои:

```
┌─────────────────────────────────────────┐
│      Presentation Layer (API)           │  ← FastAPI endpoints
├─────────────────────────────────────────┤
│      Application Layer                  │  ← Use Cases, Services
├─────────────────────────────────────────┤
│      Domain Layer                       │  ← Entities, Value Objects, Interfaces
├─────────────────────────────────────────┤
│      Infrastructure Layer               │  ← DB, HTTP Clients, Celery
└─────────────────────────────────────────┘
```

### Слои архитектуры

1. **Domain Layer** (`domain/`)
   - Доменные сущности (Entities)
   - Value Objects
   - Интерфейсы репозиториев
   - Бизнес-логика и правила валидации

2. **Application Layer** (`application/`)
   - Use Cases (сценарии использования)
   - Application Services
   - Оркестрация domain и infrastructure слоев

3. **Infrastructure Layer** (`infrastructure/`)
   - Реализация репозиториев (PostgreSQL)
   - HTTP клиенты (httpx)
   - Celery tasks
   - Dependency Injection контейнер

4. **Presentation Layer** (`app/api/`)
   - FastAPI endpoints
   - Pydantic схемы (DTOs)
   - HTTP обработка запросов

## 🎯 Используемые паттерны и технологии

### Архитектурные паттерны
- ✅ **Clean Architecture** - разделение на слои
- ✅ **Domain-Driven Design (DDD)** - доменные сущности и value objects
- ✅ **Repository Pattern** - абстракция доступа к данным
- ✅ **Use Case Pattern** - инкапсуляция бизнес-логики
- ✅ **Dependency Injection** - управление зависимостями
- ✅ **Service Layer Pattern** - сервисы приложения
- ✅ **CQRS** (частично) - разделение команд и запросов

### Технологии
- ✅ **PostgreSQL** + **SQLAlchemy 2.0** (async) + **Alembic** - БД и миграции
- ✅ **Celery** + **Redis** - фоновые задачи
- ✅ **Pydantic** + **dataclass** - валидация и схемы данных
- ✅ **httpx** - HTTP клиенты для внешних API
- ✅ **dependency-injector** - dependency injection контейнер
- ✅ **Poetry** - управление зависимостями
- ✅ **Docker** + **Docker Compose** - контейнеризация

## 📦 Установка и настройка

### Требования
- Python 3.10+
- Poetry
- Docker и Docker Compose (для запуска через Docker)
- PostgreSQL (для локальной разработки)
- Redis (для Celery)

### Установка через Poetry

```bash
# Клонирование репозитория
git clone <repository-url>
cd TextGuardAI

# Установка зависимостей
poetry install

# Активация виртуального окружения
poetry shell

# Копирование и настройка переменных окружения
cp env.example .env
# Отредактируйте .env файл с вашими настройками

# Применение миграций БД
alembic upgrade head

# Запуск приложения
uvicorn app.main:app --reload
```

### Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f api

# Остановка
docker-compose down

# Остановка с удалением volumes
docker-compose down -v
```

Docker Compose запускает:
- **api** - FastAPI приложение (порт 8000)
- **db** - PostgreSQL (порт 5432)
- **redis** - Redis для Celery (порт 6379)
- **celery_worker** - Celery worker для фоновых задач
- **celery_beat** - Celery beat для периодических задач

## 🔧 Конфигурация

Конфигурация хранится в:
- `configs/configs.yml` - основная конфигурация (YAML)
- `.env` - переменные окружения

Переменные окружения (см. `env.example`):
- `POSTGRES_*` - настройки БД
- `REDIS_*` - настройки Redis
- `MODEL_PATH`, `VECTORIZER_PATH` - пути к модели
- `APP_ENV`, `APP_HOST`, `APP_PORT` - настройки приложения

## 📚 API Документация

После запуска приложения доступна интерактивная документация:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Основные endpoints

- `POST /api/v1/predict` - Предсказание токсичности текста
- `GET /api/v1/predictions` - История предсказаний (с пагинацией)
- `GET /api/v1/predictions/{id}` - Получить предсказание по ID
- `GET /health` - Health check

## 🗄️ Работа с БД

### Миграции Alembic

```bash
# Создание новой миграции
alembic revision --autogenerate -m "Description"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1

# Просмотр текущей версии
alembic current
```

### Структура БД

Таблица `predictions`:
- `id` (UUID) - уникальный идентификатор
- `text` (TEXT) - исходный текст
- `toxicity_score` (FLOAT) - оценка токсичности (0.0 - 1.0)
- `toxicity_level` (VARCHAR) - уровень токсичности
- `model_version` (VARCHAR) - версия модели
- `confidence` (FLOAT) - уверенность модели
- `processing_time_ms` (FLOAT) - время обработки
- `metadata` (JSONB) - дополнительные метаданные
- `created_at` (TIMESTAMP) - время создания

## 🔄 Фоновые задачи (Celery)

### Запуск Celery Worker

```bash
# Локально
celery -A infrastructure.celery_app worker --loglevel=info

# Или через скрипт
./scripts/run_celery_worker.sh
```

### Запуск Celery Beat (для периодических задач)

```bash
celery -A infrastructure.celery_app beat --loglevel=info
```

### Доступные задачи

- `predict_text_async` - асинхронное предсказание токсичности
- `batch_predict` - батч обработка текстов
- `cleanup_old_predictions` - очистка старых предсказаний

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С coverage
pytest --cov=app --cov=domain --cov=application --cov=infrastructure

# Только unit тесты
pytest tests/unit

# Только integration тесты
pytest tests/integration
```

## 📖 Структура проекта

```
TextGuardAI/
├── app/                    # Presentation Layer
│   ├── api/
│   │   ├── routes.py      # API endpoints
│   │   └── schemas.py     # Pydantic схемы (DTOs)
│   └── main.py            # FastAPI приложение
├── domain/                 # Domain Layer
│   ├── entities.py        # Доменные сущности
│   ├── value_objects.py   # Value Objects
│   └── repositories.py    # Интерфейсы репозиториев
├── application/            # Application Layer
│   ├── use_cases.py       # Use Cases
│   ├── services.py        # Application Services
│   └── interfaces.py      # Интерфейсы сервисов
├── infrastructure/         # Infrastructure Layer
│   ├── database.py        # SQLAlchemy настройка
│   ├── models.py          # ORM модели
│   ├── repositories.py    # Реализация репозиториев
│   ├── dependency_injection.py  # DI контейнер
│   ├── http_clients.py    # HTTP клиенты
│   ├── celery_app.py      # Celery конфигурация
│   └── tasks.py           # Celery задачи
├── configs/                # Конфигурация
│   ├── config.py          # Загрузка конфигурации
│   └── configs.yml        # YAML конфигурация
├── migrations/             # Alembic миграции
├── model/                  # ML модель
│   ├── train.py           # Обучение модели
│   └── inference.py       # Инференс (legacy)
├── scripts/                # Утилиты
├── docker-compose.yml      # Docker Compose конфигурация
├── Dockerfile              # Docker образ
├── pyproject.toml          # Poetry зависимости
├── alembic.ini             # Alembic конфигурация
└── README.md               # Документация
```

## 🎓 Изучаемые концепции

Этот проект демонстрирует продвинутые концепции для ML/LLM инженеров:

1. **Архитектура**
   - Clean Architecture
   - Domain-Driven Design
   - Слоистая архитектура

2. **Паттерны проектирования**
   - Repository Pattern
   - Use Case Pattern
   - Dependency Injection
   - Factory Pattern
   - Strategy Pattern

3. **Технологии**
   - Async/await в Python
   - SQLAlchemy 2.0 (async)
   - Alembic миграции
   - Celery для фоновых задач
   - Pydantic для валидации
   - Poetry для управления зависимостями

4. **Best Practices**
   - Type hints
   - Docstrings
   - Error handling
   - Logging (structlog)
   - Environment variables
   - Docker multi-stage builds

## 📝 Лицензия

[Указать лицензию]

## 🤝 Вклад

[Инструкции по вкладу]
