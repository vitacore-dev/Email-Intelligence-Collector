import asyncio
import aiohttp
import re
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

from .email_validator import EmailValidator

logger = logging.getLogger(__name__)

class WebScraper:
    """Класс для веб-скрапинга и извлечения информации"""
    
    def __init__(self, email: str):
        self.email = email
        self.session = None
        self.visited_urls: Set[str] = set()
        self.max_depth = 2
        self.max_pages = 10
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def scrape_websites(self, urls: List[str]) -> Dict[str, Any]:
        """Скрапинг списка веб-сайтов"""
        results = {
            'person_info': {},
            'contact_info': {
                'emails': [],
                'phones': [],
                'addresses': []
            },
            'social_links': [],
            'content_analysis': {},
            'sources': []
        }
        
        for url in urls[:self.max_pages]:
            if url in self.visited_urls:
                continue
            
            try:
                page_data = await self._scrape_single_page(url)
                if page_data:
                    self._merge_page_data(results, page_data)
                    results['sources'].append(url)
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue
        
        return results
    
    async def _scrape_single_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Скрапинг одной страницы"""
        try:
            self.visited_urls.add(url)
            
            async with self.session.get(url, headers=self.headers, timeout=30) as response:
                if response.status != 200:
                    return None
                
                content_type = response.headers.get('content-type', '')
                if 'text/html' not in content_type:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                page_data = {
                    'url': url,
                    'title': self._extract_title(soup),
                    'person_info': self._extract_person_info(soup),
                    'contact_info': self._extract_contact_info(soup),
                    'social_links': self._extract_social_links(soup),
                    'meta_info': self._extract_meta_info(soup),
                    'content_keywords': self._extract_keywords(soup)
                }
                
                return page_data
                
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлечение заголовка страницы"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None
    
    def _extract_person_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Извлечение персональной информации"""
        person_info = {}
        
        # Поиск имени в различных местах
        name_selectors = [
            'h1', '.name', '#name', '.author', '.profile-name',
            '[itemprop="name"]', '.full-name', '.display-name'
        ]
        
        for selector in name_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if self._is_likely_name(text):
                    person_info['name'] = text
                    break
            if person_info.get('name'):
                break
        
        # Поиск должности/профессии
        job_selectors = [
            '.job-title', '.position', '.title', '[itemprop="jobTitle"]',
            '.occupation', '.role'
        ]
        
        for selector in job_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if text and len(text) < 100:  # Разумная длина для должности
                    person_info['occupation'] = text
                    break
            if person_info.get('occupation'):
                break
        
        # Поиск компании
        company_selectors = [
            '.company', '[itemprop="worksFor"]', '.organization',
            '.employer', '.workplace'
        ]
        
        for selector in company_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if text and len(text) < 100:
                    person_info['company'] = text
                    break
            if person_info.get('company'):
                break
        
        # Поиск местоположения
        location_selectors = [
            '.location', '[itemprop="address"]', '.address',
            '.city', '.country', '.region'
        ]
        
        for selector in location_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if text and len(text) < 100:
                    person_info['location'] = text
                    break
            if person_info.get('location'):
                break
        
        return person_info
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Извлечение контактной информации"""
        contact_info = {
            'emails': [],
            'phones': [],
            'addresses': []
        }
        
        # Получение всего текста страницы
        page_text = soup.get_text()
        
        # Поиск email-адресов
        emails = EmailValidator.extract_emails_from_text(page_text)
        contact_info['emails'] = emails
        
        # Поиск телефонных номеров
        phone_patterns = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US format
            r'\+?[1-9]\d{1,14}',  # International format
            r'\(\d{3}\)\s?\d{3}-\d{4}',  # (123) 456-7890
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, page_text)
            for phone in phones:
                cleaned_phone = re.sub(r'[^\d+]', '', phone)
                if len(cleaned_phone) >= 10:
                    contact_info['phones'].append(phone.strip())
        
        # Удаление дубликатов
        contact_info['phones'] = list(set(contact_info['phones']))
        
        return contact_info
    
    def _extract_social_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Извлечение ссылок на социальные сети"""
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
            'whatsapp.com': 'WhatsApp'
        }
        
        # Поиск ссылок
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            for domain, platform in social_domains.items():
                if domain in href.lower():
                    social_links.append({
                        'platform': platform,
                        'url': href,
                        'text': link.get_text().strip()
                    })
                    break
        
        return social_links
    
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
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Извлечение ключевых слов из содержимого"""
        # Удаление скриптов и стилей
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        
        # Простое извлечение ключевых слов
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Подсчет частоты и возврат топ-20
        from collections import Counter
        word_freq = Counter(words)
        
        # Исключение стоп-слов
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'between',
            'among', 'this', 'that', 'these', 'those', 'are', 'was',
            'were', 'been', 'have', 'has', 'had', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can'
        }
        
        filtered_words = {word: count for word, count in word_freq.items() 
                         if word not in stop_words and count > 1}
        
        return [word for word, _ in Counter(filtered_words).most_common(20)]
    
    def _is_likely_name(self, text: str) -> bool:
        """Проверка, является ли текст именем человека"""
        if not text or len(text) > 50:
            return False
        
        # Простые эвристики для определения имени
        words = text.split()
        if len(words) < 2 or len(words) > 4:
            return False
        
        # Проверка, что слова начинаются с заглавной буквы
        if not all(word[0].isupper() for word in words):
            return False
        
        # Проверка на наличие только букв и пробелов
        if not re.match(r'^[a-zA-Z\s]+$', text):
            return False
        
        return True
    
    def _merge_page_data(self, results: Dict[str, Any], page_data: Dict[str, Any]):
        """Объединение данных со страницы с общими результатами"""
        # Объединение персональной информации
        for key, value in page_data.get('person_info', {}).items():
            if value and not results['person_info'].get(key):
                results['person_info'][key] = value
        
        # Объединение контактной информации
        for key, values in page_data.get('contact_info', {}).items():
            if key in results['contact_info']:
                results['contact_info'][key].extend(values)
                results['contact_info'][key] = list(set(results['contact_info'][key]))
        
        # Добавление социальных ссылок
        for social_link in page_data.get('social_links', []):
            if not any(link['url'] == social_link['url'] for link in results['social_links']):
                results['social_links'].append(social_link)
        
        # Объединение анализа контента
        if 'content_analysis' not in results:
            results['content_analysis'] = {}
        
        results['content_analysis'][page_data['url']] = {
            'title': page_data.get('title'),
            'keywords': page_data.get('content_keywords', []),
            'meta_info': page_data.get('meta_info', {})
        }

