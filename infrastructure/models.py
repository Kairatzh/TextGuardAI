"""
SQLAlchemy ORM Models

ORM модели для представления данных в PostgreSQL.
Используются для маппинга между доменными сущностями и таблицами БД.

Паттерны:
- Data Mapper Pattern (SQLAlchemy)
- ORM Pattern
- Active Record (частично через SQLAlchemy)
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Float, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from infrastructure.database import Base
from domain.value_objects import ToxicityLevel


class PredictionORM(Base):
    """
    ORM модель для предсказаний.
    
    Представляет таблицу predictions в PostgreSQL.
    Соответствует доменной сущности PredictionResult.
    
    Attributes:
        id: Уникальный идентификатор (UUID)
        text: Исходный текст
        toxicity_score: Оценка токсичности (0.0 - 1.0)
        toxicity_level: Уровень токсичности (enum как строка)
        model_version: Версия модели
        confidence: Уверенность модели (0.0 - 1.0)
        processing_time_ms: Время обработки в миллисекундах
        metadata: Дополнительные метаданные (JSON)
        created_at: Время создания записи
    """
    
    __tablename__ = "predictions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    text = Column(Text, nullable=False, index=True)
    toxicity_score = Column(Float, nullable=False)
    toxicity_level = Column(String(50), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    processing_time_ms = Column(Float, nullable=False)
    metadata = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        """Строковое представление для отладки."""
        return (
            f"<PredictionORM(id={self.id}, "
            f"toxicity_score={self.toxicity_score}, "
            f"toxicity_level={self.toxicity_level})>"
        )

