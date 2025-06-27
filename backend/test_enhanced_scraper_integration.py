#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации работы улучшенного веб-скрапера
в контексте проекта Email Intelligence Collector
"""

import asyncio
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append('/Users/rafaelamirov/Documents/metod/Email-Intelligence-Collector/backend')

from modules.web_scraper import EnhancedWebScraper, ScrapingConfig, SelectorConfig

async def demo_enhanced_scraper():
    """Демонстрация возможностей улучшенного веб-скрапера"""
    
    print("=" * 60)
    print("🚀 ДЕМОНСТРАЦИЯ УЛУЧШЕННОГО ВЕБ-СКРАПЕРА")
    print("=" * 60)
    
    # Настройка конфигурации
    config = ScrapingConfig(
        max_pages=3,
        concurrent_requests=2,
        timeout=15,
        retry_attempts=2,
        cache_ttl=300,  # 5 минут
        delay_between_requests=1.0
    )
    
    # Настройка селекторов
    selector_config = SelectorConfig()
    
    # Тестовые URL (используем публичные профили)
    test_urls = [
        "https://example.com",  # Простая страница для теста
        "https://httpbin.org/html",  # HTML страница для парсинга
        "https://httpbin.org/json",  # JSON ответ (будет проигнорирован как не HTML)
    ]
    
    email = "demo@example.com"
    
    print(f"📧 Тестовый email: {email}")
    print(f"🔗 URL для тестирования: {len(test_urls)} страниц")
    print(f"⚙️  Конфигурация: макс. страниц={config.max_pages}, таймаут={config.timeout}с")
    print()
    
    try:
        async with EnhancedWebScraper(email, config, selector_config) as scraper:
            print("🔍 Запуск улучшенного скрапинга...")
            
            # Выполняем скрапинг
            results = await scraper.scrape_websites_enhanced(test_urls)
            
            print("✅ Скрапинг завершен!")
            print()
            
            # Выводим результаты
            print("📊 РЕЗУЛЬТАТЫ СКРАПИНГА:")
            print("-" * 40)
            
            # Персональная информация
            person_info = results.get('person_info', {})
            print(f"👤 Персональная информация:")
            if person_info:
                for key, value in person_info.items():
                    print(f"   {key}: {value}")
            else:
                print("   Не найдена")
            print()
            
            # Контактная информация
            contact_info = results.get('contact_info', {})
            print(f"📞 Контактная информация:")
            print(f"   Email-адреса: {len(contact_info.get('emails', []))}")
            print(f"   Телефоны: {len(contact_info.get('phones', []))}")
            print(f"   Адреса: {len(contact_info.get('addresses', []))}")
            print()
            
            # Социальные ссылки
            social_links = results.get('social_links', [])
            print(f"🔗 Социальные ссылки: {len(social_links)}")
            for link in social_links[:3]:  # Показываем первые 3
                print(f"   {link.get('platform', 'Unknown')}: {link.get('url', 'N/A')}")
            print()
            
            # NLP анализ
            nlp_analysis = results.get('nlp_analysis', {})
            print(f"🧠 NLP анализ:")
            if nlp_analysis:
                for url, analysis in list(nlp_analysis.items())[:2]:  # Первые 2 URL
                    print(f"   URL: {url}")
                    sentiment = analysis.get('sentiment', {})
                    print(f"   Тональность: полярность={sentiment.get('polarity', 0):.2f}, субъективность={sentiment.get('subjectivity', 0):.2f}")
                    
                    entities = analysis.get('entities_spacy', {})
                    if entities:
                        print(f"   Сущности: {', '.join(entities.keys())}")
                    
                    lang = analysis.get('language_detected', 'unknown')
                    print(f"   Язык: {lang}")
                    print()
            else:
                print("   Анализ недоступен")
            print()
            
            # Ключевые слова
            content_analysis = results.get('content_analysis', {})
            print(f"🔑 Ключевые слова:")
            total_keywords = 0
            for url, content in content_analysis.items():
                keywords = content.get('keywords', [])
                total_keywords += len(keywords)
                if keywords:
                    print(f"   {url}: {', '.join([kw.get('word', kw) if isinstance(kw, dict) else str(kw) for kw in keywords[:5]])}")
            print(f"   Всего ключевых слов: {total_keywords}")
            print()
            
            # Статистика производительности
            stats = results.get('performance_stats', {})
            print(f"⏱️  СТАТИСТИКА ПРОИЗВОДИТЕЛЬНОСТИ:")
            print("-" * 40)
            print(f"   Всего URL: {stats.get('total_urls', 0)}")
            print(f"   Успешных: {stats.get('successful_scrapes', 0)}")
            print(f"   Неудачных: {stats.get('failed_scrapes', 0)}")
            print(f"   Время выполнения: {stats.get('duration', 0):.2f} сек")
            print(f"   Скорость: {stats.get('total_urls', 0) / max(stats.get('duration', 1), 0.1):.2f} URL/сек")
            print()
            
            # Ошибки
            errors = results.get('errors', {})
            print(f"❌ ОШИБКИ:")
            print("-" * 40)
            print(f"   Всего ошибок: {errors.get('total_errors', 0)}")
            print(f"   Затронутых URL: {errors.get('affected_urls', 0)}")
            error_types = errors.get('error_types', {})
            if error_types:
                print("   Типы ошибок:")
                for error_type, count in error_types.items():
                    print(f"     {error_type}: {count}")
            print()
            
            # Статистика скрапера
            scraper_stats = scraper.get_scraping_stats()
            print(f"🔧 СТАТИСТИКА СКРАПЕРА:")
            print("-" * 40)
            print(f"   Посещенных URL: {scraper_stats.get('visited_urls_count', 0)}")
            print(f"   Размер кеша: {scraper_stats.get('cache_size', 0)}")
            print(f"   Доменов в rate limiter: {scraper_stats.get('rate_limiter_stats', {}).get('domains', 0)}")
            print()
            
            print("🎉 Демонстрация завершена успешно!")
            
    except Exception as e:
        print(f"❌ Ошибка при выполнении демонстрации: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Главная функция"""
    try:
        asyncio.run(demo_enhanced_scraper())
    except KeyboardInterrupt:
        print("\n🛑 Демонстрация прервана пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
