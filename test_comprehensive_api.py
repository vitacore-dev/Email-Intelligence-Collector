#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование API endpoint для комплексного анализа email адресов
Test script for comprehensive email analysis API endpoint
"""

import requests
import json
import time
from datetime import datetime

def test_comprehensive_analysis_api():
    """Тестирование API endpoint комплексного анализа"""
    
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ API КОМПЛЕКСНОГО АНАЛИЗА EMAIL АДРЕСОВ")
    print("=" * 70)
    print()
    
    # Настройки
    api_base = "http://localhost:8001"
    test_email = "buch1202@mail.ru"
    
    # Проверяем здоровье API
    print("🏥 Проверка состояния API...")
    try:
        response = requests.get(f"{api_base}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API сервер работает")
            health_data = response.json()
            print(f"   Статус: {health_data.get('status')}")
        else:
            print(f"❌ API сервер недоступен (статус: {response.status_code})")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        print("   Убедитесь, что backend сервер запущен командой: ./start_backend.sh")
        return
    
    print()
    
    # Тест 1: Комплексный анализ
    print("🔍 Тест 1: Комплексный анализ email адреса")
    print(f"   Email: {test_email}")
    
    payload = {
        "email": test_email,
        "force_refresh": True
    }
    
    try:
        print("   Отправка запроса...")
        start_time = time.time()
        
        response = requests.post(
            f"{api_base}/api/comprehensive-analysis",
            json=payload,
            timeout=300  # 5 минут
        )
        
        end_time = time.time()
        request_time = end_time - start_time
        
        if response.status_code == 200:
            print("✅ Комплексный анализ выполнен успешно!")
            data = response.json()
            
            print(f"   Время запроса: {request_time:.2f} сек")
            print(f"   Статус: {data.get('status')}")
            print(f"   Источник: {data.get('source')}")
            
            if 'processing_time' in data:
                print(f"   Время обработки: {data['processing_time']:.2f} сек")
            
            if 'confidence_score' in data:
                print(f"   Рейтинг доверия: {data['confidence_score']:.2f}")
                
            if 'completeness_score' in data:
                print(f"   Полнота данных: {data['completeness_score']:.2f}")
            
            # Сохраняем результат
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_test_result_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"   Результат сохранен: {filename}")
            
        else:
            print(f"❌ Ошибка анализа (статус: {response.status_code})")
            print(f"   Ответ: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Превышено время ожидания (5 минут)")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    print()
    
    # Тест 2: Получение сохраненного профиля
    print("📁 Тест 2: Получение сохраненного профиля")
    try:
        response = requests.get(f"{api_base}/api/profile/{test_email}", timeout=30)
        
        if response.status_code == 200:
            print("✅ Профиль получен успешно!")
            data = response.json()
            profile_data = data.get('data', {})
            
            # Проверяем наличие комплексного анализа
            if 'comprehensive_analysis' in profile_data:
                print("   ✅ Комплексный анализ найден в профиле")
                comp_data = profile_data['comprehensive_analysis']
                if 'overall_confidence_score' in comp_data:
                    print(f"   Рейтинг доверия: {comp_data['overall_confidence_score']:.2f}")
            else:
                print("   ⚠️  Комплексный анализ не найден в профиле")
                
        else:
            print(f"❌ Ошибка получения профиля (статус: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Ошибка запроса профиля: {e}")
    
    print()
    
    # Тест 3: Статистика системы
    print("📊 Тест 3: Статистика системы")
    try:
        response = requests.get(f"{api_base}/api/stats", timeout=30)
        
        if response.status_code == 200:
            print("✅ Статистика получена успешно!")
            data = response.json()
            
            print(f"   Всего профилей: {data.get('total_profiles', 0)}")
            print(f"   Всего поисков: {data.get('total_searches', 0)}")
            
            recent_searches = data.get('recent_searches', [])
            comprehensive_searches = [s for s in recent_searches if s.get('search_type') == 'comprehensive']
            print(f"   Комплексных анализов: {len(comprehensive_searches)}")
            
        else:
            print(f"❌ Ошибка получения статистики (статус: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Ошибка запроса статистики: {e}")
    
    print()
    
    # Тест 4: Тест с кэшированием
    print("🗄️  Тест 4: Проверка кэширования")
    payload_cached = {
        "email": test_email,
        "force_refresh": False  # Используем кэш
    }
    
    try:
        print("   Запрос с использованием кэша...")
        start_time = time.time()
        
        response = requests.post(
            f"{api_base}/api/comprehensive-analysis",
            json=payload_cached,
            timeout=60
        )
        
        end_time = time.time()
        cached_request_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            source = data.get('source', 'unknown')
            
            if source == 'cache':
                print("✅ Кэширование работает корректно!")
                print(f"   Время запроса: {cached_request_time:.2f} сек (кэш)")
            else:
                print("⚠️  Данные получены не из кэша")
                print(f"   Источник: {source}")
        else:
            print(f"❌ Ошибка кэширования (статус: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования кэша: {e}")
    
    print()
    print("=" * 70)
    print("🎉 ТЕСТИРОВАНИЕ API ЗАВЕРШЕНО")
    print("=" * 70)

def test_other_endpoints():
    """Тестирование других endpoint'ов"""
    
    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ДРУГИХ API ENDPOINTS")
    print("=" * 70)
    
    api_base = "http://localhost:8001"
    test_email = "buch1202@mail.ru"
    
    endpoints = [
        ("GET", "/api/academic-profile/{email}", f"Академический профиль для {test_email}"),
        ("GET", "/api/digital-twin/{email}", f"Цифровой двойник для {test_email}"),
        ("GET", "/api/digital-twin-aggregate/{email}", f"Агрегированный цифровой двойник для {test_email}")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"\n🧪 Тестирование: {description}")
        
        url = f"{api_base}{endpoint.format(email=test_email)}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            else:
                response = requests.post(url, timeout=30)
            
            if response.status_code == 200:
                print("   ✅ Успешно")
                data = response.json()
                print(f"   Статус: {data.get('status', 'N/A')}")
            elif response.status_code == 404:
                print("   ⚠️  Данные не найдены (это нормально для новых профилей)")
            else:
                print(f"   ❌ Ошибка (статус: {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестирования API комплексного анализа email адресов\n")
    
    # Основное тестирование
    test_comprehensive_analysis_api()
    
    # Дополнительные тесты
    test_other_endpoints()
    
    print("\n✅ Все тесты завершены!")
