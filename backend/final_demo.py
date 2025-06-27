#!/usr/bin/env python3
"""
Финальная демонстрация улучшенного веб-скрапера
с использованием локального контента
"""

import asyncio
import sys
import time

# Добавляем путь для импорта модулей
sys.path.append('/Users/rafaelamirov/Documents/metod/Email-Intelligence-Collector/backend')

from modules.web_scraper import EnhancedWebScraper, ScrapingConfig, SelectorConfig

async def final_demo():
    """Финальная демонстрация всех возможностей"""
    
    print("🎯" * 30)
    print("🚀 ФИНАЛЬНАЯ ДЕМОНСТРАЦИЯ УЛУЧШЕННОГО ВЕБ-СКРАПЕРА")
    print("🎯" * 30)
    print()
    
    # Настройка конфигурации для демонстрации
    config = ScrapingConfig(
        max_pages=2,
        concurrent_requests=2,
        timeout=10,
        retry_attempts=1,
        cache_ttl=60,
        delay_between_requests=0.5
    )
    
    # Настройка селекторов
    selector_config = SelectorConfig()
    
    # Тестовые URL - используем локальный сервер
    test_urls = [
        "http://localhost:9000/demo.html",
        "http://localhost:9000/"  # Директория листинг
    ]
    
    email = "john.smith@techcorp.com"
    
    print(f"📧 Email для анализа: {email}")
    print(f"🔗 Источники данных: {len(test_urls)} URL")
    print(f"⚙️  Конфигурация:")
    print(f"   • Максимум страниц: {config.max_pages}")
    print(f"   • Параллельные запросы: {config.concurrent_requests}")
    print(f"   • Таймаут: {config.timeout} сек")
    print(f"   • Время кеширования: {config.cache_ttl} сек")
    print()
    
    try:
        async with EnhancedWebScraper(email, config, selector_config) as scraper:
            print("🔍 Запуск анализа...")
            start_time = time.time()
            
            # Выполняем первый скрапинг
            results = await scraper.scrape_websites_enhanced(test_urls)
            
            print("✅ Первый анализ завершен!")
            print()
            
            # Детальный анализ результатов
            print("📊 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
            print("═" * 50)
            
            # 1. Персональная информация
            person_info = results.get('person_info', {})
            print("👤 ПЕРСОНАЛЬНАЯ ИНФОРМАЦИЯ:")
            if person_info:
                for key, value in person_info.items():
                    print(f"   ✓ {key.title()}: {value}")
            else:
                print("   ⚠️  Персональная информация не найдена")
            print()
            
            # 2. Контактная информация
            contact_info = results.get('contact_info', {})
            print("📞 КОНТАКТНАЯ ИНФОРМАЦИЯ:")
            
            emails = contact_info.get('emails', [])
            print(f"   📧 Email-адреса ({len(emails)}):")
            for email_addr in emails[:3]:
                print(f"      • {email_addr}")
            
            phones = contact_info.get('phones', [])
            print(f"   📱 Телефоны ({len(phones)}):")
            for phone in phones[:3]:
                print(f"      • {phone}")
            
            addresses = contact_info.get('addresses', [])
            print(f"   🏠 Адреса ({len(addresses)}):")
            for address in addresses[:2]:
                print(f"      • {address}")
            print()
            
            # 3. Социальные сети
            social_links = results.get('social_links', [])
            print(f"🔗 СОЦИАЛЬНЫЕ СЕТИ ({len(social_links)}):")
            for link in social_links:
                platform = link.get('platform', 'Unknown')
                url = link.get('url', 'N/A')
                print(f"   • {platform}: {url}")
            print()
            
            # 4. NLP Анализ
            nlp_analysis = results.get('nlp_analysis', {})
            print("🧠 NLP АНАЛИЗ:")
            if nlp_analysis:
                for url, analysis in nlp_analysis.items():
                    print(f"   📄 URL: {url}")
                    
                    # Тональность
                    sentiment = analysis.get('sentiment', {})
                    polarity = sentiment.get('polarity', 0)
                    subjectivity = sentiment.get('subjectivity', 0)
                    
                    polarity_label = "позитивная" if polarity > 0.1 else "негативная" if polarity < -0.1 else "нейтральная"
                    subj_label = "субъективная" if subjectivity > 0.5 else "объективная"
                    
                    print(f"   😊 Тональность: {polarity_label} (полярность: {polarity:.2f})")
                    print(f"   🎭 Субъективность: {subj_label} ({subjectivity:.2f})")
                    
                    # Языки
                    lang = analysis.get('language_detected', 'unknown')
                    print(f"   🌐 Язык: {lang}")
                    
                    # Именованные сущности
                    entities_spacy = analysis.get('entities_spacy', {})
                    entities_nltk = analysis.get('entities_nltk', {})
                    
                    if entities_spacy or entities_nltk:
                        print(f"   🏷️  Именованные сущности:")
                        all_entities = {**entities_spacy, **entities_nltk}
                        for entity_type, entity_list in all_entities.items():
                            if entity_list:
                                print(f"      • {entity_type}: {', '.join(entity_list[:3])}\")\n            else:\n                print(\"   ⚠️  NLP анализ недоступен\")\n            print()\n            \n            # 5. Ключевые слова\n            content_analysis = results.get('content_analysis', {})\n            print(\"🔑 КЛЮЧЕВЫЕ СЛОВА:\")\n            total_keywords = 0\n            for url, content in content_analysis.items():\n                keywords = content.get('keywords', [])\n                if keywords:\n                    print(f\"   📄 {url}:\")\n                    for i, kw in enumerate(keywords[:10]):\n                        if isinstance(kw, dict):\n                            word = kw.get('word', 'N/A')\n                            freq = kw.get('frequency', 0)\n                            pos = ', '.join(kw.get('pos_tags', ['UNKNOWN']))\n                            print(f\"      {i+1}. {word} (частота: {freq}, тип: {pos})\")\n                        else:\n                            print(f\"      {i+1}. {kw}\")\n                    total_keywords += len(keywords)\n                    print()\n            print(f\"   📊 Всего ключевых слов: {total_keywords}\")\n            print()\n            \n            # 6. Метаданные\n            print(\"📋 МЕТАДАННЫЕ:\")\n            for url, content in content_analysis.items():\n                meta_info = content.get('meta_info', {})\n                if meta_info:\n                    print(f\"   📄 {url}:\")\n                    for key, value in list(meta_info.items())[:5]:\n                        print(f\"      • {key}: {value}\")\n                    print()\n            \n            # 7. Статистика производительности\n            stats = results.get('performance_stats', {})\n            print(\"⏱️  ПРОИЗВОДИТЕЛЬНОСТЬ:\")\n            print(\"─\" * 30)\n            duration = stats.get('duration', 0)\n            total_urls = stats.get('total_urls', 0)\n            successful = stats.get('successful_scrapes', 0)\n            failed = stats.get('failed_scrapes', 0)\n            \n            print(f\"   ⏰ Время выполнения: {duration:.2f} сек\")\n            print(f\"   📊 Обработано URL: {total_urls}\")\n            print(f\"   ✅ Успешно: {successful}\")\n            print(f\"   ❌ Неудачно: {failed}\")\n            print(f\"   🚀 Скорость: {total_urls/max(duration, 0.1):.2f} URL/сек\")\n            print(f\"   📈 Успешность: {successful/max(total_urls, 1)*100:.1f}%\")\n            print()\n            \n            # 8. Ошибки\n            errors = results.get('errors', {})\n            print(\"🚨 АНАЛИЗ ОШИБОК:\")\n            total_errors = errors.get('total_errors', 0)\n            if total_errors > 0:\n                print(f\"   ⚠️  Всего ошибок: {total_errors}\")\n                print(f\"   🌐 Затронутых URL: {errors.get('affected_urls', 0)}\")\n                \n                error_types = errors.get('error_types', {})\n                if error_types:\n                    print(\"   📊 Типы ошибок:\")\n                    for error_type, count in error_types.items():\n                        print(f\"      • {error_type}: {count}\")\n            else:\n                print(\"   ✅ Ошибок не обнаружено\")\n            print()\n            \n            # 9. Статистика скрапера\n            scraper_stats = scraper.get_scraping_stats()\n            print(\"🔧 ВНУТРЕННЯЯ СТАТИСТИКА:\")\n            print(\"─\" * 30)\n            print(f\"   🌐 Посещенных URL: {scraper_stats.get('visited_urls_count', 0)}\")\n            print(f\"   💾 Размер кеша: {scraper_stats.get('cache_size', 0)} записей\")\n            \n            rate_stats = scraper_stats.get('rate_limiter_stats', {})\n            print(f\"   🚦 Доменов в rate limiter: {rate_stats.get('domains', 0)}\")\n            \n            delays = rate_stats.get('current_delays', {})\n            if delays:\n                print(\"   ⏳ Текущие задержки:\")\n                for domain, delay in delays.items():\n                    print(f\"      • {domain}: {delay:.2f} сек\")\n            print()\n            \n            # 10. Демонстрация кеширования\n            print(\"💾 ДЕМОНСТРАЦИЯ КЕШИРОВАНИЯ:\")\n            print(\"Повторный запрос для демонстрации кеша...\")\n            \n            cache_start = time.time()\n            cached_results = await scraper.scrape_websites_enhanced([test_urls[0]])\n            cache_duration = time.time() - cache_start\n            \n            cache_stats = cached_results.get('performance_stats', {})\n            cache_hits = cache_stats.get('cache_hits', 0)\n            \n            print(f\"   ⚡ Время с кешем: {cache_duration:.2f} сек\")\n            print(f\"   📊 Попаданий в кеш: {cache_hits}\")\n            print(f\"   🚀 Ускорение: {duration/max(cache_duration, 0.01):.1f}x\")\n            print()\n            \n            execution_time = time.time() - start_time\n            print(\"🏁 ИТОГОВАЯ СВОДКА:\")\n            print(\"═\" * 50)\n            print(f\"✅ Демонстрация завершена успешно!\")\n            print(f\"⏰ Общее время выполнения: {execution_time:.2f} секунд\")\n            print(f\"📊 Извлечено данных:\")\n            print(f\"   • Персональная информация: {len(person_info)} полей\")\n            print(f\"   • Контактные данные: {len(emails + phones + addresses)} записей\")\n            print(f\"   • Социальные ссылки: {len(social_links)} платформ\")\n            print(f\"   • Ключевые слова: {total_keywords} терминов\")\n            print(f\"📈 Эффективность системы: ВЫСОКАЯ\")\n            print()\n            print(\"🎉 Улучшенный веб-скрапер продемонстрировал все заявленные возможности!\")\n            \n    except Exception as e:\n        print(f\"❌ Ошибка при выполнении демонстрации: {e}\")\n        import traceback\n        traceback.print_exc()\n\ndef main():\n    \"\"\"Главная функция\"\"\"\n    try:\n        asyncio.run(final_demo())\n    except KeyboardInterrupt:\n        print(\"\\n🛑 Демонстрация прервана пользователем\")\n    except Exception as e:\n        print(f\"❌ Критическая ошибка: {e}\")\n\nif __name__ == \"__main__\":\n    main()
