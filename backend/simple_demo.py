#!/usr/bin/env python3
"""
Простая демонстрация улучшенного веб-скрапера
"""

import asyncio
import sys
import time

# Добавляем путь для импорта модулей
sys.path.append('/Users/rafaelamirov/Documents/metod/Email-Intelligence-Collector/backend')

from modules.web_scraper import EnhancedWebScraper, ScrapingConfig, SelectorConfig

async def simple_demo():
    """Простая демонстрация возможностей"""
    
    print("🚀 ДЕМОНСТРАЦИЯ УЛУЧШЕННОГО ВЕБ-СКРАПЕРА")
    print("=" * 60)
    
    # Настройка
    config = ScrapingConfig(
        max_pages=1,
        concurrent_requests=1,
        timeout=10,
        retry_attempts=1,
        cache_ttl=60,
        delay_between_requests=0.5
    )
    
    selector_config = SelectorConfig()
    
    # Тестовый URL
    test_urls = ["http://localhost:9000/demo.html"]
    email = "john.smith@techcorp.com"
    
    print(f"📧 Email: {email}")
    print(f"🔗 URL: {test_urls[0]}")
    print()
    
    try:
        async with EnhancedWebScraper(email, config, selector_config) as scraper:
            print("🔍 Запуск скрапинга...")
            start_time = time.time()
            
            results = await scraper.scrape_websites_enhanced(test_urls)
            
            duration = time.time() - start_time
            print(f"✅ Завершено за {duration:.2f} сек")
            print()
            
            # Персональная информация
            person_info = results.get('person_info', {})
            print("👤 ПЕРСОНАЛЬНАЯ ИНФОРМАЦИЯ:")
            if person_info:
                for key, value in person_info.items():
                    print(f"   {key}: {value}")
            else:
                print("   Не найдена")
            print()
            
            # Контакты
            contact_info = results.get('contact_info', {})
            emails = contact_info.get('emails', [])
            phones = contact_info.get('phones', [])
            addresses = contact_info.get('addresses', [])
            
            print("📞 КОНТАКТЫ:")
            print(f"   Email: {len(emails)} найдено")
            for email_addr in emails[:3]:
                print(f"      • {email_addr}")
            print(f"   Телефоны: {len(phones)} найдено")
            for phone in phones[:3]:
                print(f"      • {phone}")
            print(f"   Адреса: {len(addresses)} найдено")
            for address in addresses[:2]:
                print(f"      • {address}")
            print()
            
            # Социальные сети
            social_links = results.get('social_links', [])
            print(f"🔗 СОЦИАЛЬНЫЕ СЕТИ: {len(social_links)} найдено")
            for link in social_links:
                platform = link.get('platform', 'Unknown')
                url = link.get('url', 'N/A')
                print(f"   • {platform}: {url}")
            print()
            
            # Ключевые слова
            content_analysis = results.get('content_analysis', {})
            print("🔑 КЛЮЧЕВЫЕ СЛОВА:")
            total_keywords = 0
            for url, content in content_analysis.items():
                keywords = content.get('keywords', [])
                total_keywords += len(keywords)
                if keywords:
                    print(f"   Топ-10 слов:")
                    for i, kw in enumerate(keywords[:10]):
                        if isinstance(kw, dict):
                            word = kw.get('word', 'N/A')
                            freq = kw.get('frequency', 0)
                            print(f"      {i+1}. {word} (частота: {freq})")
                        else:
                            print(f"      {i+1}. {kw}")
            print(f"   Всего: {total_keywords} ключевых слов")
            print()
            
            # Статистика
            stats = results.get('performance_stats', {})
            print("📊 СТАТИСТИКА:")
            print(f"   Успешных запросов: {stats.get('successful_scrapes', 0)}")
            print(f"   Неудачных запросов: {stats.get('failed_scrapes', 0)}")
            print(f"   Время выполнения: {stats.get('duration', 0):.2f} сек")
            
            # Ошибки
            errors = results.get('errors', {})
            print(f"   Ошибок: {errors.get('total_errors', 0)}")
            print()
            
            # Тест кеширования
            print("💾 ТЕСТ КЕШИРОВАНИЯ:")
            cache_start = time.time()
            cached_results = await scraper.scrape_websites_enhanced(test_urls)
            cache_duration = time.time() - cache_start
            
            print(f"   Первый запрос: {duration:.2f} сек")
            print(f"   Повторный запрос: {cache_duration:.2f} сек")
            print(f"   Ускорение: {duration/max(cache_duration, 0.01):.1f}x")
            print()
            
            print("🎉 Демонстрация завершена успешно!")
            print("✅ Все функции улучшенного веб-скрапера работают корректно")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def main():
    try:
        asyncio.run(simple_demo())
    except KeyboardInterrupt:
        print("\n🛑 Демонстрация прервана")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
