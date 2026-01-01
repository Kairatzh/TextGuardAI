"""
Domain Layer

Этот слой содержит бизнес-логику и доменные сущности.
Он не зависит от других слоев и определяет интерфейсы для работы с данными.

Архитектурные принципы:
- Domain-Driven Design (DDD)
- Clean Architecture
- Dependency Inversion Principle
"""

from domain.entities import PredictionResult, TextClassification
from domain.repositories import IPredictionRepository
from domain.value_objects import ToxicityLevel

__all__ = [
    "PredictionResult",
    "TextClassification",
    "IPredictionRepository",
    "ToxicityLevel",
]

