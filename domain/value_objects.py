"""
Value Objects

Value Objects представляют концепции предметной области без идентичности.
Они сравниваются по значению, а не по ссылке.

Паттерны:
- Value Object Pattern
- Immutability
"""

from dataclasses import dataclass
from enum import Enum


class ToxicityLevel(str, Enum):
    """
    Value Object для уровня токсичности.
    
    Enum обеспечивает типобезопасность и ограничивает возможные значения.
    """
    NON_TOXIC = "non_toxic"
    TOXIC = "toxic"
    HATE = "hate"
    SPAM = "spam"
    
    @classmethod
    def from_score(cls, score: float, threshold: float = 0.5) -> "ToxicityLevel":
        """
        Преобразует числовой score в уровень токсичности.
        
        Args:
            score: Оценка токсичности (0.0 - 1.0)
            threshold: Порог для классификации (по умолчанию 0.5)
            
        Returns:
            ToxicityLevel: Уровень токсичности
        """
        if score < threshold:
            return cls.NON_TOXIC
        return cls.TOXIC


@dataclass(frozen=True)
class ModelConfig:
    """
    Конфигурация модели.
    
    Immutable Value Object для хранения параметров модели.
    
    Attributes:
        model_version: Версия модели
        model_path: Путь к файлу модели
        vectorizer_path: Путь к векторaйзеру
        input_size: Размер входного слоя
        hidden_size: Размер скрытого слоя
        output_size: Размер выходного слоя
    """
    model_version: str
    model_path: str
    vectorizer_path: str
    input_size: int
    hidden_size: int
    output_size: int

