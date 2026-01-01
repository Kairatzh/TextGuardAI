"""
Repository Implementations

Реализации репозиториев для работы с БД.
Преобразуют между ORM моделями и доменными сущностями.

Паттерны:
- Repository Pattern (реализация)
- Data Mapper Pattern
- Unit of Work (через SQLAlchemy сессии)
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from domain.entities import PredictionResult
from domain.repositories import IPredictionRepository
from domain.value_objects import ToxicityLevel
from infrastructure.models import PredictionORM

logger = structlog.get_logger(__name__)


class PredictionRepository(IPredictionRepository):
    """
    Реализация репозитория для работы с предсказаниями в PostgreSQL.
    
    Использует SQLAlchemy ORM для работы с БД.
    Преобразует между ORM моделями и доменными сущностями.
    
    Args:
        session: Async сессия SQLAlchemy
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория.
        
        Args:
            session: Async сессия SQLAlchemy
        """
        self.session = session
    
    def _to_domain(self, orm_model: PredictionORM) -> PredictionResult:
        """
        Преобразовать ORM модель в доменную сущность.
        
        Использует Data Mapper Pattern для преобразования между слоями.
        
        Args:
            orm_model: ORM модель из БД
            
        Returns:
            PredictionResult: Доменная сущность
        """
        from domain.entities import TextClassification
        
        classification = TextClassification(
            text=orm_model.text,
            toxicity_score=orm_model.toxicity_score,
            toxicity_level=ToxicityLevel(orm_model.toxicity_level),
            model_version=orm_model.model_version,
            confidence=orm_model.confidence,
        )
        
        return PredictionResult(
            id=orm_model.id,
            text_classification=classification,
            created_at=orm_model.created_at,
            processing_time_ms=orm_model.processing_time_ms,
            metadata=orm_model.metadata or {},
        )
    
    def _from_domain(self, domain_entity: PredictionResult) -> PredictionORM:
        """
        Преобразовать доменную сущность в ORM модель.
        
        Args:
            domain_entity: Доменная сущность
            
        Returns:
            PredictionORM: ORM модель для сохранения в БД
        """
        return PredictionORM(
            id=domain_entity.id,
            text=domain_entity.text_classification.text,
            toxicity_score=domain_entity.text_classification.toxicity_score,
            toxicity_level=domain_entity.text_classification.toxicity_level.value,
            model_version=domain_entity.text_classification.model_version,
            confidence=domain_entity.text_classification.confidence,
            processing_time_ms=domain_entity.processing_time_ms,
            metadata=domain_entity.metadata,
            created_at=domain_entity.created_at,
        )
    
    async def save(self, prediction: PredictionResult) -> PredictionResult:
        """
        Сохранить результат предсказания в БД.
        
        Использует merge для обновления существующих записей
        или создания новых.
        
        Args:
            prediction: Результат предсказания для сохранения
            
        Returns:
            PredictionResult: Сохраненный результат
        """
        logger.debug("Saving prediction", prediction_id=str(prediction.id))
        
        orm_model = self._from_domain(prediction)
        self.session.add(orm_model)
        await self.session.flush()  # Получить ID если был сгенерирован
        await self.session.refresh(orm_model)
        
        logger.info("Prediction saved", prediction_id=str(orm_model.id))
        
        return self._to_domain(orm_model)
    
    async def get_by_id(self, prediction_id: UUID) -> Optional[PredictionResult]:
        """
        Получить предсказание по ID.
        
        Args:
            prediction_id: UUID предсказания
            
        Returns:
            Optional[PredictionResult]: Результат предсказания или None
        """
        logger.debug("Fetching prediction by id", prediction_id=str(prediction_id))
        
        stmt = select(PredictionORM).where(PredictionORM.id == prediction_id)
        result = await self.session.execute(stmt)
        orm_model = result.scalar_one_or_none()
        
        if orm_model is None:
            return None
        
        return self._to_domain(orm_model)
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PredictionResult]:
        """
        Получить список предсказаний с пагинацией.
        
        Сортирует по времени создания (новые первые).
        
        Args:
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            
        Returns:
            List[PredictionResult]: Список результатов предсказаний
        """
        logger.debug("Fetching all predictions", limit=limit, offset=offset)
        
        stmt = (
            select(PredictionORM)
            .order_by(PredictionORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        orm_models = result.scalars().all()
        
        return [self._to_domain(orm_model) for orm_model in orm_models]
    
    async def get_by_text(
        self,
        text: str,
        limit: int = 100,
    ) -> List[PredictionResult]:
        """
        Получить предсказания по тексту.
        
        Используется для кеширования и поиска похожих предсказаний.
        
        Args:
            text: Текст для поиска
            limit: Максимальное количество записей
            
        Returns:
            List[PredictionResult]: Список результатов предсказаний
        """
        logger.debug("Fetching predictions by text", text_length=len(text), limit=limit)
        
        stmt = (
            select(PredictionORM)
            .where(PredictionORM.text == text)
            .order_by(PredictionORM.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        orm_models = result.scalars().all()
        
        return [self._to_domain(orm_model) for orm_model in orm_models]

