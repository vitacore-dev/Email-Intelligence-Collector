"""
Модули для сбора данных Email Intelligence Collector

Содержит коллекторы для различных источников данных:
- DataCollector: основной класс для координации сбора данных
- EmailValidator: валидация email-адресов
- FileProcessor: обработка файлов с email-адресами
- SocialCollectors: коллекторы для социальных сетей
- WebScraper: веб-скрапинг для извлечения информации
"""

from .data_collector import DataCollector
from .email_validator import EmailValidator
from .file_processor import FileProcessor
from .social_collectors import (
    GoogleSearchCollector,
    LinkedInCollector,
    TwitterCollector,
    GitHubCollector,
    FacebookCollector
)
from .web_scraper import WebScraper

__all__ = [
    'DataCollector',
    'EmailValidator', 
    'FileProcessor',
    'GoogleSearchCollector',
    'LinkedInCollector',
    'TwitterCollector',
    'GitHubCollector',
    'FacebookCollector',
    'WebScraper'
]

