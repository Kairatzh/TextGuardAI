"""
Доменные сущности (Entities)

Сущности представляют объекты предметной области с уникальной идентичностью.
Они содержат бизнес-логику и правила валидации.

Используемые паттерны:
- Entity Pattern (DDD)
- Value Objects
- Domain Events (можно расширить)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from domain.value_objects import ToxicityLevel


@dataclass(frozen=True)
class TextClassification:
    """
    Доменная сущность для классификации текста.
    
    Immutable объект (frozen dataclass) гарантирует целостность данных.
    
    Attributes:
        text: Исходный текст для классификации
        toxicity_score: Оценка токсичности (0.0 - 1.0)
        toxicity_level: Уровень токсичности
        model_version: Версия модели, использованная для предсказания
        confidence: Уверенность модели в предсказании
    """
    text: str
    toxicity_score: float
    toxicity_level: ToxicityLevel
    model_version: str
    confidence: float = 1.0
    
    def __post_init__(self):
        """
        Валидация данных после инициализации.
        
        Raises:
            ValueError: Если данные невалидны
        """
        if not 0.0 <= self.toxicity_score <= 1.0:
            raise ValueError(f"Toxicity score must be between 0.0 and 1.0, got {self.toxicity_score}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.text or not self.text.strip():
            raise ValueError("Text cannot be empty")


@dataclass
class PredictionResult:
    """
    Результат предсказания модели.
    
    Доменная сущность, представляющая результат работы модели классификации.
    Содержит метаданные о предсказании для аудита и анализа.
    
    Attributes:
        id: Уникальный идентификатор предсказания
        text_classification: Результат классификации текста
        created_at: Время создания предсказания
        processing_time_ms: Время обработки в миллисекундах
        metadata: Дополнительные метаданные (JSON-совместимый dict)
    """
    id: UUID
    text_classification: TextClassification
    created_at: datetime
    processing_time_ms: float
    metadata: Optional[dict] = None
    
    @classmethod
    def create(
        cls,
        text: str,
        toxicity_score: float,
        model_version: str,
        processing_time_ms: float,
        confidence: float = 1.0,
        metadata: Optional[dict] = None,
    ) -> "PredictionResult":
        """
        Фабричный метод для создания PredictionResult.
        
        Использует Factory Pattern для инкапсуляции логики создания.
        
        Args:
            text: Исходный текст
            toxicity_score: Оценка токсичности
            model_version: Версия модели
            processing_time_ms: Время обработки
            confidence: Уверенность модели
            metadata: Дополнительные метаданные
            
        Returns:
            PredictionResult: Созданный результат предсказания
        """
        toxicity_level = ToxicityLevel.from_score(toxicity_score)
        classification = TextClassification(
            text=text,
            toxicity_score=toxicity_score,
            toxicity_level=toxicity_level,
            model_version=model_version,
            confidence=confidence,
        )
        return cls(
            id=uuid4(),
            text_classification=classification,
            created_at=datetime.utcnow(),
            processing_time_ms=processing_time_ms,
            metadata=metadata or {},
        )

