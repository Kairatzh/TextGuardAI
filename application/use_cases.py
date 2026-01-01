"""
Use Cases (Use Case Pattern)

Use Cases инкапсулируют бизнес-логику для конкретных сценариев использования.
Они координируют работу domain entities и services.

Паттерны:
- Use Case Pattern
- Command Pattern
- CQRS (можно расширить разделением Command/Query)
"""

import time
from typing import List
from uuid import UUID

import structlog

from application.interfaces import IModelService
from domain.entities import PredictionResult
from domain.repositories import IPredictionRepository

logger = structlog.get_logger(__name__)


class PredictTextUseCase:
    """
    Use Case для предсказания токсичности текста.
    
    Координирует:
    - Вызов модели для предсказания
    - Сохранение результата в репозиторий
    - Создание доменной сущности
    
    Args:
        model_service: Сервис для работы с ML моделью
        prediction_repository: Репозиторий для сохранения предсказаний
    """
    
    def __init__(
        self,
        model_service: IModelService,
        prediction_repository: IPredictionRepository,
    ):
        """
        Инициализация use case.
        
        Args:
            model_service: Сервис для работы с ML моделью
            prediction_repository: Репозиторий для сохранения предсказаний
        """
        self.model_service = model_service
        self.prediction_repository = prediction_repository
    
    async def execute(
        self,
        text: str,
        save_to_db: bool = True,
    ) -> PredictionResult:
        """
        Выполнить предсказание токсичности текста.
        
        Процесс:
        1. Измерение времени начала обработки
        2. Вызов модели для предсказания
        3. Создание доменной сущности PredictionResult
        4. Сохранение в БД (опционально)
        5. Возврат результата
        
        Args:
            text: Текст для анализа
            save_to_db: Сохранять ли результат в БД
            
        Returns:
            PredictionResult: Результат предсказания с метаданными
        """
        start_time = time.time()
        
        try:
            logger.info("Starting prediction", text_length=len(text))
            
            # Получение предсказания от модели
            toxicity_score, confidence = await self.model_service.predict(text)
            model_version = self.model_service.get_model_version()
            
            # Вычисление времени обработки
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Создание доменной сущности
            prediction = PredictionResult.create(
                text=text,
                toxicity_score=toxicity_score,
                model_version=model_version,
                processing_time_ms=processing_time_ms,
                confidence=confidence,
                metadata={
                    "text_length": len(text),
                    "device": "cuda" if hasattr(self.model_service, "_device") else "cpu",
                },
            )
            
            # Сохранение в репозиторий
            if save_to_db:
                prediction = await self.prediction_repository.save(prediction)
                logger.info(
                    "Prediction saved",
                    prediction_id=str(prediction.id),
                    toxicity_score=toxicity_score,
                )
            else:
                logger.info("Prediction completed (not saved)", toxicity_score=toxicity_score)
            
            return prediction
            
        except Exception as e:
            logger.error("Prediction failed", error=str(e), exc_info=True)
            raise


class GetPredictionHistoryUseCase:
    """
    Use Case для получения истории предсказаний.
    
    Реализует паттерн Query в стиле CQRS.
    
    Args:
        prediction_repository: Репозиторий для получения предсказаний
    """
    
    def __init__(self, prediction_repository: IPredictionRepository):
        """
        Инициализация use case.
        
        Args:
            prediction_repository: Репозиторий для получения предсказаний
        """
        self.prediction_repository = prediction_repository
    
    async def execute(
        self,
        limit: int = 100,
        offset: int = 0,
        text: str = None,
    ) -> List[PredictionResult]:
        """
        Получить историю предсказаний.
        
        Args:
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            text: Опциональный фильтр по тексту
            
        Returns:
            List[PredictionResult]: Список результатов предсказаний
        """
        logger.info("Fetching prediction history", limit=limit, offset=offset, has_text_filter=bool(text))
        
        if text:
            results = await self.prediction_repository.get_by_text(text, limit=limit)
        else:
            results = await self.prediction_repository.get_all(limit=limit, offset=offset)
        
        logger.info("Prediction history fetched", count=len(results))
        return results
    
    async def get_by_id(self, prediction_id: UUID) -> PredictionResult:
        """
        Получить предсказание по ID.
        
        Args:
            prediction_id: UUID предсказания
            
        Returns:
            PredictionResult: Результат предсказания
            
        Raises:
            ValueError: Если предсказание не найдено
        """
        logger.info("Fetching prediction by id", prediction_id=str(prediction_id))
        
        result = await self.prediction_repository.get_by_id(prediction_id)
        
        if result is None:
            logger.warning("Prediction not found", prediction_id=str(prediction_id))
            raise ValueError(f"Prediction with id {prediction_id} not found")
        
        return result

