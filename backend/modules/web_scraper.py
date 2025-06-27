import asyncio
import aiohttp
import re
import json
import time
from typing import Dict, List, Optional, Any, Set, Union, Callable
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import hashlib
from concurrent.futures import ThreadPoolExecutor
# Опциональные импорты для NLP
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TextBlob = None
    TEXTBLOB_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    from nltk.tree import Tree
    NLTK_AVAILABLE = True
except ImportError:
    nltk = None
    stopwords = None
    word_tokenize = None
    sent_tokenize = None
    pos_tag = None
    ne_chunk = None
    Tree = None
    NLTK_AVAILABLE = False

try:
    from .email_validator import EmailValidator
except ImportError:
    try:
        from email_validator import EmailValidator
    except ImportError:
        # Создаем заглушку для EmailValidator если модуль недоступен
        class EmailValidator:
            @staticmethod
            def extract_emails_from_text(text):
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                return re.findall(email_pattern, text)

logger = logging.getLogger(__name__)

# Инициализация NLTK (если не загружены)
if NLTK_AVAILABLE:
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt')
        except:
            logger.warning("Could not download NLTK punkt data")
        
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords')
        except:
            logger.warning("Could not download NLTK stopwords data")
        
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        try:
            nltk.download('averaged_perceptron_tagger')
        except:
            logger.warning("Could not download NLTK POS tagger data")
        
    try:
        nltk.data.find('chunkers/maxent_ne_chunker')
    except LookupError:
        try:
            nltk.download('maxent_ne_chunker')
        except:
            logger.warning("Could not download NLTK NE chunker data")
        
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        try:
            nltk.download('words')
        except:
            logger.warning("Could not download NLTK words data")

# Загрузка spaCy модели (если доступна)
if SPACY_AVAILABLE:
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("spaCy english model not found. Install with: python -m spacy download en_core_web_sm")
        nlp = None
else:
    nlp = None

@dataclass
class ScrapingConfig:
    """Конфигурация для веб-скрапинга"""
    max_pages: int = 10
    max_depth: int = 2
    timeout: int = 30
    concurrent_requests: int = 5
    retry_attempts: int = 3
    retry_delay: float = 1.0
    cache_ttl: int = 3600  # секунды
    respect_robots_txt: bool = True
    delay_between_requests: float = 1.0
    
@dataclass
class SelectorConfig:
    """Конфигурация селекторов для различных типов сайтов"""
    name_selectors: List[str] = field(default_factory=lambda: [
        'h1', '.name', '#name', '.author', '.profile-name',
        '[itemprop="name"]', '.full-name', '.display-name',
        '.person-name', '.user-name', '.contact-name'
    ])
    
    job_selectors: List[str] = field(default_factory=lambda: [
        '.job-title', '.position', '.title', '[itemprop="jobTitle"]',
        '.occupation', '.role', '.profession', '.designation'
    ])
    
    company_selectors: List[str] = field(default_factory=lambda: [
        '.company', '[itemprop="worksFor"]', '.organization',
        '.employer', '.workplace', '.org', '.company-name'
    ])
    
    location_selectors: List[str] = field(default_factory=lambda: [
        '.location', '[itemprop="address"]', '.address',
        '.city', '.country', '.region', '.locality'
    ])
    
    # Специализированные селекторы для популярных платформ
    platform_selectors: Dict[str, Dict[str, List[str]]] = field(default_factory=lambda: {
        'linkedin.com': {
            'name': ['.text-heading-xlarge', '.pv-text-details__left-panel h1'],
            'job': ['.text-body-medium.break-words'],
            'company': ['.pv-text-details__right-panel .text-body-small'],
            'location': ['.text-body-small.inline.t-black--light']
        },
        'twitter.com': {
            'name': ['[data-testid="UserName"]', '.css-901oao.css-16my406'],
            'bio': ['[data-testid="UserDescription"]']
        },
        'github.com': {
            'name': ['.p-name.vcard-fullname'],
            'company': ['.p-org'],
            'location': ['.p-label']
        }
    })

class ErrorTracker:
    """Отслеживание и анализ ошибок скрапинга"""
    
    def __init__(self):
        self.errors: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.error_counts: Counter = Counter()
        
    def log_error(self, url: str, error_type: str, error_message: str, 
                  context: Optional[Dict[str, Any]] = None):
        """Логирование ошибки"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_message,
            'context': context or {}
        }
        
        self.errors[url].append(error_data)
        self.error_counts[error_type] += 1
        logger.error(f"Error in {url}: {error_type} - {error_message}")
        
    def get_error_summary(self) -> Dict[str, Any]:
        """Получение сводки ошибок"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_types': dict(self.error_counts),
            'affected_urls': len(self.errors),
            'most_common_errors': self.error_counts.most_common(5)
        }

class RateLimiter:
    """Адаптивное ограничение скорости запросов"""
    
    def __init__(self, initial_delay: float = 1.0):
        self.delays: Dict[str, float] = defaultdict(lambda: initial_delay)
        self.last_request: Dict[str, datetime] = {}
        self.failure_counts: Dict[str, int] = defaultdict(int)
        
    async def wait_if_needed(self, domain: str):
        """Ожидание перед запросом к домену"""
        now = datetime.now()
        
        if domain in self.last_request:
            time_since_last = (now - self.last_request[domain]).total_seconds()
            delay_needed = self.delays[domain] - time_since_last
            
            if delay_needed > 0:
                await asyncio.sleep(delay_needed)
        
        self.last_request[domain] = datetime.now()
        
    def adjust_delay(self, domain: str, success: bool):
        """Адаптивная корректировка задержки"""
        if success:
            # Уменьшаем задержку при успехе
            self.delays[domain] = max(0.5, self.delays[domain] * 0.9)
            self.failure_counts[domain] = 0
        else:
            # Увеличиваем задержку при неудаче
            self.failure_counts[domain] += 1
            self.delays[domain] = min(10.0, self.delays[domain] * 1.5)

class NLPProcessor:
    """Обработка текста с использованием NLP"""
    
    def __init__(self):
        if NLTK_AVAILABLE and stopwords:
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = {
                    'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
                    'during', 'before', 'after', 'above', 'below', 'between',
                    'among', 'this', 'that', 'these', 'those', 'are', 'was',
                    'were', 'been', 'have', 'has', 'had', 'will', 'would',
                    'could', 'should', 'may', 'might', 'must', 'can'
                }
        else:
            self.stop_words = {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
                'during', 'before', 'after', 'above', 'below', 'between',
                'among', 'this', 'that', 'these', 'those', 'are', 'was',
                'were', 'been', 'have', 'has', 'had', 'will', 'would',
                'could', 'should', 'may', 'might', 'must', 'can'
            }
        
    def extract_entities_spacy(self, text: str) -> Dict[str, List[str]]:
        """Извлечение именованных сущностей с помощью spaCy"""
        if not nlp:
            return {}
            
        doc = nlp(text)
        entities = defaultdict(list)
        
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)
            
        return dict(entities)
        
    def extract_entities_nltk(self, text: str) -> Dict[str, List[str]]:
        """Извлечение именованных сущностей с помощью NLTK"""
        if not NLTK_AVAILABLE or not word_tokenize or not pos_tag or not ne_chunk:
            return {}
            
        try:
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            chunks = ne_chunk(pos_tags)
            
            entities = defaultdict(list)
            
            for chunk in chunks:
                if isinstance(chunk, Tree):
                    entity_text = ' '.join([token for token, pos in chunk.leaves()])
                    entities[chunk.label()].append(entity_text)
                    
            return dict(entities)
        except Exception as e:
            logger.error(f"NLTK entity extraction error: {e}")
            return {}
            
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Анализ тональности текста"""
        if not TEXTBLOB_AVAILABLE or not TextBlob:
            return {'polarity': 0.0, 'subjectivity': 0.0}
            
        try:
            blob = TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0}
            
    def extract_keywords_advanced(self, text: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Продвинутое извлечение ключевых слов"""
        if not NLTK_AVAILABLE or not word_tokenize or not pos_tag:
            # Fallback к простому извлечению ключевых слов
            return self._extract_keywords_simple(text, top_k)
            
        try:
            # Токенизация и фильтрация
            tokens = word_tokenize(text.lower())
            pos_tags = pos_tag(tokens)
            
            # Оставляем только существительные, прилагательные и глаголы
            relevant_pos = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
            filtered_words = [
                word for word, pos in pos_tags 
                if word.isalpha() and len(word) > 2 and word not in self.stop_words 
                and pos in relevant_pos
            ]
            
            # Подсчет частоты с учетом POS-тегов
            word_freq = Counter(filtered_words)
            
            # Возврат топ-K слов с дополнительной информацией
            keywords = []
            for word, freq in word_freq.most_common(top_k):
                # Получаем POS-теги для каждого слова
                word_pos = [pos for w, pos in pos_tags if w == word]
                keywords.append({
                    'word': word,
                    'frequency': freq,
                    'pos_tags': list(set(word_pos))
                })
                
            return keywords
        except Exception as e:
            logger.error(f"Advanced keyword extraction error: {e}")
            return self._extract_keywords_simple(text, top_k)
            
    def _extract_keywords_simple(self, text: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Простое извлечение ключевых слов без NLTK"""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        filtered_words = [word for word in words if word not in self.stop_words]
        word_freq = Counter(filtered_words)
        
        keywords = []
        for word, freq in word_freq.most_common(top_k):
            keywords.append({
                'word': word,
                'frequency': freq,
                'pos_tags': ['UNKNOWN']  # Без NLTK не можем определить POS
            })
            
        return keywords
            
    def extract_person_info_nlp(self, text: str) -> Dict[str, Any]:
        """Извлечение информации о человеке с помощью NLP"""
        info = {}
        
        # Извлечение сущностей
        spacy_entities = self.extract_entities_spacy(text)
        nltk_entities = self.extract_entities_nltk(text)
        
        # Объединение результатов
        all_entities = {}
        for entities_dict in [spacy_entities, nltk_entities]:
            for entity_type, entity_list in entities_dict.items():
                if entity_type not in all_entities:
                    all_entities[entity_type] = []
                all_entities[entity_type].extend(entity_list)
        
        # Извлечение имен (PERSON entities)
        if 'PERSON' in all_entities:
            info['names'] = list(set(all_entities['PERSON']))
        
        # Извлечение организаций
        if 'ORG' in all_entities or 'ORGANIZATION' in all_entities:
            orgs = all_entities.get('ORG', []) + all_entities.get('ORGANIZATION', [])
            info['organizations'] = list(set(orgs))
            
        # Извлечение местоположений
        if 'GPE' in all_entities or 'LOCATION' in all_entities:
            locations = all_entities.get('GPE', []) + all_entities.get('LOCATION', [])
            info['locations'] = list(set(locations))
            
        return info

class EnhancedWebScraper:
    """Улучшенный класс для веб-скрапинга с NLP и адаптивными селекторами"""
    
    def __init__(self, email: str, config: Optional[ScrapingConfig] = None, 
                 selector_config: Optional[SelectorConfig] = None):
        self.email = email
        self.config = config or ScrapingConfig()
        self.selector_config = selector_config or SelectorConfig()
        
        self.session = None
        self.visited_urls: Set[str] = set()
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        # Компоненты для улучшенной функциональности
        self.error_tracker = ErrorTracker()
        self.rate_limiter = RateLimiter(self.config.delay_between_requests)
        self.nlp_processor = NLPProcessor()
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    async def __aenter__(self):
        """Асинхронный менеджер контекста"""
        connector = aiohttp.TCPConnector(limit=self.config.concurrent_requests)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout,
            headers=self.headers
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            
    def _get_cache_key(self, url: str) -> str:
        """Генерация ключа кеша"""
        return hashlib.md5(url.encode()).hexdigest()
        
    def _is_cache_valid(self, cache_data: Dict[str, Any]) -> bool:
        """Проверка актуальности кеша"""
        cached_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
        return (datetime.now() - cached_time).total_seconds() < self.config.cache_ttl
        
    def _get_platform_selectors(self, url: str) -> Dict[str, List[str]]:
        """Получение специализированных селекторов для платформы"""
        domain = urlparse(url).netloc.lower()
        
        for platform_domain, selectors in self.selector_config.platform_selectors.items():
            if platform_domain in domain:
                return selectors
                
        # Возвращаем стандартные селекторы
        return {
            'name': self.selector_config.name_selectors,
            'job': self.selector_config.job_selectors,
            'company': self.selector_config.company_selectors,
            'location': self.selector_config.location_selectors
        }
        
    async def scrape_websites_enhanced(self, urls: List[str]) -> Dict[str, Any]:
        """Улучшенный скрапинг с NLP, кешированием и адаптивными селекторами"""
        results = {
            'person_info': {},
            'contact_info': {
                'emails': [],
                'phones': [],
                'addresses': []
            },
            'social_links': [],
            'content_analysis': {},
            'nlp_analysis': {},
            'sources': [],
            'errors': [],
            'performance_stats': {
                'total_urls': len(urls),
                'successful_scrapes': 0,
                'failed_scrapes': 0,
                'cache_hits': 0,
                'start_time': datetime.now().isoformat()
            }
        }
        
        urls_to_process = urls[:self.config.max_pages]
        semaphore = asyncio.Semaphore(self.config.concurrent_requests)
        tasks = []
        for url in urls_to_process:
            task = self._scrape_single_page_enhanced(url, semaphore)
            tasks.append(task)
        
        page_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, page_result in enumerate(page_results):
            url = urls_to_process[i]
            
            if isinstance(page_result, Exception):
                self.error_tracker.log_error(url, "scraping_exception", str(page_result))
                results['performance_stats']['failed_scrapes'] += 1
                continue
                
            if page_result:
                self._merge_page_data_enhanced(results, page_result)
                results['sources'].append(url)
                results['performance_stats']['successful_scrapes'] += 1
            else:
                results['performance_stats']['failed_scrapes'] += 1
        
        results['performance_stats']['end_time'] = datetime.now().isoformat()
        results['performance_stats']['duration'] = (
            datetime.fromisoformat(results['performance_stats']['end_time']) -
            datetime.fromisoformat(results['performance_stats']['start_time'])
        ).total_seconds()
        
        results['errors'] = self.error_tracker.get_error_summary()
        
        return results
        
    async def _scrape_single_page_enhanced(self, url: str, semaphore: asyncio.Semaphore) -> Optional[Dict[str, Any]]:
        """Улучшенный скрапинг одной страницы с кешированием и обработкой ошибок"""
        async with semaphore:
            try:
                cache_key = self._get_cache_key(url)
                if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
                    logger.info(f"Cache hit for {url}")
                    return self.cache[cache_key]['data']
                
                domain = urlparse(url).netloc
                await self.rate_limiter.wait_if_needed(domain)
                
                for attempt in range(self.config.retry_attempts):
                    try:
                        page_data = await self._fetch_and_parse_page(url)
                        if page_data:
                            self.cache[cache_key] = {
                                'data': page_data,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            self.rate_limiter.adjust_delay(domain, True)
                            return page_data
                        
                    except aiohttp.ClientError as e:
                        self.error_tracker.log_error(url, "client_error", str(e), {'attempt': attempt + 1})
                        
                        if attempt < self.config.retry_attempts - 1:
                            await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                        
                    except Exception as e:
                        self.error_tracker.log_error(url, "unexpected_error", str(e),{'attempt': attempt + 1})
                        break
                
                self.rate_limiter.adjust_delay(domain, False)
                return None
                
            except Exception as e:
                self.error_tracker.log_error(url, "general_error", str(e))
                return None
    
    async def _fetch_and_parse_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Получение и парсинг страницы"""
        self.visited_urls.add(url)
        
        async with self.session.get(url, headers=self.headers) as response:
            if response.status != 200:
                self.error_tracker.log_error(url, "http_error", f"Status {response.status}")
                return None
            
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                self.error_tracker.log_error(url, "content_type_error", f"Unexpected content type: {content_type}")
                return None
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            platform_selectors = self._get_platform_selectors(url)
            
            page_data = {
                'url': url,
                'title': self._extract_title(soup),
                'person_info': self._extract_person_info_enhanced(soup, platform_selectors),
                'contact_info': self._extract_contact_info_enhanced(soup),
                'social_links': self._extract_social_links_enhanced(soup),
                'meta_info': self._extract_meta_info(soup),
                'content_keywords': self._extract_keywords_enhanced(soup),
                'nlp_analysis': self._perform_nlp_analysis(soup)
            }
            
            return page_data
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлечение заголовка страницы"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None
        
    def _extract_meta_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Извлечение мета-информации"""
        meta_info = {}
        
        # Open Graph теги
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                meta_info[f'og_{property_name}'] = content
        
        # Twitter Card теги
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                meta_info[f'twitter_{name}'] = content
        
        # Стандартные мета-теги
        standard_tags = ['description', 'keywords', 'author']
        for tag_name in standard_tags:
            tag = soup.find('meta', attrs={'name': tag_name})
            if tag and tag.get('content'):
                meta_info[tag_name] = tag['content']
        
        return meta_info
    
    def _extract_person_info_enhanced(self, soup: BeautifulSoup, platform_selectors: Dict[str, List[str]]) -> Dict[str, Any]:
        """Улучшенное извлечение персональной информации с учетом платформы"""
        person_info = {}
        
        for info_type, selectors in platform_selectors.items():
            for selector in selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text().strip()
                    if text and len(text) < 200:
                        if info_type == 'name' and self._is_likely_name_enhanced(text):
                            person_info['name'] = text
                            break
                        elif info_type in ['job', 'occupation'] and text:
                            person_info['occupation'] = text
                            break
                        elif info_type == 'company' and text:
                            person_info['company'] = text
                            break
                        elif info_type == 'location' and text:
                            person_info['location'] = text
                            break
                
                if person_info.get(info_type):
                    break
        
        page_text = soup.get_text()
        nlp_info = self.nlp_processor.extract_person_info_nlp(page_text)
        
        if not person_info.get('name') and nlp_info.get('names'):
            for name in nlp_info['names']:
                if self._is_likely_name_enhanced(name):
                    person_info['name'] = name
                    break
        
        if not person_info.get('company') and nlp_info.get('organizations'):
            person_info['company'] = nlp_info['organizations'][0]
            
        if not person_info.get('location') and nlp_info.get('locations'):
            person_info['location'] = nlp_info['locations'][0]
        
        return person_info
        
    def _extract_contact_info_enhanced(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Улучшенное извлечение контактной информации"""
        contact_info = {
            'emails': [],
            'phones': [],
            'addresses': []
        }
        
        page_text = soup.get_text()
        
        phone_patterns = [
            r'\+?1?[\s.-]?\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}',
            r'\+?[1-9]\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}',
            r'\(\d{3}\)\s?\d{3}[\s.-]?\d{4}',
            r'\d{3}[\s.-]?\d{3}[\s.-]?\d{4}',
        ]
        
        try:
            emails = EmailValidator.extract_emails_from_text(page_text)
            contact_info['emails'] = list(set(emails))
        except Exception as e:
            self.error_tracker.log_error(soup.find('title', default='unknown').get_text() if soup.find('title') else 'unknown','email_extraction_error', str(e))
        
        all_phones = []
        for pattern in phone_patterns:
            phones = re.findall(pattern, page_text)
            all_phones.extend(phones)
        
        cleaned_phones = []
        for phone in all_phones:
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            if 10 <= len(cleaned_phone) <= 15:
                cleaned_phones.append(phone.strip())
        
        contact_info['phones'] = list(set(cleaned_phones))
        
        address_patterns = [
            r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct)\s*,?\s*[A-Za-z\s]*\d{5}',
        ]
        
        for pattern in address_patterns:
            addresses = re.findall(pattern, page_text, re.IGNORECASE)
            contact_info['addresses'].extend(addresses)
        
        contact_info['addresses'] = list(set(contact_info['addresses']))
        
        return contact_info
        
    def _extract_social_links_enhanced(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Улучшенное извлечение ссылок на социальные сети"""
        social_links = []
        
        social_domains = {
            'linkedin.com': 'LinkedIn',
            'twitter.com': 'Twitter',
            'x.com': 'Twitter',
            'facebook.com': 'Facebook',
            'instagram.com': 'Instagram',
            'github.com': 'GitHub',
            'youtube.com': 'YouTube',
            'tiktok.com': 'TikTok',
            'telegram.org': 'Telegram',
            'telegram.me': 'Telegram',
            'whatsapp.com': 'WhatsApp',
            'snapchat.com': 'Snapchat',
            'reddit.com': 'Reddit',
            'medium.com': 'Medium',
            'behance.net': 'Behance',
            'dribbble.com': 'Dribbble',
            'vimeo.com': 'Vimeo',
            'soundcloud.com': 'SoundCloud'
        }
        
        link_sources = [
            soup.find_all('a', href=True),
            soup.find_all('link', href=True),
            soup.find_all('[data-url]'),
        ]
        
        found_urls = set()
        
        for source in link_sources:
            for link in source:
                href = link.get('href') or link.get('data-url')
                if not href:
                    continue
                    
                href = href.lower()
                
                for domain, platform in social_domains.items():
                    if domain in href and href not in found_urls:
                        social_links.append({
                            'platform': platform,
                            'url': href,
                            'text': link.get_text().strip() if hasattr(link, 'get_text') else '',
                            'context': self._get_link_context(link)
                        })
                        found_urls.add(href)
                        break
        
        return social_links
        
    def _extract_keywords_enhanced(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Улучшенное извлечение ключевых слов с помощью NLP"""
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        text = soup.get_text()
        
        return self.nlp_processor.extract_keywords_advanced(text)
        
    def _perform_nlp_analysis(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Выполнение NLP анализа страницы"""
        text = soup.get_text()
        
        if len(text) > 10000:
            text = text[:10000]
        
        analysis = {
            'sentiment': self.nlp_processor.analyze_sentiment(text),
            'entities_spacy': self.nlp_processor.extract_entities_spacy(text),
            'entities_nltk': self.nlp_processor.extract_entities_nltk(text),
            'text_length': len(text),
            'language_detected': self._detect_language(text)
        }
        
        return analysis
        
    def _is_likely_name_enhanced(self, text: str) -> bool:
        """Улучшенная проверка имени с дополнительными эвристиками"""
        if not text or len(text) > 100:
            return False
        
        text = text.strip()
        words = text.split()
        
        if len(words) < 1 or len(words) > 5:
            return False
        
        if not re.match(r'^[a-zA-Z\s\'\-\.]+$', text):
            return False
        
        if not all(word[0].isupper() or word.startswith("'") for word in words):
            return False
        
        exclude_patterns = [
            r'\b(?:page|home|about|contact|login|register|search)\b',
            r'\b(?:company|corporation|inc|ltd|llc)\b',
            r'\b(?:email|phone|address|website)\b'
        ]
        
        text_lower = text.lower()
        for pattern in exclude_patterns:
            if re.search(pattern, text_lower):
                return False
        
        return True
        
    def _get_link_context(self, link) -> str:
        """Получение контекста ссылки"""
        try:
            parent = link.parent if hasattr(link, 'parent') else None
            if parent:
                return parent.get_text().strip()[:100]
        except:
            pass
        return ''
        
    def _detect_language(self, text: str) -> str:
        """Базовое определение языка"""
        if not TEXTBLOB_AVAILABLE or not TextBlob:
            return 'unknown'
            
        try:
            blob = TextBlob(text)
            return blob.detect_language()
        except:
            return 'unknown'
            
    def _merge_page_data_enhanced(self, results: Dict[str, Any], page_data: Dict[str, Any]):
        """Улучшенное объединение данных страницы"""
        for key, value in page_data.get('person_info', {}).items():
            if value and (not results['person_info'].get(key) or len(str(value)) > len(str(results['person_info'].get(key, '')))):
                results['person_info'][key] = value
        
        for key, values in page_data.get('contact_info', {}).items():
            if key in results['contact_info']:
                combined = results['contact_info'][key] + values
                results['contact_info'][key] = list(dict.fromkeys(combined))
        
        for social_link in page_data.get('social_links', []):
            if not any(existing['url'] == social_link['url'] for existing in results['social_links']):
                results['social_links'].append(social_link)
        
        if 'content_analysis' not in results:
            results['content_analysis'] = {}
        
        url = page_data.get('url', 'unknown')
        results['content_analysis'][url] = {
            'title': page_data.get('title'),
            'keywords': page_data.get('content_keywords', []),
            'meta_info': page_data.get('meta_info', {})
        }
        
        if 'nlp_analysis' not in results:
            results['nlp_analysis'] = {}
        
        results['nlp_analysis'][url] = page_data.get('nlp_analysis', {})
        
    def get_scraping_stats(self) -> Dict[str, Any]:
        """Получение статистики скрапинга"""
        return {
            'visited_urls_count': len(self.visited_urls),
            'cache_size': len(self.cache),
            'error_summary': self.error_tracker.get_error_summary(),
            'rate_limiter_stats': {
                'domains': len(self.rate_limiter.delays),
                'current_delays': dict(self.rate_limiter.delays)
            }
        }

# Алиас для обратной совместимости
WebScraper = EnhancedWebScraper

# Добавляем методы для обратной совместимости
class EnhancedWebScraperCompat(EnhancedWebScraper):
    """Класс с методами для обратной совместимости"""
    
    async def scrape_websites(self, urls: List[str]) -> Dict[str, Any]:
        """Обратная совместимость для старого API"""
        return await self.scrape_websites_enhanced(urls)
        
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлечение заголовка страницы"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None
        
    def _extract_meta_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Извлечение мета-информации"""
        meta_info = {}
        
        # Open Graph теги
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                meta_info[f'og_{property_name}'] = content
        
        # Twitter Card теги
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                meta_info[f'twitter_{name}'] = content
        
        # Стандартные мета-теги
        standard_tags = ['description', 'keywords', 'author']
        for tag_name in standard_tags:
            tag = soup.find('meta', attrs={'name': tag_name})
            if tag and tag.get('content'):
                meta_info[tag_name] = tag['content']
        
        return meta_info

# Заменяем WebScraper на совместимую версию
WebScraper = EnhancedWebScraperCompat

