"""
Configuration Management

Управление конфигурацией приложения.
Загружает настройки из YAML файла и переменных окружения.

Паттерны:
- Configuration Pattern
- Environment Variables Pattern
"""

import os.path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv


def load_configs(path: str = "configs/configs.yml") -> Dict[str, Any]:
    """
    Загрузить конфигурацию из YAML файла.
    
    Переменные окружения из .env файла подставляются в YAML
    через синтаксис ${VARIABLE_NAME}.
    
    Args:
        path: Путь к YAML файлу конфигурации
        
    Returns:
        Dict[str, Any]: Словарь с конфигурацией
        
    Example:
        ```yaml
        database:
          host: ${POSTGRES_HOST}
          port: ${POSTGRES_PORT}
        ```
    """
    load_dotenv()
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    resolved = os.path.expandvars(raw)
    return yaml.safe_load(resolved)