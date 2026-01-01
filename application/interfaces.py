"""
Интерфейсы для Application Layer

Определяет контракты для сервисов, используемых в use cases.
"""

from abc import ABC, abstractmethod
from typing import Tuple

from domain.entities import TextClassification


class IModelService(ABC):
    """
    Интерфейс для сервиса работы с ML моделью.
    
    Абстрагирует детали работы с конкретной моделью (PyTorch, TensorFlow, etc.)
    """
    
    @abstractmethod
    async def predict(self, text: str) -> Tuple[float, float]:
        """
        Выполнить предсказание токсичности текста.
        
        Args:
            text: Текст для анализа
            
        Returns:
            Tuple[float, float]: (toxicity_score, confidence)
        """
        pass
    
    @abstractmethod
    def get_model_version(self) -> str:
        """
        Получить версию модели.
        
        Returns:
            str: Версия модели
        """
        pass


class ITextPreprocessingService(ABC):
    """
    Интерфейс для сервиса предобработки текста.
    
    Абстрагирует логику предобработки текста.
    """
    
    @abstractmethod
    def preprocess(self, text: str) -> str:
        """
        Предобработать текст перед подачей в модель.
        
        Args:
            text: Исходный текст
            
        Returns:
            str: Предобработанный текст
        """
        pass

