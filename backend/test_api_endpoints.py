#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API эндпоинтов академической интеллектуальности
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Тест health check"""
    print("🏥 Тестирование health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check: OK")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def test_academic_search():
    """Тест академического поиска"""
    print("\n🔬 Тестирование академического поиска...")
    
    test_email = "test.professor@university.edu"
    
    payload = {
        "email": test_email,
        "force_refresh": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/academic-search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Академический поиск выполнен")
            print(f"📊 Источник данных: {data.get('source', 'unknown')}")
            
            # Проверяем структуру ответа
            if 'data' in data:
                academic_data = data['data']
                print(f"📋 Структура данных:")
                if 'academic_profile' in academic_data:
                    profile = academic_data['academic_profile']
                    print(f"  - Email: {profile.get('email', 'не найден')}")
                    print(f"  - Степени: {len(profile.get('degrees', []))}")
                    print(f"  - Должности: {len(profile.get('positions', []))}")
                    print(f"  - Институции: {len(profile.get('institutions', []))}")
                    print(f"  - Области исследований: {len(profile.get('research_areas', []))}")
                    print(f"  - Публикации: {len(profile.get('publications', []))}")
                
                if 'search_results' in academic_data:
                    print(f"  - Результаты поиска: {len(academic_data['search_results'])}")
                
                if 'confidence_scores' in academic_data:
                    confidence = academic_data['confidence_scores']
                    print(f"  - Общая уверенность: {confidence.get('overall', 0):.2f}")
            
            return True
        else:
            print(f"❌ Ошибка академического поиска: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def test_digital_twin_creation():
    """Тест создания цифрового двойника"""
    print("\n🤖 Тестирование создания цифрового двойника...")
    
    test_email = "test.professor@university.edu"
    
    payload = {
        "email": test_email,
        "force_refresh": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/digital-twin",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Цифровой двойник создан")
            print(f"📊 Источник данных: {data.get('source', 'unknown')}")
            
            # Проверяем структуру ответа
            if 'data' in data:
                twin_data = data['data']
                print(f"🎭 Информация о цифровом двойнике:")
                print(f"  - Email: {twin_data.get('email', 'не найден')}")
                print(f"  - Имя: {twin_data.get('name', 'не найдено')}")
                print(f"  - Основная аффилиация: {twin_data.get('primary_affiliation', 'не найдена')}")
                
                if 'personality_profile' in twin_data:
                    personality = twin_data['personality_profile']
                    print(f"  - Стадия карьеры: {personality.get('career_stage', 'неизвестна')}")
                    print(f"  - Уровень экспертизы: {personality.get('expertise_level', 'неизвестен')}")
                    print(f"  - Стиль коммуникации: {personality.get('communication_style', 'неизвестен')}")
                
                if 'impact_metrics' in twin_data:
                    impact = twin_data['impact_metrics']
                    print(f"  - Общий балл воздействия: {impact.get('overall_impact_score', 0):.2f}")
                
                print(f"  - Балл уверенности: {twin_data.get('confidence_score', 0):.2f}")
                print(f"  - Балл полноты: {twin_data.get('completeness_score', 0):.2f}")
            
            if 'summary' in data:
                summary = data['summary']
                print(f"📋 Краткая сводка:")
                print(f"  - Готовность визуализации: {summary.get('visualization_ready', False)}")
                if 'quality_metrics' in summary:
                    quality = summary['quality_metrics']
                    print(f"  - Источников данных: {quality.get('data_sources_count', 0)}")
            
            return True
        else:
            print(f"❌ Ошибка создания цифрового двойника: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def test_get_academic_profile():
    """Тест получения академического профиля"""
    print("\n📚 Тестирование получения академического профиля...")
    
    test_email = "test.professor@university.edu"
    
    try:
        response = requests.get(f"{BASE_URL}/api/academic-profile/{test_email}")
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Академический профиль получен")
            
            if 'data' in data:
                profile_data = data['data']
                if 'academic_profile' in profile_data:
                    profile = profile_data['academic_profile']
                    print(f"📊 Профиль содержит:")
                    print(f"  - Степени: {len(profile.get('degrees', []))}")
                    print(f"  - Должности: {len(profile.get('positions', []))}")
                    print(f"  - Институции: {len(profile.get('institutions', []))}")
                    print(f"  - Области исследований: {len(profile.get('research_areas', []))}")
            
            return True
        elif response.status_code == 404:
            print("⚠️ Академический профиль не найден (ожидаемо для первого запроса)")
            return True
        else:
            print(f"❌ Ошибка получения профиля: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def test_get_digital_twin():
    """Тест получения цифрового двойника"""
    print("\n🎭 Тестирование получения цифрового двойника...")
    
    test_email = "test.professor@university.edu"
    
    try:
        response = requests.get(f"{BASE_URL}/api/digital-twin/{test_email}")
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Цифровой двойник получен")
            
            if 'data' in data:
                twin_data = data['data']
                print(f"🎭 Цифровой двойник:")
                print(f"  - Email: {twin_data.get('email', 'не найден')}")
                print(f"  - Имя: {twin_data.get('name', 'не найдено')}")
                print(f"  - Временная метка создания: {twin_data.get('creation_timestamp', 'не найдена')}")
            
            return True
        elif response.status_code == 404:
            print("⚠️ Цифровой двойник не найден")
            return True
        else:
            print(f"❌ Ошибка получения двойника: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def test_get_visualization():
    """Тест получения данных визуализации"""
    print("\n📊 Тестирование получения данных визуализации...")
    
    test_email = "test.professor@university.edu"
    
    try:
        response = requests.get(f"{BASE_URL}/api/visualization/{test_email}")
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Данные визуализации получены")
            
            if 'data' in data:
                viz_data = data['data']
                print(f"📊 Разделы визуализации ({len(viz_data)}):")
                for section in viz_data.keys():
                    print(f"  - {section}")
            
            return True
        elif response.status_code == 404:
            print("⚠️ Данные визуализации не найдены")
            return True
        else:
            print(f"❌ Ошибка получения данных визуализации: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def main():
    """Основная функция тестирования API"""
    print("🚀 Тестирование API эндпоинтов Email Intelligence Collector")
    print("=" * 70)
    
    tests = [
        ("Health Check", test_health),
        ("Академический поиск", test_academic_search),
        ("Создание цифрового двойника", test_digital_twin_creation),
        ("Получение академического профиля", test_get_academic_profile),
        ("Получение цифрового двойника", test_get_digital_twin),
        ("Получение данных визуализации", test_get_visualization),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            
            if result:
                print(f"✅ {test_name}: ПРОЙДЕН")
            else:
                print(f"❌ {test_name}: НЕ ПРОЙДЕН")
            
            results.append((test_name, result))
            
            # Задержка между тестами
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ {test_name}: ОШИБКА - {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print(f"\n{'='*70}")
    print("📋 ИТОГОВЫЙ ОТЧЕТ API ТЕСТИРОВАНИЯ")
    print(f"{'='*70}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"{test_name}: {status}")
    
    print(f"\nИтого: {passed}/{total} тестов API пройдено")
    
    if passed == total:
        print("🎉 Все API тесты пройдены успешно!")
        return True
    else:
        print("⚠️ Некоторые API тесты не пройдены")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
