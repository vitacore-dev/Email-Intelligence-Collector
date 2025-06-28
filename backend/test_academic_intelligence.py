#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы модулей академической интеллектуальности
"""

import asyncio
import json
import sys
import os
import logging

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from modules.academic_intelligence import AcademicIntelligenceCollector, AcademicDataExtractor
    from modules.digital_twin import DigitalTwinCreator
    print("✅ Модули успешно импортированы")
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    sys.exit(1)

def test_academic_data_extractor():
    """Тест извлечения академических данных из текста"""
    print("\n🔬 Тестирование извлечения академических данных...")
    
    extractor = AcademicDataExtractor()
    
    # Тестовый текст с академической информацией
    test_text = """
    Dr. John Smith received his PhD in Computer Science from MIT in 2010. 
    He is currently a Professor at Stanford University, Department of Computer Science. 
    His research focuses on artificial intelligence and machine learning.
    He has published papers in top conferences like NeurIPS and ICML.
    John has collaborated with researchers from Google and Microsoft.
    """
    
    # Тест извлечения степеней
    degrees = extractor.extract_degrees(test_text)
    print(f"📜 Найденные степени: {len(degrees)}")
    for degree in degrees:
        print(f"  - {degree['degree']} ({degree.get('year', 'неизвестен')})")
    
    # Тест извлечения должностей
    positions = extractor.extract_positions(test_text)
    print(f"💼 Найденные должности: {len(positions)}")
    for position in positions:
        print(f"  - {position['position']} в {position.get('university', 'неизвестно')}")
    
    # Тест извлечения областей исследований
    research_areas = extractor.extract_research_areas(test_text)
    print(f"🔬 Области исследований: {research_areas}")
    
    return len(degrees) > 0 and len(positions) > 0

async def test_academic_search_simulation():
    """Симуляция академического поиска (без реальных HTTP запросов)"""
    print("\n🔍 Симуляция академического поиска...")
    
    try:
        collector = AcademicIntelligenceCollector()
        
        # Импортируем AcademicSearchResult для правильного создания объектов
        from modules.academic_intelligence import AcademicSearchResult
        
        # Создаем мок-данные для тестирования
        mock_search_results = [
            AcademicSearchResult(
                title='Dr. John Smith - Computer Science Professor',
                url='https://stanford.edu/faculty/john-smith',
                snippet='John Smith is a Professor of Computer Science at Stanford University. He received his PhD from MIT in 2010.',
                source='google',
                rank=1,
                academic_score=0.9
            ),
            AcademicSearchResult(
                title='Publications by John Smith - Google Scholar',
                url='https://scholar.google.com/citations?user=abc123',
                snippet='John Smith has published 25 papers in machine learning and artificial intelligence.',
                source='google',
                rank=2,
                academic_score=0.8
            )
        ]
        
        # Тестируем анализ результатов
        profile_data = await collector._analyze_search_results(mock_search_results, "john.smith@stanford.edu")
        
        print(f"📊 Результаты анализа:")
        print(f"  - Степени: {len(profile_data['degrees'])}")
        print(f"  - Должности: {len(profile_data['positions'])}")
        print(f"  - Институции: {profile_data['institutions']}")
        print(f"  - Области исследований: {profile_data['research_areas']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в симуляции поиска: {e}")
        return False

def test_digital_twin_creation():
    """Тест создания цифрового двойника"""
    print("\n🤖 Тестирование создания цифрового двойника...")
    
    try:
        twin_creator = DigitalTwinCreator()
        
        # Мок-данные для академического профиля
        mock_academic_data = {
            'academic_profile': {
                'email': 'john.smith@stanford.edu',
                'name': 'John Smith',
                'degrees': [
                    {
                        'degree': 'PhD',
                        'university': 'MIT',
                        'year': '2010',
                        'context': 'John Smith received his PhD in Computer Science from MIT in 2010'
                    }
                ],
                'positions': [
                    {
                        'position': 'Professor',
                        'university': 'Stanford University',
                        'department': 'Computer Science',
                        'context': 'Professor at Stanford University, Department of Computer Science'
                    }
                ],
                'institutions': ['Stanford University', 'MIT'],
                'research_areas': ['Artificial Intelligence', 'Machine Learning'],
                'publications': [
                    {
                        'title': 'Deep Learning for Computer Vision',
                        'journal': 'NeurIPS',
                        'year': '2020'
                    }
                ],
                'academic_websites': ['https://scholar.google.com/citations?user=abc123']
            },
            'confidence_scores': {
                'overall': 0.85,
                'degrees': 0.9,
                'positions': 0.8,
                'publications': 0.7
            }
        }
        
        mock_search_results = [
            {
                'title': 'Dr. John Smith - Stanford Faculty',
                'snippet': 'Professor of Computer Science specializing in AI research',
                'url': 'https://stanford.edu/faculty/john-smith',
                'academic_score': 0.9
            }
        ]
        
        # Создаем цифрового двойника
        digital_twin = twin_creator.create_digital_twin(
            'john.smith@stanford.edu',
            mock_academic_data,
            mock_search_results
        )
        
        print(f"🎭 Цифровой двойник создан:")
        print(f"  - Имя: {digital_twin.name}")
        print(f"  - Email: {digital_twin.email}")
        print(f"  - Основная аффилиация: {digital_twin.primary_affiliation}")
        print(f"  - Стадия карьеры: {digital_twin.personality_profile.career_stage}")
        print(f"  - Уровень экспертизы: {digital_twin.personality_profile.expertise_level}")
        print(f"  - Общий балл воздействия: {digital_twin.impact_metrics.overall_impact_score:.2f}")
        print(f"  - Балл уверенности: {digital_twin.confidence_score:.2f}")
        print(f"  - Балл полноты: {digital_twin.completeness_score:.2f}")
        
        # Тестируем визуализацию
        viz_data = digital_twin.visualization_data
        print(f"📊 Данные для визуализации: {len(viz_data)} разделов")
        for section in viz_data.keys():
            print(f"  - {section}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания цифрового двойника: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_imports():
    """Тест импорта API модулей"""
    print("\n🌐 Тестирование импорта API...")
    
    try:
        # Проверяем импорт основного API
        from app.main import app
        print("✅ FastAPI приложение импортировано")
        
        # Проверяем наличие новых эндпоинтов
        routes = [route.path for route in app.routes]
        expected_routes = [
            '/api/academic-search',
            '/api/digital-twin',
            '/api/academic-profile/{email}',
            '/api/digital-twin/{email}',
            '/api/visualization/{email}'
        ]
        
        missing_routes = []
        for route in expected_routes:
            if route not in routes:
                missing_routes.append(route)
        
        if missing_routes:
            print(f"❌ Отсутствующие маршруты: {missing_routes}")
            return False
        else:
            print("✅ Все новые API эндпоинты найдены")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка импорта API: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования Email Intelligence Collector (Academic Intelligence)")
    print("=" * 70)
    
    tests = [
        ("Извлечение академических данных", test_academic_data_extractor),
        ("Симуляция академического поиска", test_academic_search_simulation),
        ("Создание цифрового двойника", test_digital_twin_creation),
        ("Импорт API модулей", test_api_imports)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print(f"{'='*50}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                print(f"✅ {test_name}: ПРОЙДЕН")
            else:
                print(f"❌ {test_name}: НЕ ПРОЙДЕН")
            
            results.append((test_name, result))
            
        except Exception as e:
            print(f"❌ {test_name}: ОШИБКА - {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print(f"\n{'='*70}")
    print("📋 ИТОГОВЫЙ ОТЧЕТ")
    print(f"{'='*70}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"{test_name}: {status}")
    
    print(f"\nИтого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        return True
    else:
        print("⚠️ Некоторые тесты не пройдены")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
