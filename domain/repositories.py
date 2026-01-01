"""
Репозитории (Repository Pattern)

Интерфейсы репозиториев определяют контракты для работы с данными.
Реализация находится в infrastructure layer.

Паттерны:
- Repository Pattern
- Interface Segregation Principle
- Dependency Inversion Principle
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities import PredictionResult


class IPredictionRepository(ABC):
    """
    Интерфейс репозитория для работы с предсказаниями.
    
    Определяет контракт для персистентности данных предсказаний.
    Реализация не зависит от конкретной БД (PostgreSQL, MongoDB, etc.)
    
    Методы:
        save: Сохранить результат предсказания
        get_by_id: Получить предсказание по ID
        get_all: Получить все предсказания (с пагинацией)
        get_by_text: Получить предсказания по тексту
    """
    
    @abstractmethod
    async def save(self, prediction: PredictionResult) -> PredictionResult:
        """
        Сохранить результат предсказания в хранилище.
        
        Args:
            prediction: Результат предсказания для сохранения
            
        Returns:
            PredictionResult: Сохраненный результат с обновленными данными
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, prediction_id: UUID) -> Optional[PredictionResult]:
        """
        Получить предсказание по уникальному идентификатору.
        
        Args:
            prediction_id: UUID предсказания
            
        Returns:
            Optional[PredictionResult]: Результат предсказания или None если не найдено
        """
        pass
    
    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PredictionResult]:
        """
        Получить список предсказаний с пагинацией.
        
        Args:
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            
        Returns:
            List[PredictionResult]: Список результатов предсказаний
        """
        pass
    
    @abstractmethod
    async def get_by_text(
        self,
        text: str,
        limit: int = 100,
    ) -> List[PredictionResult]:
        """
        Получить предсказания по тексту (для кеширования).
        
        Args:
            text: Текст для поиска
            limit: Максимальное количество записей
            
        Returns:
            List[PredictionResult]: Список результатов предсказаний
        """
        pass

