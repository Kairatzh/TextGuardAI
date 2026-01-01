"""
HTTP Clients

Клиенты для работы с внешними HTTP API.
Использует httpx для асинхронных HTTP запросов.

Паттерны:
- Adapter Pattern (для различных API)
- Client Pattern
- Retry Pattern (можно расширить)
"""

import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class IHTTPClient(ABC):
    """
    Интерфейс для HTTP клиентов.
    
    Абстрагирует работу с HTTP запросами для различных сервисов.
    """
    
    @abstractmethod
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполнить GET запрос.
        
        Args:
            url: URL для запроса
            params: Query параметры
            
        Returns:
            Dict[str, Any]: JSON ответ
        """
        pass
    
    @abstractmethod
    async def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполнить POST запрос.
        
        Args:
            url: URL для запроса
            data: Тело запроса
            
        Returns:
            Dict[str, Any]: JSON ответ
        """
        pass


class HTTPClient(IHTTPClient):
    """
    Реализация HTTP клиента с использованием httpx.
    
    Использует async/await для неблокирующих запросов.
    Поддерживает retry логику и обработку ошибок.
    
    Args:
        base_url: Базовый URL для всех запросов
        timeout: Таймаут запросов в секундах
        headers: Заголовки по умолчанию
    """
    
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Инициализация HTTP клиента.
        
        Args:
            base_url: Базовый URL (опционально)
            timeout: Таймаут запросов
            headers: Заголовки по умолчанию
        """
        self.base_url = base_url
        self.timeout = timeout
        self.default_headers = headers or {}
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """
        Получить или создать HTTP клиент.
        
        Использует ленивую инициализацию.
        
        Returns:
            httpx.AsyncClient: Клиент для HTTP запросов
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.default_headers,
            )
        return self._client
    
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполнить GET запрос.
        
        Args:
            url: URL для запроса
            params: Query параметры
            
        Returns:
            Dict[str, Any]: JSON ответ
            
        Raises:
            httpx.HTTPError: При ошибке HTTP запроса
        """
        client = await self._get_client()
        
        try:
            logger.debug("HTTP GET request", url=url, params=params)
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("HTTP GET request failed", url=url, error=str(e))
            raise
    
    async def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполнить POST запрос.
        
        Args:
            url: URL для запроса
            data: Тело запроса (будет отправлено как JSON)
            
        Returns:
            Dict[str, Any]: JSON ответ
            
        Raises:
            httpx.HTTPError: При ошибке HTTP запроса
        """
        client = await self._get_client()
        
        try:
            logger.debug("HTTP POST request", url=url, data=data)
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("HTTP POST request failed", url=url, error=str(e))
            raise
    
    async def close(self):
        """
        Закрыть HTTP клиент.
        
        Освобождает ресурсы и закрывает соединения.
        """
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.debug("HTTP client closed")


class ExternalMLServiceClient:
    """
    Пример клиента для внешнего ML сервиса.
    
    Демонстрирует использование HTTP клиента для интеграции
    с внешними API (например, для fallback или сравнения моделей).
    
    Args:
        http_client: HTTP клиент для запросов
        api_key: API ключ для аутентификации
    """
    
    def __init__(self, http_client: IHTTPClient, api_key: str):
        """
        Инициализация клиента внешнего сервиса.
        
        Args:
            http_client: HTTP клиент
            api_key: API ключ
        """
        self.http_client = http_client
        self.api_key = api_key
    
    async def predict_toxicity(self, text: str) -> Dict[str, Any]:
        """
        Получить предсказание токсичности от внешнего сервиса.
        
        Args:
            text: Текст для анализа
            
        Returns:
            Dict[str, Any]: Результат предсказания
        """
        return await self.http_client.post(
            "/api/predict",
            data={
                "text": text,
                "api_key": self.api_key,
            },
        )

