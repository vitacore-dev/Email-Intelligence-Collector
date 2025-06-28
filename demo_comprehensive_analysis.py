#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрационный скрипт для комплексной системы анализа email адресов
Comprehensive Email Intelligence Analysis Demo Script
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Добавляем backend в путь
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.modules.automated_intelligence_system import AutomatedIntelligenceSystem, analyze_email_comprehensive

async def demo_comprehensive_analysis():
    """Демонстрация комплексного анализа email адреса"""
    
    print("=" * 80)
    print("ДЕМОНСТРАЦИЯ КОМПЛЕКСНОЙ СИСТЕМЫ АНАЛИЗА EMAIL АДРЕСОВ")
    print("=" * 80)
    print()
    
    # Тестовый email адрес
    test_email = "buch1202@mail.ru"
    print(f"🎯 Целевой email адрес: {test_email}")
    print()
    
    # Конфигурация системы
    config = {
        'max_processing_time': 180,  # 3 минуты
        'enable_deep_search': True,
        'enable_academic_analysis': True,
        'enable_social_analysis': True,
        'enable_digital_twin': True,
        'request_delay': 1.0,
        'max_concurrent_requests': 3
    }
    
    print("⚙️  Конфигурация системы:")
    for key, value in config.items():
        print(f"   • {key}: {value}")
    print()
    
    # Инициализация системы
    print("🚀 Инициализация автоматизированной системы анализа...")
    system = AutomatedIntelligenceSystem(config)
    
    try:
        # Запуск комплексного анализа
        print("📊 Запуск комплексного анализа...")
        print("   Это может занять несколько минут...")
        print()
        
        start_time = datetime.now()
        results = await system.analyze_email(test_email)
        end_time = datetime.now()
        
        # Отображение результатов
        print("✅ АНАЛИЗ ЗАВЕРШЕН!")
        print("=" * 80)
        print()
        
        print("📈 СВОДКА РЕЗУЛЬТАТОВ:")
        print(f"   • Email адрес: {results.email}")
        print(f"   • Время обработки: {results.processing_time:.2f} секунд")
        print(f"   • Общий рейтинг доверия: {results.overall_confidence_score:.2f}/1.0")
        print(f"   • Полнота данных: {results.data_completeness_score:.2f}/1.0")
        print(f"   • Источники верификации: {len(results.verification_sources)}")
        print()
        
        # Валидация email
        print("📧 ВАЛИДАЦИЯ EMAIL:")
        email_valid = results.email_validation.get('is_valid', False)
        print(f"   • Валидный: {'✅ Да' if email_valid else '❌ Нет'}")
        print(f"   • Домен: {results.email_validation.get('domain', 'N/A')}")
        print(f"   • Тип домена: {_get_domain_type(results.email_validation)}")
        print()
        
        # Ключевые находки
        print("🔍 КЛЮЧЕВЫЕ НАХОДКИ:")
        if results.key_findings:
            for finding in results.key_findings:
                print(f"   • {finding}")
        else:
            print("   • Ключевые находки не обнаружены")
        print()
        
        # Академический профиль
        print("🎓 АКАДЕМИЧЕСКИЙ АНАЛИЗ:")
        if results.academic_profile:
            institution = results.academic_profile.get('institution', 'N/A')
            orcid = results.academic_profile.get('orcid_id', 'N/A')
            print(f"   • Учреждение: {institution}")
            print(f"   • ORCID ID: {orcid}")
            print(f"   • Публикации: {len(results.academic_publications)}")
        else:
            print("   • Академическая информация не найдена")
        print()
        
        # Социальные сети
        print("🌐 СОЦИАЛЬНЫЕ СЕТИ:")
        if results.social_profiles:
            print(f"   • Найдено профилей: {len(results.social_profiles)}")
            for profile in results.social_profiles[:3]:  # Показываем первые 3
                platform = profile.get('platform', 'Unknown')
                url = profile.get('url', 'N/A')
                print(f"   • {platform}: {url}")
        else:
            print("   • Социальные профили не найдены")
        print()
        
        # Цифровой двойник
        print("🤖 ЦИФРОВОЙ ДВОЙНИК:")
        if results.digital_twin:
            personality = results.personality_analysis.get('communication_style', 'N/A')
            network_size = results.network_analysis.get('network_size', 0)
            print(f"   • Стиль коммуникации: {personality}")
            print(f"   • Размер сети: {network_size}")
            print(f"   • Цифровой двойник создан: ✅")
        else:
            print("   • Цифровой двойник не создан")
        print()
        
        # Источники верификации
        print("✅ ИСТОЧНИКИ ВЕРИФИКАЦИИ:")
        if results.verification_sources:
            for source in results.verification_sources:
                print(f"   • {source}")
        else:
            print("   • Источники верификации отсутствуют")
        print()
        
        # Рекомендации
        print("💡 РЕКОМЕНДАЦИИ:")
        if results.recommendations:
            for recommendation in results.recommendations:
                print(f"   • {recommendation}")
        else:
            print("   • Дополнительные рекомендации отсутствуют")
        print()
        
        # Индикаторы риска
        print("⚠️  ИНДИКАТОРЫ РИСКА:")
        if results.risk_indicators:
            for risk in results.risk_indicators:
                print(f"   • {risk}")
        else:
            print("   • Индикаторы риска не обнаружены")
        print()
        
        # Сохранение результатов
        print("💾 СОХРАНЕНИЕ РЕЗУЛЬТАТОВ:")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Сохраняем JSON
        json_path = f"comprehensive_analysis_{test_email.replace('@', '_at_')}_{timestamp}.json"
        system.save_results(json_path)
        print(f"   • JSON результаты: {json_path}")
        
        # Генерируем отчет
        report = system.generate_report()
        report_path = f"comprehensive_report_{test_email.replace('@', '_at_')}_{timestamp}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"   • Отчет в Markdown: {report_path}")
        print()
        
        print("=" * 80)
        print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 80)
        
        return results
        
    except Exception as e:
        print(f"❌ ОШИБКА АНАЛИЗА: {str(e)}")
        print("=" * 80)
        return None

def _get_domain_type(validation_data):
    """Определение типа домена"""
    if validation_data.get('is_academic_domain'):
        return "Академический"
    elif validation_data.get('is_corporate_domain'):
        return "Корпоративный"
    elif validation_data.get('is_public_domain'):
        return "Публичный почтовый провайдер"
    else:
        return "Неизвестный"

async def test_api_endpoint():
    """Тестирование API endpoint"""
    import aiohttp
    
    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ API ENDPOINT")
    print("=" * 80)
    
    api_url = "http://localhost:8000/api/comprehensive-analysis"
    test_email = "buch1202@mail.ru"
    
    payload = {
        "email": test_email,
        "force_refresh": True
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📡 Отправка запроса к API: {api_url}")
            print(f"📧 Email для анализа: {test_email}")
            
            async with session.post(api_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ API ответил успешно!")
                    print(f"   • Статус: {data.get('status')}")
                    print(f"   • Источник: {data.get('source')}")
                    print(f"   • Время обработки: {data.get('processing_time', 'N/A')} сек")
                    print(f"   • Рейтинг доверия: {data.get('confidence_score', 'N/A')}")
                else:
                    print(f"❌ API ошибка: {response.status}")
                    error_text = await response.text()
                    print(f"   Детали: {error_text}")
                    
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {str(e)}")
        print("   Убедитесь, что backend сервер запущен на localhost:8000")

async def main():
    """Основная функция демонстрации"""
    
    print("🎯 ВЫБЕРИТЕ РЕЖИМ ДЕМОНСТРАЦИИ:")
    print("1. Прямой анализ через модуль")
    print("2. Тестирование API endpoint")
    print("3. Оба режима")
    print()
    
    try:
        choice = input("Введите номер (1-3): ").strip()
        print()
        
        if choice == "1" or choice == "3":
            await demo_comprehensive_analysis()
            
        if choice == "2" or choice == "3":
            await test_api_endpoint()
            
        if choice not in ["1", "2", "3"]:
            print("❌ Неверный выбор. Запуск режима 1 по умолчанию...")
            await demo_comprehensive_analysis()
            
    except KeyboardInterrupt:
        print("\n\n❌ Демонстрация прервана пользователем")
    except Exception as e:
        print(f"\n\n❌ Неожиданная ошибка: {str(e)}")

if __name__ == "__main__":
    print()
    print("🚀 Запуск демонстрации комплексной системы анализа email адресов...")
    print()
    
    # Проверяем наличие необходимых модулей
    try:
        import aiohttp
        print("✅ aiohttp доступен")
    except ImportError:
        print("⚠️  aiohttp не установлен - тестирование API будет недоступно")
    
    # Запускаем демонстрацию
    asyncio.run(main())
