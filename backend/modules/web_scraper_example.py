"""
Пример использования улучшенного веб-скрапера (EnhancedWebScraper)

Этот пример демонстрирует все новые возможности улучшенного скрапера:
- Адаптивные селекторы для различных платформ
- NLP анализ и извлечение именованных сущностей
- Кеширование результатов
- Умное ограничение скорости запросов
- Расширенная обработка ошибок
- Параллельная обработка страниц
"""

import asyncio
import json
from web_scraper import EnhancedWebScraper, ScrapingConfig, SelectorConfig

async def basic_usage_example():
    """Базовое использование скрапера"""
    email = "test@example.com"
    urls = [
        "https://www.linkedin.com/in/example",
        "https://github.com/example",
        "https://twitter.com/example"
    ]
    
    async with EnhancedWebScraper(email) as scraper:
        results = await scraper.scrape_websites_enhanced(urls)
        
        print("=== Базовые результаты ===")
        print(f"Найдена персональная информация: {results['person_info']}")
        print(f"Контактная информация: {results['contact_info']}")
        print(f"Социальные ссылки: {len(results['social_links'])}")
        print(f"Статистика: {results['performance_stats']}")

async def advanced_config_example():
    """Пример с продвинутой конфигурацией"""
    email = "test@example.com"
    
    # Настройка параметров скрапинга
    config = ScrapingConfig(
        max_pages=15,
        concurrent_requests=3,
        timeout=45,
        retry_attempts=2,
        cache_ttl=7200,  # 2 часа
        delay_between_requests=1.5
    )
    
    # Настройка селекторов
    selector_config = SelectorConfig()
    selector_config.name_selectors.extend([
        '.user-profile-name',
        '.author-name',
        '[data-name]'
    ])
    
    # Добавление специфичных селекторов для новых платформ
    selector_config.platform_selectors['example.com'] = {
        'name': ['.profile-name', '.user-title'],
        'job': ['.job-description'],
        'company': ['.company-info']
    }
    
    urls = ["https://example.com/profile/user123"]
    
    async with EnhancedWebScraper(email, config, selector_config) as scraper:
        results = await scraper.scrape_websites_enhanced(urls)
        
        print("=== Продвинутые результаты ===")
        print(f"NLP анализ: {results['nlp_analysis']}")
        print(f"Ошибки: {results['errors']}")
        
        # Получение статистики скрапера
        stats = scraper.get_scraping_stats()
        print(f"Статистика скрапера: {stats}")

async def nlp_analysis_example():
    """Пример NLP анализа"""
    email = "test@example.com"
    urls = ["https://blog.example.com/about-author"]
    
    async with EnhancedWebScraper(email) as scraper:
        results = await scraper.scrape_websites_enhanced(urls)
        
        print("=== NLP Анализ ===")
        for url, analysis in results['nlp_analysis'].items():
            print(f"\nURL: {url}")
            print(f"Тональность: {analysis.get('sentiment', {})}")
            print(f"Именованные сущности (spaCy): {analysis.get('entities_spacy', {})}")
            print(f"Именованные сущности (NLTK): {analysis.get('entities_nltk', {})}")
            print(f"Определенный язык: {analysis.get('language_detected', 'unknown')}")
        
        # Продвинутые ключевые слова
        for url, content in results['content_analysis'].items():
            print(f"\nКлючевые слова для {url}:")
            keywords = content.get('keywords', [])[:10]  # Топ-10
            for kw in keywords:
                if isinstance(kw, dict):
                    print(f"  - {kw['word']} (частота: {kw['frequency']}, POS: {kw.get('pos_tags', [])})")
                else:
                    print(f"  - {kw}")

async def error_handling_example():
    """Пример обработки ошибок"""
    email = "test@example.com"
    urls = [
        "https://valid-site.com",
        "https://non-existent-site-12345.com",
        "https://site-with-errors.com",
        "invalid-url"
    ]
    
    async with EnhancedWebScraper(email) as scraper:
        results = await scraper.scrape_websites_enhanced(urls)
        
        print("=== Обработка ошибок ===")
        print(f"Успешных скрапингов: {results['performance_stats']['successful_scrapes']}")
        print(f"Неудачных скрапингов: {results['performance_stats']['failed_scrapes']}")
        
        errors = results['errors']
        print(f"\nВсего ошибок: {errors['total_errors']}")
        print(f"Типы ошибок: {errors['error_types']}")
        print(f"Затронутых URL: {errors['affected_urls']}")
        print(f"Самые частые ошибки: {errors['most_common_errors']}")

async def performance_analysis_example():
    """Пример анализа производительности"""
    email = "test@example.com"
    urls = [f"https://example{i}.com" for i in range(20)]  # 20 URL для тестирования
    
    config = ScrapingConfig(
        concurrent_requests=5,
        max_pages=20
    )
    
    async with EnhancedWebScraper(email, config) as scraper:
        results = await scraper.scrape_websites_enhanced(urls)
        
        print("=== Анализ производительности ===")
        stats = results['performance_stats']
        print(f"Общее время выполнения: {stats['duration']:.2f} секунд")
        print(f"Скорость: {stats['total_urls'] / stats['duration']:.2f} URL/сек")
        print(f"Успешность: {stats['successful_scrapes'] / stats['total_urls'] * 100:.1f}%")
        
        scraper_stats = scraper.get_scraping_stats()
        print(f"Размер кеша: {scraper_stats['cache_size']} записей")
        print(f"Текущие задержки по доменам: {scraper_stats['rate_limiter_stats']['current_delays']}")

async def export_results_example():
    """Пример экспорта результатов"""
    email = "test@example.com"
    urls = ["https://example.com/profile"]
    
    async with EnhancedWebScraper(email) as scraper:
        results = await scraper.scrape_websites_enhanced(urls)
        
        # Экспорт в JSON
        with open('scraping_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print("=== Экспорт результатов ===")
        print("Результаты экспортированы в scraping_results.json")
        
        # Создание краткого отчета
        report = {
            'summary': {
                'total_urls_processed': results['performance_stats']['total_urls'],
                'successful_scrapes': results['performance_stats']['successful_scrapes'],
                'duration': results['performance_stats']['duration'],
                'person_found': bool(results['person_info']),
                'contacts_found': sum(len(contacts) for contacts in results['contact_info'].values()),
                'social_links_found': len(results['social_links'])
            },
            'person_info': results['person_info'],
            'contact_summary': {
                'emails_count': len(results['contact_info']['emails']),
                'phones_count': len(results['contact_info']['phones']),
                'addresses_count': len(results['contact_info']['addresses'])
            }
        }
        
        with open('scraping_summary.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("Краткий отчет сохранен в scraping_summary.json")

if __name__ == "__main__":
    print("Запуск примеров улучшенного веб-скрапера...\n")
    
    # Запуск всех примеров
    asyncio.run(basic_usage_example())
    print("\n" + "="*50 + "\n")
    
    asyncio.run(advanced_config_example())
    print("\n" + "="*50 + "\n")
    
    asyncio.run(nlp_analysis_example())
    print("\n" + "="*50 + "\n")
    
    asyncio.run(error_handling_example())
    print("\n" + "="*50 + "\n")
    
    asyncio.run(performance_analysis_example())
    print("\n" + "="*50 + "\n")
    
    asyncio.run(export_results_example())
    
    print("\nВсе примеры выполнены!")
