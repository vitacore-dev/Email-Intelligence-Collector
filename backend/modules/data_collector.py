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
from .search_engines import SearchEngineManager, SearchResultProcessor, SearchEngineConfig
from .pdf_analyzer import PDFAnalyzer
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
            'search_results': [],
            'search_statistics': {},
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
            
            # Дополнительный поиск через поисковые системы
            await self._search_engine_collection()
            
            # Дополнительный поиск по найденным данным
            await self._enhanced_search()
            
            # PDF анализ
            await self._pdf_search_and_analysis()
            
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
    
    async def _search_engine_collection(self):
        """Сбор данных через поисковые системы"""
        logger.info(f"Starting search engine collection for {self.email}")
        
        try:
            # Создаем конфигурацию для поиска
            search_config = SearchEngineConfig(
                max_results=10,
                timeout=30,
                delay_between_requests=2.0
            )
            
            async with SearchEngineManager(search_config) as search_manager:
                # Выполняем комплексный поиск
                search_data = await search_manager.comprehensive_email_search(self.email)
                
                # Сохраняем результаты поиска
                self.results['search_results'] = [
                    {
                        'title': result.title,
                        'url': result.url,
                        'snippet': result.snippet,
                        'source': result.source,
                        'rank': result.rank,
                        'relevance_score': result.relevance_score
                    }
                    for result in search_data['search_results']
                ]
                
                self.results['search_statistics'] = search_data['statistics']
                
                # Добавляем поисковые системы как источники
                search_engines = search_data['statistics'].get('search_engines_used', [])
                for engine in search_engines:
                    if engine not in self.results['sources']:
                        self.results['sources'].append(f"Search-{engine.title()}")
                
                # Обработка найденных URL через веб-скрапер
                await self._process_search_results(search_data['search_results'])
                
                logger.info(f"Found {len(search_data['search_results'])} relevant results from search engines")
                
        except Exception as e:
            logger.error(f"Error in search engine collection: {e}")
    
    async def _process_search_results(self, search_results):
        """Обработка результатов поиска через веб-скрапер"""
        if not search_results:
            return
            
        try:
            # Создаем обработчик результатов поиска
            async with SearchResultProcessor() as processor:
                processed_results = await processor.process_search_results(search_results)
                
                # Извлекаем дополнительную информацию со страниц
                for result in processed_results:
                    extracted_data = result.extracted_data
                    
                    if extracted_data:
                        # Добавляем найденные email адреса
                        for email in extracted_data.get('emails', []):
                            if email != self.email and email not in self.results['phone_numbers']:
                                # Можно добавить связанные email в отдельное поле
                                pass
                        
                        # Добавляем социальные ссылки
                        for social_link in extracted_data.get('social_links', []):
                            social_profile = {
                                'platform': social_link['platform'],
                                'url': social_link['url'],
                                'username': self._extract_username_from_url(social_link['url']),
                                'verified': False,
                                'source': 'search_engine'
                            }
                            
                            # Проверяем, что профиль еще не добавлен
                            if not any(p['url'] == social_profile['url'] for p in self.results['social_profiles']):
                                self.results['social_profiles'].append(social_profile)
                        
                        # Добавляем найденные телефоны
                        for phone in extracted_data.get('contact_info', {}).get('phones', []):
                            cleaned_phone = self._clean_phone_number(phone)
                            if cleaned_phone and cleaned_phone not in self.results['phone_numbers']:
                                self.results['phone_numbers'].append(cleaned_phone)
                        
                        # Добавляем URL как веб-сайт
                        if result.url not in self.results['websites']:
                            self.results['websites'].append(result.url)
                            
        except Exception as e:
            logger.error(f"Error processing search results: {e}")
    
    def _extract_username_from_url(self, url: str) -> str:
        """Извлечение имени пользователя из URL социальной сети"""
        try:
            # Простое извлечение имени пользователя из URL
            if 'linkedin.com/in/' in url:
                return url.split('/in/')[-1].split('/')[0]
            elif 'twitter.com/' in url or 'x.com/' in url:
                return url.split('/')[-1].split('?')[0]
            elif 'facebook.com/' in url:
                return url.split('/')[-1].split('?')[0]
            elif 'github.com/' in url:
                return url.split('/')[-1].split('?')[0]
            else:
                return url.split('/')[-1].split('?')[0]
        except:
            return ''
    
    def _clean_phone_number(self, phone: str) -> Optional[str]:
        """Очистка и валидация номера телефона"""
        # Удаляем все символы кроме цифр и +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Проверяем минимальную длину
        if len(cleaned) >= 10:
            return cleaned
        return None
    
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
    
    async def _pdf_search_and_analysis(self):
        """Поиск и анализ PDF документов"""
        logger.info(f"Starting PDF search and analysis for {self.email}")
        
        try:
            async with PDFAnalyzer(self.session) as pdf_analyzer:
                pdf_results = await pdf_analyzer.search_pdf_documents(self.email)
                
                if pdf_results:
                    # Добавляем PDF результаты в основные данные
                    self.results['pdf_documents'] = pdf_results
                    
                    # Обрабатываем найденную информацию из PDF
                    await self._process_pdf_results(pdf_results)
                    
                    # Добавляем PDF источники
                    pdf_sources = list(set([pdf.get('source', 'PDF') for pdf in pdf_results]))
                    for source in pdf_sources:
                        source_name = f"PDF-{source}"
                        if source_name not in self.results['sources']:
                            self.results['sources'].append(source_name)
                    
                    logger.info(f"Found {len(pdf_results)} PDF documents for {self.email}")
                else:
                    logger.info(f"No PDF documents found for {self.email}")
                    
        except Exception as e:
            logger.error(f"Error in PDF search and analysis: {e}")
    
    async def _process_pdf_results(self, pdf_results: List[Dict[str, Any]]):
        """Обработка результатов PDF анализа"""
        for pdf_result in pdf_results:
            # Добавляем авторов в персональную информацию
            authors = pdf_result.get('authors', [])
            if authors and not self.results['person_info'].get('name'):
                # Берем первого автора как возможное имя
                self.results['person_info']['name'] = authors[0]
                self.results['person_info']['source'] = 'PDF document'
            
            # Добавляем учреждения
            institutions = pdf_result.get('institutions', [])
            if institutions:
                # Можно добавить в отдельное поле или в person_info
                if not self.results['person_info'].get('organization'):
                    self.results['person_info']['organization'] = institutions[0]
            
            # Добавляем найденные email адреса
            all_emails = pdf_result.get('all_emails', [])
            for email in all_emails:
                if email != self.email and email not in [p.get('email') for p in self.results.get('related_emails', [])]:
                    if 'related_emails' not in self.results:
                        self.results['related_emails'] = []
                    self.results['related_emails'].append({
                        'email': email,
                        'source': f"PDF: {pdf_result.get('title', 'Unknown')}",
                        'confidence': pdf_result.get('confidence_score', 0.0)
                    })
            
            # Добавляем URL PDF как веб-сайт
            pdf_url = pdf_result.get('url')
            if pdf_url and pdf_url not in self.results['websites']:
                self.results['websites'].append(pdf_url)
    
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

