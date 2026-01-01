"""
API Routes

Определяет HTTP endpoints для взаимодействия с API.
Использует dependency injection для получения use cases.

Паттерны:
- REST API Pattern
- Controller Pattern
- Dependency Injection (FastAPI Depends)
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.api.schemas import (
    TextInputSchema,
    PredictionOutputSchema,
    PredictionHistorySchema,
)
from application.use_cases import PredictTextUseCase, GetPredictionHistoryUseCase
from infrastructure.database import get_session
from infrastructure.repositories import PredictionRepository
from infrastructure.dependency_injection import Container

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["predictions"])

# Глобальный контейнер зависимостей (должен быть инициализирован при старте приложения)
container: Container = None


def get_container() -> Container:
    """
    Получить контейнер зависимостей.
    
    Returns:
        Container: Контейнер с зависимостями
    """
    if container is None:
        raise RuntimeError("Container not initialized")
    return container


def get_predict_use_case(session: AsyncSession = Depends(get_session)) -> PredictTextUseCase:
    """
    Dependency для получения PredictTextUseCase.
    
    Args:
        session: Сессия БД из dependency injection
        
    Returns:
        PredictTextUseCase: Use case для предсказаний
    """
    cont = get_container()
    return cont.predict_text_use_case(session=session)


def get_history_use_case(session: AsyncSession = Depends(get_session)) -> GetPredictionHistoryUseCase:
    """
    Dependency для получения GetPredictionHistoryUseCase.
    
    Args:
        session: Сессия БД из dependency injection
        
    Returns:
        GetPredictionHistoryUseCase: Use case для истории предсказаний
    """
    cont = get_container()
    return cont.get_prediction_history_use_case(session=session)


@router.post(
    "/predict",
    response_model=PredictionOutputSchema,
    status_code=status.HTTP_200_OK,
    summary="Предсказать токсичность текста",
    description="Анализирует текст и возвращает оценку токсичности",
)
async def predict_text(
    input_data: TextInputSchema,
    use_case: PredictTextUseCase = Depends(get_predict_use_case),
) -> PredictionOutputSchema:
    """
    Эндпоинт для предсказания токсичности текста.
    
    Использует PredictTextUseCase для обработки запроса.
    Сохраняет результат в БД для истории.
    
    Args:
        input_data: Входные данные (текст)
        use_case: Use case для предсказания (injected)
        
    Returns:
        PredictionOutputSchema: Результат предсказания
        
    Raises:
        HTTPException: При ошибке обработки
    """
    try:
        logger.info("Prediction request received", text_length=len(input_data.text))
        
        prediction = await use_case.execute(text=input_data.text, save_to_db=True)
        
        return PredictionOutputSchema(
            id=prediction.id,
            text=prediction.text_classification.text,
            toxicity_score=prediction.text_classification.toxicity_score,
            toxicity_level=prediction.text_classification.toxicity_level.value,
            confidence=prediction.text_classification.confidence,
            model_version=prediction.text_classification.model_version,
            processing_time_ms=prediction.processing_time_ms,
            created_at=prediction.created_at,
        )
        
    except Exception as e:
        logger.error("Prediction failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.get(
    "/predictions",
    response_model=List[PredictionHistorySchema],
    summary="Получить историю предсказаний",
    description="Возвращает список предсказаний с пагинацией",
)
async def get_predictions(
    limit: int = 100,
    offset: int = 0,
    use_case: GetPredictionHistoryUseCase = Depends(get_history_use_case),
) -> List[PredictionHistorySchema]:
    """
    Эндпоинт для получения истории предсказаний.
    
    Args:
        limit: Максимальное количество записей
        offset: Смещение для пагинации
        use_case: Use case для истории (injected)
        
    Returns:
        List[PredictionHistorySchema]: Список предсказаний
    """
    try:
        predictions = await use_case.execute(limit=limit, offset=offset)
        
        return [
            PredictionHistorySchema(
                id=p.id,
                text=p.text_classification.text,
                toxicity_score=p.text_classification.toxicity_score,
                toxicity_level=p.text_classification.toxicity_level.value,
                confidence=p.text_classification.confidence,
                model_version=p.text_classification.model_version,
                processing_time_ms=p.processing_time_ms,
                created_at=p.created_at,
            )
            for p in predictions
        ]
        
    except Exception as e:
        logger.error("Failed to fetch predictions", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch predictions: {str(e)}",
        )


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionHistorySchema,
    summary="Получить предсказание по ID",
    description="Возвращает детали конкретного предсказания",
)
async def get_prediction_by_id(
    prediction_id: UUID,
    use_case: GetPredictionHistoryUseCase = Depends(get_history_use_case),
) -> PredictionHistorySchema:
    """
    Эндпоинт для получения предсказания по ID.
    
    Args:
        prediction_id: UUID предсказания
        use_case: Use case для истории (injected)
        
    Returns:
        PredictionHistorySchema: Детали предсказания
        
    Raises:
        HTTPException: Если предсказание не найдено
    """
    try:
        prediction = await use_case.get_by_id(prediction_id)
        
        return PredictionHistorySchema(
            id=prediction.id,
            text=prediction.text_classification.text,
            toxicity_score=prediction.text_classification.toxicity_score,
            toxicity_level=prediction.text_classification.toxicity_level.value,
            confidence=prediction.text_classification.confidence,
            model_version=prediction.text_classification.model_version,
            processing_time_ms=prediction.processing_time_ms,
            created_at=prediction.created_at,
        )
        
    except ValueError as e:
        logger.warning("Prediction not found", prediction_id=str(prediction_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Failed to fetch prediction", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prediction: {str(e)}",
        )

