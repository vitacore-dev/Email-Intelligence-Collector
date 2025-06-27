"""
Тесты для улучшенного веб-скрапера
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from bs4 import BeautifulSoup

from web_scraper import (
    EnhancedWebScraper, 
    ScrapingConfig, 
    SelectorConfig,
    ErrorTracker,
    RateLimiter,
    NLPProcessor
)

class TestErrorTracker(unittest.TestCase):
    """Тесты для ErrorTracker"""
    
    def setUp(self):
        self.error_tracker = ErrorTracker()
    
    def test_log_error(self):
        """Тест логирования ошибки"""
        self.error_tracker.log_error("http://test.com", "test_error", "Test message")
        
        self.assertEqual(len(self.error_tracker.errors["http://test.com"]), 1)
        self.assertEqual(self.error_tracker.error_counts["test_error"], 1)
    
    def test_get_error_summary(self):
        """Тест получения сводки ошибок"""
        self.error_tracker.log_error("http://test1.com", "error1", "Message 1")
        self.error_tracker.log_error("http://test2.com", "error2", "Message 2")
        self.error_tracker.log_error("http://test1.com", "error1", "Message 3")
        
        summary = self.error_tracker.get_error_summary()
        
        self.assertEqual(summary["total_errors"], 3)
        self.assertEqual(summary["affected_urls"], 2)
        self.assertEqual(summary["error_types"]["error1"], 2)
        self.assertEqual(summary["error_types"]["error2"], 1)

class TestRateLimiter(unittest.TestCase):
    """Тесты для RateLimiter"""
    
    def setUp(self):
        self.rate_limiter = RateLimiter(initial_delay=0.1)
    
    def test_adjust_delay_success(self):
        """Тест корректировки задержки при успехе"""
        domain = "test.com"
        initial_delay = self.rate_limiter.delays[domain]
        
        self.rate_limiter.adjust_delay(domain, success=True)
        
        self.assertLess(self.rate_limiter.delays[domain], initial_delay)
        self.assertEqual(self.rate_limiter.failure_counts[domain], 0)
    
    def test_adjust_delay_failure(self):
        """Тест корректировки задержки при неудаче"""
        domain = "test.com"
        initial_delay = self.rate_limiter.delays[domain]
        
        self.rate_limiter.adjust_delay(domain, success=False)
        
        self.assertGreater(self.rate_limiter.delays[domain], initial_delay)
        self.assertEqual(self.rate_limiter.failure_counts[domain], 1)

class TestNLPProcessor(unittest.TestCase):
    """Тесты для NLPProcessor"""
    
    def setUp(self):
        self.nlp_processor = NLPProcessor()
    
    def test_analyze_sentiment(self):
        """Тест анализа тональности"""
        positive_text = "I love this amazing product!"
        negative_text = "This is terrible and awful!"
        
        positive_sentiment = self.nlp_processor.analyze_sentiment(positive_text)
        negative_sentiment = self.nlp_processor.analyze_sentiment(negative_text)
        
        self.assertGreater(positive_sentiment["polarity"], 0)
        self.assertLess(negative_sentiment["polarity"], 0)
    
    def test_extract_keywords_advanced(self):
        """Тест продвинутого извлечения ключевых слов"""
        text = "John works as a software engineer at Google. He loves programming and coding."
        
        keywords = self.nlp_processor.extract_keywords_advanced(text, top_k=5)
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        
        # Проверяем структуру ключевых слов
        if keywords:
            keyword = keywords[0]
            self.assertIn("word", keyword)
            self.assertIn("frequency", keyword)
            self.assertIn("pos_tags", keyword)
    
    def test_extract_person_info_nlp(self):
        """Тест извлечения информации о человеке через NLP"""
        text = "John Doe works at Microsoft in Seattle. He is a software engineer."
        
        info = self.nlp_processor.extract_person_info_nlp(text)
        
        # Результат может варьироваться в зависимости от доступности моделей
        self.assertIsInstance(info, dict)

class TestScrapingConfig(unittest.TestCase):
    """Тесты для ScrapingConfig"""
    
    def test_default_config(self):
        """Тест конфигурации по умолчанию"""
        config = ScrapingConfig()
        
        self.assertEqual(config.max_pages, 10)
        self.assertEqual(config.concurrent_requests, 5)
        self.assertEqual(config.timeout, 30)
    
    def test_custom_config(self):
        """Тест пользовательской конфигурации"""
        config = ScrapingConfig(
            max_pages=20,
            concurrent_requests=10,
            timeout=60
        )
        
        self.assertEqual(config.max_pages, 20)
        self.assertEqual(config.concurrent_requests, 10)
        self.assertEqual(config.timeout, 60)

class TestSelectorConfig(unittest.TestCase):
    """Тесты для SelectorConfig"""
    
    def test_default_selectors(self):
        """Тест селекторов по умолчанию"""
        config = SelectorConfig()
        
        self.assertIn('h1', config.name_selectors)
        self.assertIn('.job-title', config.job_selectors)
        self.assertIn('.company', config.company_selectors)
    
    def test_platform_selectors(self):
        """Тест селекторов платформ"""
        config = SelectorConfig()
        
        self.assertIn('linkedin.com', config.platform_selectors)
        self.assertIn('twitter.com', config.platform_selectors)
        self.assertIn('github.com', config.platform_selectors)

class TestEnhancedWebScraper(unittest.IsolatedAsyncioTestCase):
    """Тесты для EnhancedWebScraper"""
    
    def setUp(self):
        self.email = "test@example.com"
        self.config = ScrapingConfig(max_pages=1, concurrent_requests=1)
        self.scraper = EnhancedWebScraper(self.email, self.config)
    
    def test_initialization(self):
        """Тест инициализации скрапера"""
        self.assertEqual(self.scraper.email, self.email)
        self.assertEqual(self.scraper.config.max_pages, 1)
        self.assertIsInstance(self.scraper.error_tracker, ErrorTracker)
        self.assertIsInstance(self.scraper.rate_limiter, RateLimiter)
        self.assertIsInstance(self.scraper.nlp_processor, NLPProcessor)
    
    def test_get_cache_key(self):
        """Тест генерации ключа кеша"""
        url = "https://example.com"
        key1 = self.scraper._get_cache_key(url)
        key2 = self.scraper._get_cache_key(url)
        
        self.assertEqual(key1, key2)
        self.assertIsInstance(key1, str)
    
    def test_get_platform_selectors(self):
        """Тест получения селекторов платформы"""
        linkedin_url = "https://www.linkedin.com/in/user"
        github_url = "https://github.com/user"
        unknown_url = "https://unknown-site.com/user"
        
        linkedin_selectors = self.scraper._get_platform_selectors(linkedin_url)
        github_selectors = self.scraper._get_platform_selectors(github_url)
        unknown_selectors = self.scraper._get_platform_selectors(unknown_url)
        
        # LinkedIn должен иметь специфичные селекторы
        self.assertIn('name', linkedin_selectors)
        
        # GitHub тоже
        self.assertIn('name', github_selectors)
        
        # Неизвестный сайт должен получить стандартные селекторы
        self.assertEqual(unknown_selectors['name'], self.scraper.selector_config.name_selectors)
    
    def test_is_likely_name_enhanced(self):
        """Тест улучшенной проверки имен"""
        valid_names = [
            "John Doe",
            "Mary Jane Smith",
            "Jean-Claude Van Damme",
            "O'Connor"
        ]
        
        invalid_names = [
            "john doe",  # не с заглавной буквы
            "Page Title",  # содержит ключевое слово
            "Company Inc",  # содержит ключевое слово
            "A",  # слишком короткое
            "This Is A Very Long Name That Should Not Be Considered Valid",  # слишком длинное
            "John123",  # содержит цифры
        ]
        
        for name in valid_names:
            with self.subTest(name=name):\n                self.assertTrue(self.scraper._is_likely_name_enhanced(name))\n        \n        for name in invalid_names:\n            with self.subTest(name=name):\n                self.assertFalse(self.scraper._is_likely_name_enhanced(name))\n    \n    def test_detect_language(self):\n        \"\"\"Тест определения языка\"\"\"\n        english_text = \"This is an English text about technology and programming.\"\n        \n        language = self.scraper._detect_language(english_text)\n        \n        # Результат может быть 'en' или 'unknown' в зависимости от доступности библиотек\n        self.assertIn(language, ['en', 'unknown'])\n    \n    @patch('aiohttp.ClientSession.get')\n    async def test_fetch_and_parse_page_success(self, mock_get):\n        \"\"\"Тест успешного получения и парсинга страницы\"\"\"\n        # Мокаем HTTP ответ\n        mock_response = AsyncMock()\n        mock_response.status = 200\n        mock_response.headers = {'content-type': 'text/html'}\n        mock_response.text.return_value = \"\"\"\n        <html>\n            <head><title>John Doe - Profile</title></head>\n            <body>\n                <h1>John Doe</h1>\n                <div class=\"job-title\">Software Engineer</div>\n                <div class=\"company\">Tech Corp</div>\n                <a href=\"https://linkedin.com/in/johndoe\">LinkedIn</a>\n            </body>\n        </html>\n        \"\"\"\n        \n        mock_get.return_value.__aenter__.return_value = mock_response\n        \n        # Создаем сессию для тестирования\n        self.scraper.session = MagicMock()\n        \n        url = \"https://example.com\"\n        result = await self.scraper._fetch_and_parse_page(url)\n        \n        self.assertIsNotNone(result)\n        self.assertEqual(result['url'], url)\n        self.assertEqual(result['title'], \"John Doe - Profile\")\n        self.assertIn('person_info', result)\n        self.assertIn('contact_info', result)\n        self.assertIn('social_links', result)\n    \n    @patch('aiohttp.ClientSession.get')\n    async def test_fetch_and_parse_page_error(self, mock_get):\n        \"\"\"Тест обработки ошибки при получении страницы\"\"\"\n        # Мокаем HTTP ответ с ошибкой\n        mock_response = AsyncMock()\n        mock_response.status = 404\n        \n        mock_get.return_value.__aenter__.return_value = mock_response\n        \n        self.scraper.session = MagicMock()\n        \n        url = \"https://example.com/404\"\n        result = await self.scraper._fetch_and_parse_page(url)\n        \n        self.assertIsNone(result)\n        \n        # Проверяем, что ошибка была залогирована\n        self.assertGreater(len(self.scraper.error_tracker.errors), 0)\n\nclass TestIntegration(unittest.IsolatedAsyncioTestCase):\n    \"\"\"Интеграционные тесты\"\"\"\n    \n    def test_mock_html_parsing(self):\n        \"\"\"Тест парсинга HTML с различными структурами\"\"\"\n        scraper = EnhancedWebScraper(\"test@example.com\")\n        \n        # Тест LinkedIn-подобной структуры\n        linkedin_html = \"\"\"\n        <html>\n            <body>\n                <div class=\"text-heading-xlarge\">John Smith</div>\n                <div class=\"text-body-medium break-words\">Senior Developer</div>\n                <div class=\"pv-text-details__right-panel\">\n                    <div class=\"text-body-small\">Microsoft</div>\n                </div>\n            </body>\n        </html>\n        \"\"\"\n        \n        soup = BeautifulSoup(linkedin_html, 'html.parser')\n        platform_selectors = scraper._get_platform_selectors(\"https://linkedin.com/in/user\")\n        \n        person_info = scraper._extract_person_info_enhanced(soup, platform_selectors)\n        \n        # В зависимости от структуры, может найти информацию\n        self.assertIsInstance(person_info, dict)\n    \n    def test_social_links_extraction(self):\n        \"\"\"Тест извлечения социальных ссылок\"\"\"\n        scraper = EnhancedWebScraper(\"test@example.com\")\n        \n        html = \"\"\"\n        <html>\n            <body>\n                <a href=\"https://linkedin.com/in/johndoe\">LinkedIn Profile</a>\n                <a href=\"https://github.com/johndoe\">GitHub</a>\n                <a href=\"https://twitter.com/johndoe\">@johndoe</a>\n                <a href=\"https://example.com\">Regular Link</a>\n            </body>\n        </html>\n        \"\"\"\n        \n        soup = BeautifulSoup(html, 'html.parser')\n        social_links = scraper._extract_social_links_enhanced(soup)\n        \n        self.assertEqual(len(social_links), 3)  # LinkedIn, GitHub, Twitter\n        \n        platforms = [link['platform'] for link in social_links]\n        self.assertIn('LinkedIn', platforms)\n        self.assertIn('GitHub', platforms)\n        self.assertIn('Twitter', platforms)\n\nif __name__ == '__main__':\n    # Запуск всех тестов\n    unittest.main(verbosity=2)
