"""
Dependency Injection Container

Использует dependency-injector для управления зависимостями.
Централизует создание и конфигурацию компонентов системы.

Паттерны:
- Dependency Injection
- Service Locator Pattern (через контейнер)
- Inversion of Control (IoC)
"""

from dependency_injector import containers, providers

from application.services import ModelService, TextPreprocessingService
from application.use_cases import PredictTextUseCase, GetPredictionHistoryUseCase
from infrastructure.database import Database
from infrastructure.repositories import PredictionRepository


class Container(containers.DeclarativeContainer):
    """
    Контейнер зависимостей для всего приложения.
    
    Управляет lifecycle и зависимостями всех компонентов:
    - Database
    - Services
    - Repositories
    - Use Cases
    
    Использует Singleton для сервисов и Factory для use cases.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Database
    database = providers.Singleton(Database)
    
    # Repositories (Factory, создается для каждой сессии)
    prediction_repository = providers.Factory(
        PredictionRepository,
        session=providers.Dependency(),
    )
    
    # Services (Singleton, один экземпляр на все приложение)
    text_preprocessing_service = providers.Singleton(
        TextPreprocessingService,
    )
    
    model_service = providers.Singleton(
        ModelService,
        preprocessor=text_preprocessing_service,
    )
    
    # Use Cases (Factory, можно создавать несколько экземпляров)
    predict_text_use_case = providers.Factory(
        PredictTextUseCase,
        model_service=model_service,
        prediction_repository=prediction_repository,
    )
    
    get_prediction_history_use_case = providers.Factory(
        GetPredictionHistoryUseCase,
        prediction_repository=prediction_repository,
    )

