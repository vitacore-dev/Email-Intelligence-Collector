import asyncio
import aiohttp
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from .social_collectors import (
    GoogleSearchCollector,
    LinkedInCollector,
    TwitterCollector,
    GitHubCollector,
    FacebookCollector
)
from .web_scraper import WebScraper
from .email_validator import EmailValidator
from config.settings import settings

logger = logging.getLogger(__name__)

class DataCollector:
    """Основной класс для сбора данных по email-адресу"""
    
    def __init__(self, email: str):
        self.email = email.lower().strip()
        self.session = None
        self.collectors = []
        self.results = {
            'email': self.email,
            'person_info': {},
            'social_profiles': [],
            'websites': [],
            'phone_numbers': [],
            'addresses': [],
            'sources': [],
            'confidence_score': 0.0,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Инициализация коллекторов
        self._init_collectors()
    
    def _init_collectors(self):
        """Инициализация всех коллекторов данных"""
        self.collectors = [
            GoogleSearchCollector(self.email),
            LinkedInCollector(self.email),
            TwitterCollector(self.email),
            GitHubCollector(self.email),
            FacebookCollector(self.email)
        ]
    
    async def collect_all(self) -> Dict[str, Any]:
        """Запуск сбора данных из всех источников"""
        logger.info(f"Starting data collection for {self.email}")
        
        # Проверка валидности email
        if not EmailValidator.is_valid(self.email):
            raise ValueError(f"Invalid email format: {self.email}")
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT),
            connector=aiohttp.TCPConnector(limit=settings.MAX_CONCURRENT_REQUESTS)
        ) as session:
            self.session = session
            
            # Запуск всех коллекторов параллельно
            tasks = []
            for collector in self.collectors:
                collector.session = session
                tasks.append(self._safe_collect(collector))
            
            # Ожидание завершения всех задач
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обработка результатов
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error in collector {self.collectors[i].__class__.__name__}: {result}")
                elif result:
                    self._merge_results(result)
            
            # Дополнительный поиск по найденным данным
            await self._enhanced_search()
            
            # Вычисление рейтинга достоверности
            self._calculate_confidence_score()
            
            logger.info(f"Data collection completed for {self.email}. Sources: {len(self.results['sources'])}")
            
        return self.results
    
    async def _safe_collect(self, collector) -> Optional[Dict[str, Any]]:
        """Безопасный запуск коллектора с обработкой ошибок"""
        try:
            return await collector.collect()
        except Exception as e:
            logger.error(f"Error in {collector.__class__.__name__}: {e}")
            return None
    
    def _merge_results(self, data: Dict[str, Any]):
        """Объединение результатов от коллектора"""
        if not data:
            return
        
        # Объединение персональной информации
        if 'person_info' in data:
            for key, value in data['person_info'].items():
                if value and not self.results['person_info'].get(key):
                    self.results['person_info'][key] = value
        
        # Добавление социальных профилей
        if 'social_profiles' in data:
            for profile in data['social_profiles']:
                if not any(p['url'] == profile['url'] for p in self.results['social_profiles']):
                    self.results['social_profiles'].append(profile)
        
        # Добавление веб-сайтов
        if 'websites' in data:
            for website in data['websites']:
                if website not in self.results['websites']:
                    self.results['websites'].append(website)
        
        # Добавление телефонов
        if 'phone_numbers' in data:
            for phone in data['phone_numbers']:
                if phone not in self.results['phone_numbers']:
                    self.results['phone_numbers'].append(phone)
        
        # Добавление адресов
        if 'addresses' in data:
            for address in data['addresses']:
                if address not in self.results['addresses']:
                    self.results['addresses'].append(address)
        
        # Добавление источников
        if 'sources' in data:
            for source in data['sources']:
                if source not in self.results['sources']:
                    self.results['sources'].append(source)
    
    async def _enhanced_search(self):
        """Дополнительный поиск на основе найденных данных"""
        # Поиск по имени, если оно найдено
        if self.results['person_info'].get('name'):
            name = self.results['person_info']['name']
            enhanced_collector = GoogleSearchCollector(f'"{name}" {self.email}')
            enhanced_collector.session = self.session
            
            try:
                enhanced_data = await enhanced_collector.collect()
                if enhanced_data:
                    self._merge_results(enhanced_data)
            except Exception as e:
                logger.error(f"Error in enhanced search: {e}")
    
    def _calculate_confidence_score(self):
        """Вычисление рейтинга достоверности данных"""
        score = 0.0
        
        # Базовые баллы за наличие данных
        if self.results['person_info'].get('name'):
            score += 0.3
        if self.results['social_profiles']:
            score += 0.2 * min(len(self.results['social_profiles']), 3)
        if self.results['websites']:
            score += 0.1 * min(len(self.results['websites']), 2)
        if self.results['sources']:
            score += 0.1 * min(len(self.results['sources']), 5)
        
        # Дополнительные баллы за верифицированные профили
        verified_profiles = sum(1 for p in self.results['social_profiles'] if p.get('verified'))
        score += 0.1 * verified_profiles
        
        self.results['confidence_score'] = min(score, 1.0)
    
    def get_summary(self) -> Dict[str, Any]:
        """Получение краткой сводки результатов"""
        return {
            'email': self.email,
            'name': self.results['person_info'].get('name', 'Unknown'),
            'social_count': len(self.results['social_profiles']),
            'sources_count': len(self.results['sources']),
            'confidence_score': self.results['confidence_score'],
            'last_updated': self.results['last_updated']
        }

