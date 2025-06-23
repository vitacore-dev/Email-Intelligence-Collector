import asyncio
import aiohttp
import re
import json
from typing import Dict, List, Optional, Any
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

class BaseCollector:
    """Базовый класс для всех коллекторов"""
    
    def __init__(self, email: str):
        self.email = email
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Абстрактный метод для сбора данных"""
        raise NotImplementedError
    
    async def _get_page(self, url: str, **kwargs) -> Optional[str]:
        """Безопасное получение страницы"""
        try:
            async with self.session.get(url, headers=self.headers, **kwargs) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

class GoogleSearchCollector(BaseCollector):
    """Коллектор для поиска через Google"""
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Поиск информации через Google"""
        results = {
            'person_info': {},
            'social_profiles': [],
            'websites': [],
            'sources': ['Google Search']
        }
        
        try:
            # Поиск по email
            search_query = f'"{self.email}"'
            search_url = f"https://www.google.com/search?q={quote(search_query)}"
            
            html = await self._get_page(search_url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Извлечение результатов поиска
            search_results = soup.find_all('div', class_='g')
            
            for result in search_results[:10]:  # Первые 10 результатов
                try:
                    link_elem = result.find('a')
                    if link_elem and link_elem.get('href'):
                        url = link_elem['href']
                        
                        # Проверка на социальные сети
                        social_profile = self._extract_social_profile(url)
                        if social_profile:
                            results['social_profiles'].append(social_profile)
                        
                        # Добавление в список сайтов
                        if self._is_relevant_website(url):
                            results['websites'].append(url)
                
                except Exception as e:
                    logger.error(f"Error processing search result: {e}")
                    continue
            
            # Поиск имени в результатах
            name = self._extract_name_from_search(soup)
            if name:
                results['person_info']['name'] = name
            
            return results if results['social_profiles'] or results['websites'] else None
            
        except Exception as e:
            logger.error(f"Error in Google search for {self.email}: {e}")
            return None
    
    def _extract_social_profile(self, url: str) -> Optional[Dict[str, Any]]:
        """Извлечение информации о социальном профиле из URL"""
        social_patterns = {
            'linkedin.com': 'LinkedIn',
            'twitter.com': 'Twitter',
            'x.com': 'Twitter',
            'facebook.com': 'Facebook',
            'instagram.com': 'Instagram',
            'github.com': 'GitHub',
            'youtube.com': 'YouTube',
            'tiktok.com': 'TikTok'
        }
        
        for domain, platform in social_patterns.items():
            if domain in url.lower():
                return {
                    'platform': platform,
                    'url': url,
                    'username': self._extract_username_from_url(url, platform)
                }
        
        return None
    
    def _extract_username_from_url(self, url: str, platform: str) -> Optional[str]:
        """Извлечение имени пользователя из URL"""
        try:
            if platform == 'LinkedIn':
                match = re.search(r'/in/([^/?]+)', url)
            elif platform in ['Twitter', 'Instagram', 'TikTok']:
                match = re.search(r'/([^/?]+)/?$', url)
            elif platform == 'GitHub':
                match = re.search(r'/([^/?]+)/?$', url)
            else:
                match = re.search(r'/([^/?]+)', url)
            
            return match.group(1) if match else None
        except:
            return None
    
    def _is_relevant_website(self, url: str) -> bool:
        """Проверка релевантности сайта"""
        irrelevant_domains = [
            'google.com', 'facebook.com', 'twitter.com', 'linkedin.com',
            'instagram.com', 'youtube.com', 'tiktok.com'
        ]
        
        return not any(domain in url.lower() for domain in irrelevant_domains)
    
    def _extract_name_from_search(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлечение имени из результатов поиска"""
        # Поиск в заголовках и описаниях
        text_elements = soup.find_all(['h3', 'span', 'div'])
        
        for elem in text_elements:
            text = elem.get_text()
            # Простой паттерн для поиска имен
            name_match = re.search(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', text)
            if name_match:
                return name_match.group(1)
        
        return None

class LinkedInCollector(BaseCollector):
    """Коллектор для LinkedIn"""
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Поиск профиля в LinkedIn"""
        # В реальной реализации здесь был бы API LinkedIn или парсинг
        # Для демонстрации возвращаем заглушку
        logger.info(f"LinkedIn search for {self.email} (mock implementation)")
        
        return {
            'person_info': {},
            'social_profiles': [],
            'sources': ['LinkedIn']
        }

class TwitterCollector(BaseCollector):
    """Коллектор для Twitter/X"""
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Поиск профиля в Twitter"""
        logger.info(f"Twitter search for {self.email} (mock implementation)")
        
        return {
            'person_info': {},
            'social_profiles': [],
            'sources': ['Twitter']
        }

class GitHubCollector(BaseCollector):
    """Коллектор для GitHub"""
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Поиск профиля в GitHub"""
        results = {
            'person_info': {},
            'social_profiles': [],
            'websites': [],
            'sources': ['GitHub']
        }
        
        try:
            # GitHub API поиск по email
            if settings.GITHUB_API_KEY:
                api_url = f"https://api.github.com/search/users?q={self.email}"
                headers = {
                    **self.headers,
                    'Authorization': f'token {settings.GITHUB_API_KEY}'
                }
                
                html = await self._get_page(api_url, headers=headers)
                if html:
                    data = json.loads(html)
                    
                    if data.get('items'):
                        user = data['items'][0]
                        results['social_profiles'].append({
                            'platform': 'GitHub',
                            'url': user['html_url'],
                            'username': user['login'],
                            'avatar_url': user.get('avatar_url')
                        })
                        
                        # Получение дополнительной информации о пользователе
                        user_info = await self._get_github_user_info(user['login'])
                        if user_info:
                            results['person_info'].update(user_info)
            
            return results if results['social_profiles'] else None
            
        except Exception as e:
            logger.error(f"Error in GitHub search for {self.email}: {e}")
            return None
    
    async def _get_github_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Получение дополнительной информации о пользователе GitHub"""
        try:
            api_url = f"https://api.github.com/users/{username}"
            headers = {}
            
            if settings.GITHUB_API_KEY:
                headers['Authorization'] = f'token {settings.GITHUB_API_KEY}'
            
            html = await self._get_page(api_url, headers=headers)
            if html:
                data = json.loads(html)
                
                user_info = {}
                if data.get('name'):
                    user_info['name'] = data['name']
                if data.get('location'):
                    user_info['location'] = data['location']
                if data.get('company'):
                    user_info['company'] = data['company']
                if data.get('bio'):
                    user_info['bio'] = data['bio']
                
                return user_info
        
        except Exception as e:
            logger.error(f"Error getting GitHub user info for {username}: {e}")
        
        return None

class FacebookCollector(BaseCollector):
    """Коллектор для Facebook"""
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Поиск профиля в Facebook"""
        logger.info(f"Facebook search for {self.email} (mock implementation)")
        
        return {
            'person_info': {},
            'social_profiles': [],
            'sources': ['Facebook']
        }

