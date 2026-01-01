"""
Infrastructure Layer

Этот слой содержит реализации интерфейсов из domain и application слоев.
Включает работу с БД, внешними API, файловой системой и т.д.

Паттерны:
- Repository Pattern (реализация)
- Adapter Pattern
- Infrastructure Services
"""

from infrastructure.database import get_session, Database
from infrastructure.repositories import PredictionRepository
from infrastructure.models import PredictionORM

__all__ = [
    "get_session",
    "Database",
    "PredictionRepository",
    "PredictionORM",
]

