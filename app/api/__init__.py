"""
API Layer (Presentation Layer)

Содержит HTTP endpoints и схемы для FastAPI.
Это точка входа для всех HTTP запросов.

Паттерны:
- REST API Pattern
- DTO Pattern (Data Transfer Objects)
- Controller Pattern
"""

from app.api.routes import router

__all__ = ["router"]

