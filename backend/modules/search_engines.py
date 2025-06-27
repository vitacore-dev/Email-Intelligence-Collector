import asyncio
import aiohttp
import re
import json
import time
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup
import logging
from dataclasses import dataclass, field
from datetime import datetime
import random
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Результат поиска"""
    title: str
    url: str
    snippet: str
    source: str
    rank: int
    relevance_score: float = 0.0
    extracted_data: Dict[str, Any] = field(default_factory=dict)

@dataclass  
class SearchEngineConfig:
    """Конфигурация поисковых систем"""
    max_results: int = 10
    timeout: int = 30
    delay_between_requests: float = 2.0
    user_agents: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
    ])

class SearchEngineManager:
    """Менеджер для работы с различными поисковыми системами"""
    
    def __init__(self, config: Optional[SearchEngineConfig] = None):
        self.config = config or SearchEngineConfig()
        self.session = None
        self.cache: Dict[str, List[SearchResult]] = {}
        self.last_request_time: Dict[str, float] = {}
        
        # Поисковые системы и их настройки
        self.search_engines = {
            'google': {
                'url_template': 'https://www.google.com/search?q={query}&num={num}',
                'selectors': {
                    'results': 'div.g',
                    'title': 'h3',
                    'url': 'a[href]',
                    'snippet': '.VwiC3b, .s3v9rd'
                },
                'enabled': True
            },
            'bing': {
                'url_template': 'https://www.bing.com/search?q={query}&count={num}',
                'selectors': {
                    'results': '.b_algo',
                    'title': 'h2 a',
                    'url': 'h2 a[href]',
                    'snippet': '.b_caption p'
                },
                'enabled': True
            },
            'duckduckgo': {
                'url_template': 'https://html.duckduckgo.com/html/?q={query}',
                'selectors': {
                    'results': '.result',
                    'title': '.result__title a',
                    'url': '.result__title a[href]',
                    'snippet': '.result__snippet'
                },
                'enabled': True
            },
            'yandex': {
                'url_template': 'https://yandex.com/search/?text={query}&numdoc={num}',
                'selectors': {
                    'results': '.serp-item',
                    'title': '.organic__title a',
                    'url': '.organic__title a[href]',
                    'snippet': '.organic__text'
                },
                'enabled': True
            }
        }
        
    async def __aenter__(self):
        """Асинхронный менеджер контекста"""
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            
    def _get_cache_key(self, query: str, engine: str) -> str:
        """Генерация ключа кеша"""
        return hashlib.md5(f"{query}:{engine}".encode()).hexdigest()
        
    def _get_random_user_agent(self) -> str:
        """Получение случайного User-Agent"""
        return random.choice(self.config.user_agents)
        
    async def _respect_rate_limit(self, engine: str):
        """Соблюдение лимитов запросов"""
        now = time.time()
        last_request = self.last_request_time.get(engine, 0)
        
        if now - last_request < self.config.delay_between_requests:
            sleep_time = self.config.delay_between_requests - (now - last_request)
            await asyncio.sleep(sleep_time)
            
        self.last_request_time[engine] = time.time()
        
    async def search_single_engine(self, query: str, engine: str) -> List[SearchResult]:
        """Поиск в одной поисковой системе"""
        if engine not in self.search_engines or not self.search_engines[engine]['enabled']:
            return []
            
        cache_key = self._get_cache_key(query, engine)
        if cache_key in self.cache:
            logger.info(f"Cache hit for {engine} search: {query}")
            return self.cache[cache_key]
            
        await self._respect_rate_limit(engine)
        
        engine_config = self.search_engines[engine]
        
        # Формируем URL для поиска
        search_url = engine_config['url_template'].format(
            query=quote_plus(query),
            num=self.config.max_results
        )
        
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Специфичные заголовки для разных поисковиков
        if engine == 'google':
            headers['Accept-Language'] = 'en-US,en;q=0.9'
        elif engine == 'bing':
            headers['Accept-Language'] = 'en-US,en;q=0.8'
            
        try:
            async with self.session.get(search_url, headers=headers) as response:
                if response.status != 200:
                    logger.warning(f"Search engine {engine} returned status {response.status}")
                    return []
                    
                html = await response.text()
                results = self._parse_search_results(html, engine, engine_config['selectors'])
                
                # Кешируем результаты
                self.cache[cache_key] = results
                
                logger.info(f"Found {len(results)} results from {engine}")
                return results
                
        except Exception as e:
            logger.error(f"Error searching {engine}: {str(e)}")
            return []
            
    def _parse_search_results(self, html: str, engine: str, selectors: Dict[str, str]) -> List[SearchResult]:
        """Парсинг результатов поиска"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        result_elements = soup.select(selectors['results'])
        
        for rank, result_elem in enumerate(result_elements[:self.config.max_results], 1):
            try:
                # Извлекаем заголовок
                title_elem = result_elem.select_one(selectors['title'])
                title = title_elem.get_text().strip() if title_elem else ""
                
                # Извлекаем URL
                url_elem = result_elem.select_one(selectors['url'])
                if not url_elem:
                    continue
                    
                url = url_elem.get('href', '')
                
                # Обработка относительных URL для разных поисковиков
                if engine == 'google' and url.startswith('/url?'):
                    # Google перенаправляет через /url?q=
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                    if 'q' in parsed:
                        url = parsed['q'][0]
                elif engine == 'bing' and not url.startswith('http'):
                    url = 'https://www.bing.com' + url
                elif engine == 'duckduckgo' and url.startswith('/l/?uddg='):
                    # DuckDuckGo использует перенаправления
                    import urllib.parse
                    url = urllib.parse.unquote(url.split('uddg=')[1])
                    
                # Извлекаем описание
                snippet_elem = result_elem.select_one(selectors['snippet'])
                snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                
                if url and title:
                    result = SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source=engine,
                        rank=rank,
                        relevance_score=self._calculate_relevance_score(title, snippet, rank)
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.warning(f"Error parsing result #{rank} from {engine}: {str(e)}")
                continue
                
        return results
        
    def _calculate_relevance_score(self, title: str, snippet: str, rank: int) -> float:
        """Расчет релевантности результата"""
        score = 1.0
        
        # Снижаем релевантность в зависимости от позиции
        score -= (rank - 1) * 0.1
        
        # Увеличиваем релевантность для более длинных описаний
        if len(snippet) > 100:
            score += 0.1
            
        # Проверяем наличие контактной информации
        if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', title + ' ' + snippet):
            score += 0.2
            
        # Проверяем наличие социальных сетей
        social_keywords = ['linkedin', 'twitter', 'facebook', 'instagram', 'github']
        for keyword in social_keywords:
            if keyword in (title + ' ' + snippet).lower():
                score += 0.15
                break
                
        return max(0.0, min(1.0, score))
        
    async def search_all_engines(self, query: str) -> List[SearchResult]:
        """Поиск во всех доступных поисковых системах"""
        tasks = []
        enabled_engines = [
            engine for engine, config in self.search_engines.items() 
            if config['enabled']
        ]
        
        for engine in enabled_engines:
            task = self.search_single_engine(query, engine)
            tasks.append(task)
            
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for engine, results in zip(enabled_engines, results_lists):
            if isinstance(results, Exception):
                logger.error(f"Error in {engine} search: {str(results)}")
                continue
            all_results.extend(results)
            
        # Удаляем дубликаты по URL
        unique_results = []
        seen_urls = set()
        
        for result in sorted(all_results, key=lambda x: x.relevance_score, reverse=True):
            if result.url not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result.url)
                
        return unique_results[:self.config.max_results]
        
    def create_search_queries_for_email(self, email: str) -> List[str]:
        """Создание поисковых запросов для email"""
        username = email.split('@')[0]
        domain = email.split('@')[1]
        
        queries = [
            f'"{email}"',  # Точный поиск email
            f'"{username}" site:{domain}',  # Поиск пользователя на домене
            f'"{username}" "{domain}"',  # Поиск пользователя и домена
            f'"{email}" profile',  # Поиск профилей
            f'"{email}" contact',  # Поиск контактной информации
            f'"{email}" linkedin',  # Поиск в LinkedIn
            f'"{email}" twitter',  # Поиск в Twitter
            f'"{email}" facebook',  # Поиск в Facebook
            f'"{email}" github',  # Поиск в GitHub
            f'"{username}" profile {domain}',  # Альтернативный поиск профиля
        ]
        
        return queries
        
    async def comprehensive_email_search(self, email: str) -> Dict[str, Any]:
        """Комплексный поиск информации по email"""
        queries = self.create_search_queries_for_email(email)
        
        all_results = []
        search_stats = {
            'total_queries': len(queries),
            'successful_queries': 0,
            'total_results': 0,
            'unique_urls': 0,
            'search_engines_used': list(self.search_engines.keys()),
            'start_time': datetime.now().isoformat()
        }
        
        for query in queries:
            try:
                results = await self.search_all_engines(query)
                if results:
                    search_stats['successful_queries'] += 1
                    all_results.extend(results)
                    
                # Добавляем задержку между запросами
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in comprehensive search for query '{query}': {str(e)}")
                
        # Обработка и фильтрация результатов
        unique_results = []
        seen_urls = set()
        
        for result in sorted(all_results, key=lambda x: x.relevance_score, reverse=True):
            if result.url not in seen_urls and self._is_relevant_result(result, email):
                unique_results.append(result)
                seen_urls.add(result.url)
                
        search_stats['end_time'] = datetime.now().isoformat()
        search_stats['total_results'] = len(all_results)
        search_stats['unique_urls'] = len(unique_results)
        
        return {
            'email': email,
            'search_results': unique_results[:self.config.max_results],
            'statistics': search_stats,
            'queries_used': queries
        }
        
    def _is_relevant_result(self, result: SearchResult, email: str) -> bool:
        """Проверка релевантности результата для email"""
        text = (result.title + ' ' + result.snippet).lower()
        email_lower = email.lower()
        username = email.split('@')[0].lower()
        
        # Проверяем наличие email или username
        if email_lower in text or username in text:
            return True
            
        # Проверяем наличие профилей в социальных сетях
        social_indicators = ['profile', 'about', 'bio', 'contact', 'linkedin', 'twitter', 'facebook']
        if any(indicator in text for indicator in social_indicators):
            return True
            
        # Исключаем нерелевантные результаты
        irrelevant_indicators = ['spam', 'scam', 'fake', 'bot', 'advertisement']
        if any(indicator in text for indicator in irrelevant_indicators):
            return False
            
        return result.relevance_score > 0.3
        
    def get_search_statistics(self) -> Dict[str, Any]:
        """Получение статистики поиска"""
        return {
            'cache_size': len(self.cache),
            'engines_configured': len(self.search_engines),
            'engines_enabled': len([e for e in self.search_engines.values() if e['enabled']]),
            'last_request_times': dict(self.last_request_time)
        }


class SearchResultProcessor:
    """Обработчик результатов поиска для извлечения дополнительной информации"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=5)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def process_search_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Обработка результатов поиска для извлечения дополнительной информации"""
        processed_results = []
        
        for result in results:
            try:
                # Извлекаем дополнительные данные с найденных страниц
                extracted_data = await self._extract_page_data(result.url)
                result.extracted_data = extracted_data
                processed_results.append(result)
                
                # Задержка между запросами
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error processing result {result.url}: {str(e)}")
                processed_results.append(result)  # Добавляем даже с ошибкой
                
        return processed_results
        
    async def _extract_page_data(self, url: str) -> Dict[str, Any]:
        """Извлечение данных со страницы"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    return {}
                    
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                data = {
                    'page_title': self._extract_page_title(soup),
                    'meta_description': self._extract_meta_description(soup),
                    'emails': self._extract_emails(soup),
                    'social_links': self._extract_social_links(soup),
                    'contact_info': self._extract_contact_info(soup)
                }
                
                return data
                
        except Exception as e:
            logger.warning(f"Error extracting data from {url}: {str(e)}")
            return {}
            
    def _extract_page_title(self, soup: BeautifulSoup) -> str:
        """Извлечение заголовка страницы"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
        
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Извлечение мета-описания"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ""
        
    def _extract_emails(self, soup: BeautifulSoup) -> List[str]:
        """Извлечение email адресов"""
        text = soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))  # Удаляем дубликаты
        
    def _extract_social_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Извлечение ссылок на социальные сети"""
        social_links = []
        social_domains = {
            'linkedin.com': 'LinkedIn',
            'twitter.com': 'Twitter', 
            'x.com': 'Twitter',
            'facebook.com': 'Facebook',
            'instagram.com': 'Instagram',
            'github.com': 'GitHub'
        }
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            for domain, platform in social_domains.items():
                if domain in href:
                    social_links.append({
                        'platform': platform,
                        'url': link.get('href'),
                        'text': link.get_text().strip()
                    })
                    break
                    
        return social_links
        
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Извлечение контактной информации"""
        text = soup.get_text()
        
        # Поиск телефонов
        phone_patterns = [
            r'\+?1?[- ]?\(?[0-9]{3}\)?[- ]?[0-9]{3}[- ]?[0-9]{4}',
            r'\+?[1-9]\d{1,3}[- ]?\(?[0-9]{1,4}\)?[- ]?[0-9]{1,4}[- ]?[0-9]{1,9}'
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
            
        return {
            'phones': list(set(phones)),
            'addresses': []  # Можно добавить извлечение адресов
        }
