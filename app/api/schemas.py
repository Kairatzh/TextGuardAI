"""
API Schemas (DTOs)

Pydantic схемы для валидации входных и выходных данных API.
Используются как Data Transfer Objects (DTO) между слоями.

Паттерны:
- DTO Pattern
- Data Validation Pattern
- Schema Pattern
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TextInputSchema(BaseModel):
    """
    Схема для входных данных предсказания.
    
    Используется для валидации текста перед обработкой.
    
    Attributes:
        text: Текст для анализа (минимум 1 символ, максимум 10000)
    """
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Текст для анализа на токсичность",
        examples=["This is a sample text to analyze"],
    )
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """
        Валидация текста.
        
        Проверяет, что текст не пустой после strip.
        
        Args:
            v: Входное значение
            
        Returns:
            str: Валидированный текст
            
        Raises:
            ValueError: Если текст пустой
        """
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()
    
    class Config:
        """Конфигурация Pydantic модели."""
        json_schema_extra = {
            "example": {
                "text": "This is a sample text to analyze for toxicity"
            }
        }


class PredictionOutputSchema(BaseModel):
    """
    Схема для результата предсказания.
    
    Представляет результат работы модели классификации.
    
    Attributes:
        id: Уникальный идентификатор предсказания
        text: Исходный текст
        toxicity_score: Оценка токсичности (0.0 - 1.0)
        toxicity_level: Уровень токсичности (строка)
        confidence: Уверенность модели (0.0 - 1.0)
        model_version: Версия модели
        processing_time_ms: Время обработки в миллисекундах
        created_at: Время создания предсказания
    """
    
    id: UUID = Field(..., description="Уникальный идентификатор предсказания")
    text: str = Field(..., description="Исходный текст")
    toxicity_score: float = Field(..., ge=0.0, le=1.0, description="Оценка токсичности (0.0 - 1.0)")
    toxicity_level: str = Field(..., description="Уровень токсичности")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность модели (0.0 - 1.0)")
    model_version: str = Field(..., description="Версия модели")
    processing_time_ms: float = Field(..., ge=0.0, description="Время обработки в миллисекундах")
    created_at: datetime = Field(..., description="Время создания предсказания")
    
    class Config:
        """Конфигурация Pydantic модели."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class PredictionHistorySchema(BaseModel):
    """
    Схема для истории предсказаний.
    
    Используется для отображения списка предсказаний.
    Аналогична PredictionOutputSchema, но может быть расширена
    дополнительными полями для списков.
    """
    
    id: UUID = Field(..., description="Уникальный идентификатор предсказания")
    text: str = Field(..., description="Исходный текст")
    toxicity_score: float = Field(..., ge=0.0, le=1.0, description="Оценка токсичности")
    toxicity_level: str = Field(..., description="Уровень токсичности")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность модели")
    model_version: str = Field(..., description="Версия модели")
    processing_time_ms: float = Field(..., ge=0.0, description="Время обработки в миллисекундах")
    created_at: datetime = Field(..., description="Время создания предсказания")
    
    class Config:
        """Конфигурация Pydantic модели."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

