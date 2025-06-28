"""
Модуль для извлечения и анализа академической информации из Google поиска
Специализируется на поиске степеней, должностей, публикаций и академических профилей
"""

import asyncio
import aiohttp
import re
import json
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup
import logging
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
from collections import defaultdict, Counter

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

logger = logging.getLogger(__name__)

@dataclass
class AcademicProfile:
    """Академический профиль персоны"""
    name: Optional[str] = None
    email: str = ""
    degrees: List[Dict[str, str]] = field(default_factory=list)
    positions: List[Dict[str, str]] = field(default_factory=list)
    institutions: List[str] = field(default_factory=list)
    publications: List[Dict[str, Any]] = field(default_factory=list)
    research_areas: List[str] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    academic_ids: Dict[str, str] = field(default_factory=dict)  # ORCID, ResearcherID, etc.
    social_profiles: List[Dict[str, str]] = field(default_factory=list)
    academic_websites: List[str] = field(default_factory=list)
    courses_taught: List[str] = field(default_factory=list)
    academic_awards: List[str] = field(default_factory=list)
    conference_presentations: List[Dict[str, Any]] = field(default_factory=list)
    collaborators: List[str] = field(default_factory=list)
    academic_rank: Optional[str] = None
    h_index: Optional[int] = None
    citation_count: Optional[int] = None
    
@dataclass
class AcademicSearchResult:
    """Результат академического поиска"""
    title: str
    url: str
    snippet: str
    source: str
    rank: int
    relevance_score: float = 0.0
    academic_score: float = 0.0
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    academic_indicators: List[str] = field(default_factory=list)

class AcademicDataExtractor:
    """Извлечение академических данных из текста"""
    
    def __init__(self):
        # Паттерны для степеней
        self.degree_patterns = [
            r'\b(?:Ph\.?D\.?|PhD|Doctor of Philosophy|Doctorate)\b',
            r'\b(?:M\.?D\.?|MD|Doctor of Medicine)\b',
            r'\b(?:M\.?S\.?|MS|Master of Science)\b',
            r'\b(?:M\.?A\.?|MA|Master of Arts)\b',
            r'\b(?:M\.?B\.?A\.?|MBA|Master of Business Administration)\b',
            r'\b(?:B\.?S\.?|BS|Bachelor of Science)\b',
            r'\b(?:B\.?A\.?|BA|Bachelor of Arts)\b',
            r'\b(?:LL\.?M\.?|LLM|Master of Laws)\b',
            r'\b(?:J\.?D\.?|JD|Juris Doctor)\b',
            r'\b(?:Ed\.?D\.?|EdD|Doctor of Education)\b',
            r'\b(?:D\.?Sc\.?|DSc|Doctor of Science)\b',
            r'\b(?:Sc\.?D\.?|ScD|Doctor of Science)\b'
        ]
        
        # Паттерны для академических должностей
        self.position_patterns = [
            r'\b(?:Professor|Prof\.?)\b',
            r'\b(?:Associate Professor|Assoc\.? Prof\.?)\b',
            r'\b(?:Assistant Professor|Asst\.? Prof\.?)\b',
            r'\b(?:Adjunct Professor|Adjunct Prof\.?)\b',
            r'\b(?:Visiting Professor|Visiting Prof\.?)\b',
            r'\b(?:Professor Emeritus|Prof\.? Emeritus)\b',
            r'\b(?:Research Professor|Research Prof\.?)\b',
            r'\b(?:Clinical Professor|Clinical Prof\.?)\b',
            r'\b(?:Lecturer|Senior Lecturer)\b',
            r'\b(?:Research Scientist|Principal Research Scientist)\b',
            r'\b(?:Postdoctoral Researcher|Postdoc|Post-doc)\b',
            r'\b(?:Graduate Student|PhD Student|Doctoral Student)\b',
            r'\b(?:Research Fellow|Senior Research Fellow)\b',
            r'\b(?:Principal Investigator|PI)\b',
            r'\b(?:Department Chair|Chair|Head of Department)\b',
            r'\b(?:Dean|Vice Dean|Associate Dean)\b',
            r'\b(?:Provost|Vice Provost)\b',
            r'\b(?:Chancellor|Vice Chancellor)\b'
        ]
        
        # Паттерны для институций
        self.institution_patterns = [
            r'\b(?:University|Univ\.?)\b',
            r'\b(?:College|Coll\.?)\b',
            r'\b(?:Institute|Inst\.?)\b',
            r'\b(?:Laboratory|Lab\.?)\b',
            r'\b(?:Center|Centre)\b',
            r'\b(?:School|Academy)\b',
            r'\b(?:Hospital|Medical Center)\b',
            r'\b(?:Research Center|Research Centre)\b'
        ]
        
        # Академические платформы
        self.academic_platforms = {
            'scholar.google.com': 'Google Scholar',
            'researchgate.net': 'ResearchGate',
            'academia.edu': 'Academia.edu',
            'orcid.org': 'ORCID',
            'publons.com': 'Publons',
            'arxiv.org': 'arXiv',
            'pubmed.ncbi.nlm.nih.gov': 'PubMed',
            'ieee.org': 'IEEE Xplore',
            'acm.org': 'ACM Digital Library',
            'jstor.org': 'JSTOR',
            'scopus.com': 'Scopus',
            'mendeley.com': 'Mendeley'
        }
        
    def extract_degrees(self, text: str) -> List[Dict[str, str]]:
        """Извлечение степеней из текста"""
        degrees = []
        text_lower = text.lower()
        
        for pattern in self.degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                degree = match.group().strip()
                
                # Пытаемся найти контекст (университет, год)
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                # Поиск года
                year_match = re.search(r'\b(19|20)\d{2}\b', context)
                year = year_match.group() if year_match else None
                
                # Поиск университета
                university_patterns = [
                    r'\bat\s+([A-Z][a-zA-Z\s]+(?:University|College|Institute))',
                    r'\bfrom\s+([A-Z][a-zA-Z\s]+(?:University|College|Institute))',
                    r'([A-Z][a-zA-Z\s]+(?:University|College|Institute))'
                ]
                
                university = None
                for uni_pattern in university_patterns:
                    uni_match = re.search(uni_pattern, context)
                    if uni_match:
                        university = uni_match.group(1).strip()
                        break
                
                degrees.append({
                    'degree': degree,
                    'university': university,
                    'year': year,
                    'context': context.strip()
                })
        
        return degrees
    
    def extract_positions(self, text: str) -> List[Dict[str, str]]:
        """Извлечение академических должностей"""
        positions = []
        
        for pattern in self.position_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                position = match.group().strip()
                
                # Контекст для поиска департамента/университета
                start = max(0, match.start() - 150)
                end = min(len(text), match.end() + 150)
                context = text[start:end]
                
                # Поиск департамента
                dept_patterns = [
                    r'\bof\s+([A-Z][a-zA-Z\s]+(?:Science|Studies|Engineering|Medicine))',
                    r'\bin\s+([A-Z][a-zA-Z\s]+(?:Department|School|College))',
                    r'([A-Z][a-zA-Z\s]+(?:Department|School|College))'
                ]
                
                department = None
                for dept_pattern in dept_patterns:
                    dept_match = re.search(dept_pattern, context)
                    if dept_match:
                        department = dept_match.group(1).strip()
                        break
                
                # Поиск университета
                university = None
                for inst_pattern in self.institution_patterns:
                    inst_matches = re.finditer(r'([A-Z][a-zA-Z\s]+' + inst_pattern + r')', context)
                    for inst_match in inst_matches:
                        university = inst_match.group(1).strip()
                        break
                    if university:
                        break
                
                positions.append({
                    'position': position,
                    'department': department,
                    'university': university,
                    'context': context.strip()
                })
        
        return positions
    
    def extract_publications(self, text: str) -> List[Dict[str, Any]]:
        """Извлечение публикаций"""
        publications = []
        
        # Паттерны для названий статей
        publication_patterns = [
            r'"([^"]{20,200})"',  # Заключенные в кавычки
            r'[A-Z][a-zA-Z\s,:-]{30,200}(?:\.|$)',  # Длинные заголовки
        ]
        
        # Паттерны для журналов
        journal_patterns = [
            r'\bin\s+([A-Z][a-zA-Z\s&]+(?:Journal|Review|Proceedings|Conference))',
            r'\bpublished in\s+([A-Z][a-zA-Z\s&]+)',
            r'([A-Z][a-zA-Z\s&]+(?:Journal|Review|Proceedings|Conference))'
        ]
        
        # Поиск DOI
        doi_pattern = r'\b10\.\d{4,}/[^\s]+'
        
        for pattern in publication_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                title = match.group(1) if '"' in pattern else match.group()
                title = title.strip()
                
                if len(title) < 20 or len(title) > 300:
                    continue
                
                # Контекст для поиска дополнительной информации
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]
                
                # Поиск года
                year_match = re.search(r'\b(19|20)\d{2}\b', context)
                year = year_match.group() if year_match else None
                
                # Поиск журнала
                journal = None
                for journal_pattern in journal_patterns:
                    journal_match = re.search(journal_pattern, context)
                    if journal_match:
                        journal = journal_match.group(1).strip()
                        break
                
                # Поиск DOI
                doi_match = re.search(doi_pattern, context)
                doi = doi_match.group() if doi_match else None
                
                publications.append({
                    'title': title,
                    'journal': journal,
                    'year': year,
                    'doi': doi,
                    'context': context.strip()
                })
        
        return publications
    
    def extract_research_areas(self, text: str) -> List[str]:
        """Извлечение областей исследований"""
        research_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'computer science', 'data science', 'bioinformatics',
            'computational biology', 'neuroscience', 'cognitive science',
            'robotics', 'computer vision', 'natural language processing',
            'mathematics', 'statistics', 'physics', 'chemistry',
            'biology', 'medicine', 'engineering', 'psychology',
            'economics', 'finance', 'linguistics', 'philosophy',
            'sociology', 'anthropology', 'political science'
        ]
        
        areas = []
        text_lower = text.lower()
        
        for keyword in research_keywords:
            if keyword in text_lower:
                areas.append(keyword.title())
        
        return list(set(areas))
    
    def extract_academic_ids(self, text: str, soup: BeautifulSoup = None) -> Dict[str, str]:
        """Извлечение академических идентификаторов"""
        ids = {}
        
        # ORCID
        orcid_pattern = r'\b(\d{4}-\d{4}-\d{4}-\d{3}[\dX])\b'
        orcid_match = re.search(orcid_pattern, text)
        if orcid_match:
            ids['orcid'] = orcid_match.group(1)
        
        # ResearcherID
        researcher_id_pattern = r'\b([A-Z]-\d{4}-\d{4})\b'
        researcher_id_match = re.search(researcher_id_pattern, text)
        if researcher_id_match:
            ids['researcher_id'] = researcher_id_match.group(1)
        
        # Google Scholar ID (если есть ссылка)
        if soup:
            scholar_links = soup.find_all('a', href=re.compile(r'scholar\.google\.com/citations\?user=([^&]+)'))
            for link in scholar_links:
                match = re.search(r'user=([^&]+)', link['href'])
                if match:
                    ids['google_scholar'] = match.group(1)
        
        return ids

class AcademicSearchEngine:
    """Специализированный поисковик для академической информации"""
    
    def __init__(self, timeout: int = 30, max_results: int = 30):
        self.timeout = timeout
        self.max_results = max_results
        self.session = None
        self.extractor = AcademicDataExtractor()
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    def create_academic_search_queries(self, email: str) -> List[str]:
        """Создание специализированных запросов для академического поиска"""
        username = email.split('@')[0]
        domain = email.split('@')[1]
        
        # Базовые запросы
        base_queries = [
            f'"{email}" professor',
            f'"{email}" PhD',
            f'"{email}" research',
            f'"{email}" university',
            f'"{email}" publication',
            f'"{email}" scholar',
            f'"{email}" academic',
            f'"{email}" faculty'
        ]
        
        # Запросы для академических платформ
        platform_queries = [
            f'"{email}" site:scholar.google.com',
            f'"{email}" site:researchgate.net',
            f'"{email}" site:academia.edu',
            f'"{email}" site:orcid.org',
            f'"{email}" site:arxiv.org',
            f'"{email}" site:pubmed.ncbi.nlm.nih.gov'
        ]
        
        # Запросы по имени пользователя
        username_queries = [
            f'"{username}" professor university',
            f'"{username}" PhD {domain}',
            f'"{username}" research publication',
            f'"{username}" academic {domain}'
        ]
        
        # Специализированные запросы для поиска публикаций
        publication_queries = [
            f'"{email}" "published in"',
            f'"{email}" "journal"',
            f'"{email}" "conference"',
            f'"{email}" "proceedings"',
            f'"{email}" DOI'
        ]
        
        return base_queries + platform_queries + username_queries + publication_queries
    
    async def search_google_academic(self, email: str) -> List[AcademicSearchResult]:
        """Поиск академической информации в Google"""
        queries = self.create_academic_search_queries(email)
        all_results = []
        
        for query in queries[:15]:  # Ограничиваем количество запросов
            try:
                results = await self._search_single_query(query, email)
                all_results.extend(results)
                await asyncio.sleep(2)  # Пауза между запросами
            except Exception as e:
                logger.error(f"Error searching query '{query}': {str(e)}")
                continue
        
        # Удаляем дубликаты и сортируем по релевантности
        unique_results = []
        seen_urls = set()
        
        for result in sorted(all_results, key=lambda x: x.academic_score, reverse=True):
            if result.url not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result.url)
        
        return unique_results[:self.max_results]
    
    async def _search_single_query(self, query: str, email: str) -> List[AcademicSearchResult]:
        """Выполнение одного поискового запроса"""
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        try:
            async with self.session.get(search_url, headers=headers) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                return self._parse_google_results(soup, email, query)
                
        except Exception as e:
            logger.error(f"Error fetching search results: {str(e)}")
            return []
    
    def _parse_google_results(self, soup: BeautifulSoup, email: str, query: str) -> List[AcademicSearchResult]:
        """Парсинг результатов Google с академическим скорингом"""
        results = []
        result_elements = soup.select('div.g')
        
        for rank, result_elem in enumerate(result_elements, 1):
            try:
                # Извлекаем заголовок
                title_elem = result_elem.select_one('h3')
                title = title_elem.get_text().strip() if title_elem else ""
                
                # Извлекаем URL
                url_elem = result_elem.select_one('a[href]')
                if not url_elem:
                    continue
                
                url = url_elem.get('href', '')
                if url.startswith('/url?'):
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                    if 'q' in parsed:
                        url = parsed['q'][0]
                
                # Извлекаем описание
                snippet_elem = result_elem.select_one('.VwiC3b, .s3v9rd')
                snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                
                if url and title:
                    # Вычисляем академический скоринг
                    academic_score = self._calculate_academic_score(title, snippet, url, email)
                    academic_indicators = self._identify_academic_indicators(title, snippet, url)
                    
                    result = AcademicSearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        source='google',
                        rank=rank,
                        relevance_score=self._calculate_relevance_score(title, snippet, email),
                        academic_score=academic_score,
                        academic_indicators=academic_indicators
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.warning(f"Error parsing result #{rank}: {str(e)}")
                continue
        
        return results
    
    def _calculate_academic_score(self, title: str, snippet: str, url: str, email: str) -> float:
        """Расчет академического скоринга"""
        score = 0.0
        text = (title + ' ' + snippet + ' ' + url).lower()
        
        # Академические платформы (высокий вес)
        academic_domains = [
            'scholar.google.com', 'researchgate.net', 'academia.edu',
            'orcid.org', 'arxiv.org', 'pubmed.ncbi.nlm.nih.gov',
            'ieee.org', 'acm.org', 'springer.com', 'elsevier.com'
        ]
        
        for domain in academic_domains:
            if domain in url:
                score += 0.4
                break
        
        # Университетские домены (.edu)
        if '.edu' in url:
            score += 0.3
        
        # Академические ключевые слова
        academic_keywords = {
            'professor': 0.3, 'phd': 0.25, 'doctor': 0.2, 'research': 0.2,
            'university': 0.25, 'college': 0.2, 'faculty': 0.25,
            'publication': 0.3, 'journal': 0.25, 'conference': 0.2,
            'paper': 0.15, 'study': 0.1, 'academic': 0.2,
            'scholar': 0.25, 'researcher': 0.25, 'scientist': 0.2,
            'laboratory': 0.2, 'institute': 0.2, 'department': 0.15
        }
        
        for keyword, weight in academic_keywords.items():
            if keyword in text:
                score += weight
        
        # Степени
        degree_keywords = ['phd', 'ph.d', 'md', 'm.d', 'msc', 'm.sc', 'mba', 'm.b.a']
        for degree in degree_keywords:
            if degree in text:
                score += 0.2
                break
        
        # Наличие email в контексте
        if email.lower() in text:
            score += 0.3
        
        # Нормализация скора
        return min(1.0, score)
    
    def _identify_academic_indicators(self, title: str, snippet: str, url: str) -> List[str]:
        """Идентификация академических индикаторов"""
        indicators = []
        text = (title + ' ' + snippet + ' ' + url).lower()
        
        # Платформы
        if any(domain in url for domain in ['scholar.google.com', 'researchgate.net', 'academia.edu']):
            indicators.append('academic_platform')
        
        # Университетский домен
        if '.edu' in url:
            indicators.append('university_domain')
        
        # Степени
        if any(degree in text for degree in ['phd', 'ph.d', 'md', 'doctor']):
            indicators.append('degree_mentioned')
        
        # Должности
        if any(pos in text for pos in ['professor', 'faculty', 'researcher']):
            indicators.append('academic_position')
        
        # Публикации
        if any(pub in text for pub in ['publication', 'journal', 'conference', 'paper']):
            indicators.append('publications')
        
        # Исследования
        if 'research' in text:
            indicators.append('research_activity')
        
        return indicators
    
    def _calculate_relevance_score(self, title: str, snippet: str, email: str) -> float:
        """Базовый расчет релевантности"""
        score = 1.0
        text = (title + ' ' + snippet).lower()
        email_lower = email.lower()
        
        if email_lower in text:
            score += 0.5
        
        if email.split('@')[0].lower() in text:
            score += 0.3
        
        return min(1.0, score)

class AcademicIntelligenceCollector:
    """Основной класс для сбора академической информации"""
    
    def __init__(self, timeout: int = 30, max_results: int = 30):
        self.search_engine = AcademicSearchEngine(timeout, max_results)
        self.extractor = AcademicDataExtractor()
        
    async def collect_academic_profile(self, email: str) -> Dict[str, Any]:
        """Сбор полного академического профиля"""
        logger.info(f"Starting academic intelligence collection for {email}")
        
        async with self.search_engine:
            # Поиск академической информации
            search_results = await self.search_engine.search_google_academic(email)
            
            # Анализ найденных страниц
            profile_data = await self._analyze_search_results(search_results, email)
            
            # Создание академического профиля
            academic_profile = self._build_academic_profile(profile_data, email)
            
            return {
                'email': email,
                'academic_profile': academic_profile.__dict__,
                'search_results': [result.__dict__ for result in search_results],
                'analysis_summary': self._create_analysis_summary(academic_profile, search_results),
                'confidence_scores': self._calculate_confidence_scores(academic_profile, search_results),
                'collection_timestamp': datetime.now().isoformat()
            }
    
    async def _analyze_search_results(self, results: List[AcademicSearchResult], email: str) -> Dict[str, Any]:
        """Анализ результатов поиска для извлечения данных"""
        profile_data = {
            'degrees': [],
            'positions': [],
            'institutions': set(),
            'publications': [],
            'research_areas': set(),
            'academic_ids': {},
            'social_profiles': [],
            'academic_websites': []
        }
        
        # Анализируем каждый результат
        for result in results:
            try:
                # Извлекаем данные из сниппета и заголовка
                text = result.title + ' ' + result.snippet
                
                # Степени
                degrees = self.extractor.extract_degrees(text)
                profile_data['degrees'].extend(degrees)
                
                # Должности
                positions = self.extractor.extract_positions(text)
                profile_data['positions'].extend(positions)
                
                # Публикации
                publications = self.extractor.extract_publications(text)
                profile_data['publications'].extend(publications)
                
                # Области исследований
                research_areas = self.extractor.extract_research_areas(text)
                profile_data['research_areas'].update(research_areas)
                
                # Академические ID
                academic_ids = self.extractor.extract_academic_ids(text)
                profile_data['academic_ids'].update(academic_ids)
                
                # Сохраняем ссылки на академические платформы
                if any(platform in result.url for platform in self.extractor.academic_platforms):
                    profile_data['academic_websites'].append(result.url)
                
                # Если это университетский сайт
                if '.edu' in result.url:
                    # Пытаемся извлечь название университета из URL
                    domain_parts = result.url.split('/')
                    if len(domain_parts) > 2:
                        university = domain_parts[2].replace('.edu', '').replace('www.', '')
                        profile_data['institutions'].add(university.title())
                
            except Exception as e:
                logger.warning(f"Error analyzing result {result.url}: {str(e)}")
                continue
        
        # Преобразуем множества в списки
        profile_data['institutions'] = list(profile_data['institutions'])
        profile_data['research_areas'] = list(profile_data['research_areas'])
        
        return profile_data
    
    def _build_academic_profile(self, profile_data: Dict[str, Any], email: str) -> AcademicProfile:
        """Построение академического профиля"""
        profile = AcademicProfile(email=email)
        
        # Степени (убираем дубликаты)
        unique_degrees = []
        seen_degrees = set()
        for degree in profile_data['degrees']:
            degree_key = f"{degree['degree']}_{degree.get('university', '')}"
            if degree_key not in seen_degrees:
                unique_degrees.append(degree)
                seen_degrees.add(degree_key)
        profile.degrees = unique_degrees
        
        # Должности (убираем дубликаты)
        unique_positions = []
        seen_positions = set()
        for position in profile_data['positions']:
            pos_key = f"{position['position']}_{position.get('university', '')}"
            if pos_key not in seen_positions:
                unique_positions.append(position)
                seen_positions.add(pos_key)
        profile.positions = unique_positions
        
        # Определяем текущую академическую позицию
        if profile.positions:
            # Сортируем по "престижности" должности
            position_ranks = {
                'professor': 5, 'associate professor': 4, 'assistant professor': 3,
                'lecturer': 2, 'postdoc': 1, 'graduate student': 0
            }
            
            best_position = max(profile.positions, 
                              key=lambda p: max([position_ranks.get(keyword, 0) 
                                               for keyword in p['position'].lower().split()]))
            profile.academic_rank = best_position['position']
        
        # Остальные поля
        profile.institutions = profile_data['institutions']
        profile.publications = profile_data['publications']
        profile.research_areas = profile_data['research_areas']
        profile.academic_ids = profile_data['academic_ids']
        profile.academic_websites = list(set(profile_data['academic_websites']))
        
        # Попытка извлечь имя из контекста
        if not profile.name and profile.positions:
            # Ищем имя в контексте должностей
            for position in profile.positions:
                context = position.get('context', '')
                # Простая эвристика для поиска имени
                name_patterns = [
                    r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
                    r'\bDr\.?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
                    r'\bProf\.?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, context)
                    if match:
                        potential_name = match.group(1)
                        # Проверяем, что это не общие слова
                        if not any(word in potential_name.lower() for word in ['university', 'department', 'college']):
                            profile.name = potential_name
                            break
                if profile.name:
                    break
        
        return profile
    
    def _create_analysis_summary(self, profile: AcademicProfile, results: List[AcademicSearchResult]) -> Dict[str, Any]:
        """Создание сводки анализа"""
        return {
            'total_search_results': len(results),
            'academic_results': len([r for r in results if r.academic_score > 0.3]),
            'high_confidence_results': len([r for r in results if r.academic_score > 0.6]),
            'platforms_found': len(set([self._extract_platform(r.url) for r in results if self._extract_platform(r.url)])),
            'degrees_found': len(profile.degrees),
            'positions_found': len(profile.positions),
            'publications_found': len(profile.publications),
            'institutions_found': len(profile.institutions),
            'research_areas_found': len(profile.research_areas),
            'has_name': profile.name is not None,
            'has_academic_rank': profile.academic_rank is not None,
            'academic_ids_found': len(profile.academic_ids)
        }
    
    def _calculate_confidence_scores(self, profile: AcademicProfile, results: List[AcademicSearchResult]) -> Dict[str, float]:
        """Расчет показателей уверенности"""
        scores = {}
        
        # Общая уверенность в академическом статусе
        academic_indicators = sum(1 for r in results if r.academic_score > 0.3)
        scores['academic_status'] = min(1.0, academic_indicators / 5.0)
        
        # Уверенность в степенях
        degree_sources = len(set([d.get('context', '') for d in profile.degrees]))
        scores['degrees'] = min(1.0, degree_sources / 3.0)
        
        # Уверенность в должности
        position_sources = len(set([p.get('context', '') for p in profile.positions]))
        scores['positions'] = min(1.0, position_sources / 2.0)
        
        # Уверенность в публикациях
        pub_sources = len(set([p.get('context', '') for p in profile.publications]))
        scores['publications'] = min(1.0, pub_sources / 3.0)
        
        # Общая уверенность
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _extract_platform(self, url: str) -> Optional[str]:
        """Извлечение платформы из URL"""
        for domain, platform in self.extractor.academic_platforms.items():
            if domain in url:
                return platform
        return None

# Пример использования
async def main():
    collector = AcademicIntelligenceCollector()
    result = await collector.collect_academic_profile("john.smith@university.edu")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
