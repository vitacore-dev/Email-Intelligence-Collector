#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Analysis Module for Email Intelligence Collection
Specialized module for searching, downloading, and analyzing PDF documents
"""

import asyncio
import aiohttp
import logging
import re
import hashlib
import tempfile
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import time

# PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PDF libraries not available. Install PyPDF2 and pdfplumber.")

logger = logging.getLogger(__name__)

class PDFSearchEngines:
    """PDF-специфичные поисковые системы и репозитории"""
    
    # Поисковые системы с filetype:pdf
    SEARCH_ENGINES = [
        "https://www.google.com/search?q=\"{email}\"+filetype:pdf",
        "https://www.bing.com/search?q=\"{email}\"+filetype:pdf", 
        "https://duckduckgo.com/?q=\"{email}\"+filetype:pdf",
        "https://yandex.ru/search/?text={email}%20filetype%3Apdf",
    ]
    
    # Академические репозитории
    ACADEMIC_REPOSITORIES = [
        "https://scholar.google.com/scholar?q=\"{email}\"",
        "https://www.researchgate.net/search?q={email}",
        "https://arxiv.org/search/?query={email}&searchtype=all",
        "https://www.academia.edu/search?q={email}",
        "https://pubmed.ncbi.nlm.nih.gov/?term={email}",
    ]
    
    # Документные репозитории
    DOCUMENT_REPOSITORIES = [
        "https://www.scribd.com/search?query={email}",
        "https://www.slideshare.net/search/slideshow?q={email}",
        "https://issuu.com/search?q={email}",
    ]

class PDFAnalyzer:
    """Анализатор PDF документов для поиска email и извлечения контекста"""
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self._own_session = session is None
        self.temp_dir = tempfile.mkdtemp(prefix="pdf_analysis_")
        
        # Настройки для скачивания PDF
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,*/*',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        }
        
    async def __aenter__(self):
        if self._own_session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers=self.headers
            )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_session and self.session:
            await self.session.close()
        # Очистка временных файлов
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def search_pdf_documents(self, email: str) -> List[Dict[str, Any]]:
        """Поиск PDF документов, содержащих указанный email"""
        all_results = []
        encoded_email = quote(email)
        
        # Поиск через поисковые системы
        logger.info(f"Searching for PDF documents containing {email}")
        
        search_engines = PDFSearchEngines.SEARCH_ENGINES
        for engine_url in search_engines:
            engine_name = self._extract_engine_name(engine_url)
            search_url = engine_url.format(email=encoded_email)
            
            try:
                pdf_links = await self._search_engine_for_pdfs(search_url, engine_name)
                for pdf_link in pdf_links:
                    pdf_info = await self._analyze_pdf_url(pdf_link, email)
                    if pdf_info:
                        pdf_info['source'] = engine_name
                        pdf_info['search_url'] = search_url
                        all_results.append(pdf_info)
                        
                # Ограничиваем количество результатов на движок
                if len([r for r in all_results if r.get('source') == engine_name]) >= 3:
                    break
                    
            except Exception as e:
                logger.error(f"Error searching {engine_name}: {e}")
                
            await asyncio.sleep(1)  # Rate limiting
        
        # Поиск в академических репозиториях
        for repo_url in PDFSearchEngines.ACADEMIC_REPOSITORIES[:2]:  # Ограничиваем 2 репозиториями
            repo_name = self._extract_engine_name(repo_url)
            search_url = repo_url.format(email=encoded_email)
            
            try:
                academic_results = await self._search_academic_repository(search_url, repo_name, email)
                all_results.extend(academic_results)
            except Exception as e:
                logger.error(f"Error searching {repo_name}: {e}")
                
            await asyncio.sleep(1)
        
        logger.info(f"Found {len(all_results)} PDF documents for analysis")
        return all_results

    async def _search_engine_for_pdfs(self, search_url: str, engine_name: str) -> List[str]:
        """Поиск PDF ссылок через поисковую систему"""
        try:
            async with self.session.get(search_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._extract_pdf_links(content)
        except Exception as e:
            logger.warning(f"Failed to search {engine_name}: {e}")
        return []

    async def _search_academic_repository(self, search_url: str, repo_name: str, email: str) -> List[Dict[str, Any]]:
        """Поиск в академических репозиториях"""
        results = []
        try:
            async with self.session.get(search_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Извлекаем ссылки на статьи/документы
                    if 'scholar.google' in search_url:
                        results.extend(await self._parse_google_scholar(content, email))
                    elif 'researchgate' in search_url:
                        results.extend(await self._parse_researchgate(content, email))
                    elif 'arxiv' in search_url:
                        results.extend(await self._parse_arxiv(content, email))
                        
        except Exception as e:
            logger.warning(f"Failed to search {repo_name}: {e}")
        return results

    def _extract_pdf_links(self, content: str) -> List[str]:
        """Извлечение PDF ссылок из HTML контента"""
        # Паттерны для поиска PDF ссылок
        pdf_patterns = [
            r'href="([^"]*\.pdf[^"]*)"',
            r'href=\'([^\']*\.pdf[^\']*)\'',
            r'https?://[^"\s]*\.pdf[^"\s]*',
        ]
        
        pdf_links = []
        for pattern in pdf_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            pdf_links.extend(matches)
        
        # Очистка и валидация ссылок
        clean_links = []
        for link in pdf_links:
            if link.startswith('http') and '.pdf' in link.lower():
                clean_links.append(link)
        
        return list(set(clean_links))[:5]  # Уникальные ссылки, максимум 5

    async def _analyze_pdf_url(self, pdf_url: str, target_email: str) -> Optional[Dict[str, Any]]:
        """Анализ PDF документа по URL"""
        if not PDF_AVAILABLE:
            return {
                'url': pdf_url,
                'title': 'PDF Processing Unavailable',
                'error': 'PDF libraries not installed',
                'email_found': False
            }
        
        try:
            # Скачивание PDF
            pdf_data = await self._download_pdf(pdf_url)
            if not pdf_data:
                return None
            
            # Сохранение во временный файл
            pdf_hash = hashlib.md5(pdf_url.encode()).hexdigest()
            temp_path = Path(self.temp_dir) / f"pdf_{pdf_hash}.pdf"
            
            with open(temp_path, 'wb') as f:
                f.write(pdf_data)
            
            # Анализ содержимого
            analysis_result = await self._analyze_pdf_content(temp_path, target_email, pdf_url)
            
            # Удаление временного файла
            temp_path.unlink(missing_ok=True)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing PDF {pdf_url}: {e}")
            return None

    async def _download_pdf(self, pdf_url: str) -> Optional[bytes]:
        """Скачивание PDF файла"""
        try:
            async with self.session.get(pdf_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200 and 'pdf' in response.headers.get('content-type', '').lower():
                    content = await response.read()
                    if len(content) > 1000:  # Минимальный размер PDF
                        return content
        except Exception as e:
            logger.warning(f"Failed to download PDF {pdf_url}: {e}")
        return None

    async def _analyze_pdf_content(self, pdf_path: Path, target_email: str, pdf_url: str) -> Dict[str, Any]:
        """Анализ содержимого PDF файла"""
        try:
            # Извлечение текста
            text = await self._extract_pdf_text(pdf_path)
            
            # Поиск email в тексте
            email_contexts = self._find_email_contexts(text, target_email)
            
            # Извлечение метаданных
            metadata = await self._extract_pdf_metadata(pdf_path, text)
            
            return {
                'url': pdf_url,
                'title': metadata.get('title', 'Unknown Title'),
                'authors': metadata.get('authors', []),
                'institutions': metadata.get('institutions', []),
                'email_found': len(email_contexts) > 0,
                'email_contexts': email_contexts,
                'text_length': len(text),
                'all_emails': metadata.get('all_emails', []),
                'confidence_score': self._calculate_pdf_confidence(email_contexts, metadata),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing PDF content: {e}")
            return {
                'url': pdf_url,
                'error': str(e),
                'email_found': False
            }

    async def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Извлечение текста из PDF"""
        text = ""
        
        try:
            # Попытка с pdfplumber (более точный)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
            
            # Fallback на PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                logger.error(f"PyPDF2 also failed: {e2}")
        
        return text

    def _find_email_contexts(self, text: str, target_email: str) -> List[Dict[str, str]]:
        """Поиск контекстов где упоминается email"""
        lines = text.split('\n')
        contexts = []
        
        for i, line in enumerate(lines):
            if target_email.lower() in line.lower():
                start = max(0, i-3)
                end = min(len(lines), i+4)
                
                contexts.append({
                    'line_number': i+1,
                    'line': line.strip(),
                    'context': '\n'.join(lines[start:end]),
                    'context_range': f"lines {start+1}-{end}"
                })
        
        return contexts

    async def _extract_pdf_metadata(self, pdf_path: Path, text: str) -> Dict[str, Any]:
        """Извлечение метаданных из PDF"""
        metadata = {
            'title': self._extract_title(text),
            'authors': self._extract_authors(text),
            'institutions': self._extract_institutions(text),
            'all_emails': self._extract_all_emails(text),
            'keywords': self._extract_keywords(text)
        }
        
        return metadata

    def _extract_title(self, text: str) -> str:
        """Извлечение заголовка документа"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines[:10]:  # Проверяем первые 10 непустых строк
            if 10 < len(line) < 200 and not any(char.isdigit() for char in line[:10]):
                return line
        
        return "Unknown Title"

    def _extract_authors(self, text: str) -> List[str]:
        """Извлечение имен авторов"""
        patterns = [
            r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.\s*[А-ЯЁ][а-яё]+',  # Русские имена
            r'[A-Z][a-z]+\s+[A-Z]\.\s*[A-Z]\.\s*[A-Z][a-z]+',  # Английские имена
            r'[A-Z][a-z]+\s+[A-Z][a-z]+',  # Простые имена
        ]
        
        authors = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            authors.extend(matches)
        
        return list(set(authors))[:10]  # Максимум 10 авторов

    def _extract_institutions(self, text: str) -> List[str]:
        """Извлечение названий учреждений"""
        patterns = [
            r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Уу]ниверситет',
            r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Ии]нститут',
            r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Аа]кадеми[яи]',
            r'[A-Z][a-z]+\s+University',
            r'[A-Z][a-z]+\s+Institute',
        ]
        
        institutions = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            institutions.extend(matches)
        
        return list(set(institutions))[:5]

    def _extract_all_emails(self, text: str) -> List[str]:
        """Извлечение всех email адресов из текста"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))

    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов"""
        # Простое извлечение часто встречающихся слов
        words = re.findall(r'\b[а-яёА-ЯЁa-zA-Z]{4,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Возвращаем топ-10 слов
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10] if freq > 2]

    def _calculate_pdf_confidence(self, email_contexts: List[Dict], metadata: Dict) -> float:
        """Расчет коэффициента достоверности для PDF"""
        score = 0.0
        
        # Email найден в документе
        if email_contexts:
            score += 0.4
            # Бонус за количество упоминаний
            score += min(0.2, len(email_contexts) * 0.05)
        
        # Есть авторы
        if metadata.get('authors'):
            score += 0.2
        
        # Есть учреждения
        if metadata.get('institutions'):
            score += 0.1
        
        # Есть другие email адреса (указывает на достоверность)
        if metadata.get('all_emails'):
            score += 0.1
        
        return min(score, 1.0)

    async def _parse_google_scholar(self, content: str, email: str) -> List[Dict[str, Any]]:
        """Парсинг результатов Google Scholar"""
        # Упрощенная реализация для демонстрации
        return []

    async def _parse_researchgate(self, content: str, email: str) -> List[Dict[str, Any]]:
        """Парсинг результатов ResearchGate"""
        return []

    async def _parse_arxiv(self, content: str, email: str) -> List[Dict[str, Any]]:
        """Парсинг результатов arXiv"""
        return []

    def _extract_engine_name(self, url: str) -> str:
        """Извлечение имени поисковой системы из URL"""
        domain = urlparse(url).netloc.lower()
        if 'google' in domain:
            return 'Google'
        elif 'bing' in domain:
            return 'Bing'
        elif 'duckduckgo' in domain:
            return 'DuckDuckGo'
        elif 'yandex' in domain:
            return 'Yandex'
        elif 'scholar' in domain:
            return 'Google Scholar'
        elif 'researchgate' in domain:
            return 'ResearchGate'
        elif 'arxiv' in domain:
            return 'arXiv'
        elif 'academia' in domain:
            return 'Academia.edu'
        else:
            return domain.split('.')[1].title() if '.' in domain else 'Unknown'

# Convenience function for external use
async def search_and_analyze_pdfs(email: str, session: Optional[aiohttp.ClientSession] = None) -> List[Dict[str, Any]]:
    """
    Удобная функция для поиска и анализа PDF документов
    
    Args:
        email: Email адрес для поиска
        session: Опциональная сессия aiohttp
        
    Returns:
        Список результатов анализа PDF документов
    """
    async with PDFAnalyzer(session) as analyzer:
        return await analyzer.search_pdf_documents(email)

if __name__ == "__main__":
    # Пример использования
    async def test_pdf_analysis():
        test_email = "buch1202@mail.ru"
        
        print(f"Тестирование PDF анализа для email: {test_email}")
        
        results = await search_and_analyze_pdfs(test_email)
        
        print(f"\nНайдено PDF документов: {len(results)}")
        for i, result in enumerate(results):
            print(f"\n{i+1}. {result.get('title', 'Unknown')}")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Email найден: {result.get('email_found', False)}")
            print(f"   Источник: {result.get('source', 'Unknown')}")
            if result.get('email_contexts'):
                print(f"   Контекстов: {len(result['email_contexts'])}")

    # Запуск теста
    asyncio.run(test_pdf_analysis())
