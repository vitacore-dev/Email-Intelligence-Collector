#!/usr/bin/env python3
"""
Демонстрационный скрипт для показа возможностей 
системы академической интеллектуальности и создания цифрового двойника
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.academic_intelligence import AcademicIntelligenceCollector, AcademicDataExtractor, AcademicSearchResult
    from modules.digital_twin import DigitalTwinCreator
    print("✅ Модули импортированы успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def create_demo_academic_data():
    """Создание демонстрационных академических данных"""
    return {
        'email': 'john.smith@stanford.edu',
        'academic_profile': {
            'name': 'Dr. John Smith',
            'email': 'john.smith@stanford.edu',
            'degrees': [
                {
                    'degree': 'PhD in Computer Science',
                    'university': 'MIT',
                    'year': '2010',
                    'context': 'John Smith received his PhD in Computer Science from MIT in 2010'
                },
                {
                    'degree': 'MS in Artificial Intelligence',
                    'university': 'Stanford University',
                    'year': '2007',
                    'context': 'Master of Science in Artificial Intelligence from Stanford University in 2007'
                }
            ],
            'positions': [
                {
                    'position': 'Professor',
                    'university': 'Stanford University',
                    'department': 'Computer Science Department',
                    'context': 'Professor at Stanford University, Computer Science Department since 2015'
                },
                {
                    'position': 'Associate Professor',
                    'university': 'UC Berkeley',
                    'department': 'EECS',
                    'context': 'Associate Professor at UC Berkeley EECS from 2012-2015'
                }
            ],
            'institutions': ['Stanford University', 'MIT', 'UC Berkeley'],
            'research_areas': [
                'Artificial Intelligence', 
                'Machine Learning', 
                'Computer Vision', 
                'Deep Learning',
                'Neural Networks'
            ],
            'publications': [
                {
                    'title': 'Deep Learning for Computer Vision: A Comprehensive Survey',
                    'journal': 'Nature Machine Intelligence',
                    'year': '2023',
                    'doi': '10.1038/s42256-023-00123-x',
                    'context': 'Published comprehensive survey on deep learning applications in computer vision'
                },
                {
                    'title': 'Transformer Networks for Image Recognition',
                    'journal': 'NeurIPS',
                    'year': '2022',
                    'context': 'Groundbreaking work on applying transformer architectures to image recognition tasks'
                },
                {
                    'title': 'Federated Learning in Healthcare Applications',
                    'journal': 'Journal of Medical AI',
                    'year': '2023',
                    'context': 'Novel approach to privacy-preserving machine learning in medical settings'
                },
                {
                    'title': 'Adversarial Training for Robust Neural Networks',
                    'journal': 'ICML',
                    'year': '2021',
                    'context': 'Innovative methods for training neural networks resistant to adversarial attacks'
                }
            ],
            'academic_websites': [
                'https://scholar.google.com/citations?user=abc123',
                'https://www.researchgate.net/profile/John-Smith-123',
                'https://stanford.edu/~jsmith'
            ],
            'academic_ids': {
                'orcid': '0000-0002-1234-5678',
                'google_scholar': 'abc123def456'
            },
            'academic_rank': 'Professor'
        },
        'search_results': [
            {
                'title': 'Dr. John Smith - Stanford Faculty',
                'url': 'https://cs.stanford.edu/people/john-smith',
                'snippet': 'John Smith is a Professor of Computer Science at Stanford University. His research focuses on artificial intelligence, machine learning, and computer vision.',
                'source': 'google',
                'rank': 1,
                'academic_score': 0.95
            },
            {
                'title': 'John Smith - Google Scholar',
                'url': 'https://scholar.google.com/citations?user=abc123',
                'snippet': 'John Smith, Stanford University - Cited by 15,000+ - artificial intelligence, machine learning, computer vision',
                'source': 'google',
                'rank': 2,
                'academic_score': 0.92
            },
            {
                'title': 'Publications by John Smith - ResearchGate',
                'url': 'https://www.researchgate.net/profile/John-Smith-123',
                'snippet': 'John Smith has published 45+ papers in top-tier conferences and journals including Nature, NeurIPS, ICML',
                'source': 'google',
                'rank': 3,
                'academic_score': 0.88
            }
        ],
        'confidence_scores': {
            'overall': 0.92,
            'degrees': 0.95,
            'positions': 0.90,
            'publications': 0.88,
            'academic_status': 0.95
        },
        'analysis_summary': {
            'total_search_results': 15,
            'academic_results': 12,
            'high_confidence_results': 8,
            'platforms_found': 3,
            'degrees_found': 2,
            'positions_found': 2,
            'publications_found': 4,
            'institutions_found': 3,
            'research_areas_found': 5,
            'has_name': True,
            'has_academic_rank': True,
            'academic_ids_found': 2
        },
        'collection_timestamp': datetime.now().isoformat()
    }

async def demo_academic_intelligence():
    """Демонстрация возможностей академической интеллектуальности"""
    print("\n" + "="*70)
    print("🔬 ДЕМОНСТРАЦИЯ АКАДЕМИЧЕСКОЙ ИНТЕЛЛЕКТУАЛЬНОСТИ")
    print("="*70)
    
    # Создаем демо-данные
    demo_data = create_demo_academic_data()
    
    print(f"\n📧 Анализируемый email: {demo_data['email']}")
    print(f"👤 Идентифицированное имя: {demo_data['academic_profile']['name']}")
    
    # Показываем степени
    print(f"\n🎓 АКАДЕМИЧЕСКИЕ СТЕПЕНИ ({len(demo_data['academic_profile']['degrees'])} найдено):")
    for i, degree in enumerate(demo_data['academic_profile']['degrees'], 1):
        print(f"  {i}. {degree['degree']}")
        print(f"     📍 {degree['university']} ({degree['year']})")
    
    # Показываем должности
    print(f"\n💼 АКАДЕМИЧЕСКИЕ ДОЛЖНОСТИ ({len(demo_data['academic_profile']['positions'])} найдено):")
    for i, position in enumerate(demo_data['academic_profile']['positions'], 1):
        print(f"  {i}. {position['position']}")
        print(f"     🏛️ {position['university']} - {position['department']}")
    
    # Показываем области исследований
    print(f"\n🔬 ОБЛАСТИ ИССЛЕДОВАНИЙ ({len(demo_data['academic_profile']['research_areas'])} найдено):")
    for i, area in enumerate(demo_data['academic_profile']['research_areas'], 1):
        print(f"  {i}. {area}")
    
    # Показываем публикации
    print(f"\n📚 ПУБЛИКАЦИИ ({len(demo_data['academic_profile']['publications'])} найдено):")
    for i, pub in enumerate(demo_data['academic_profile']['publications'], 1):
        print(f"  {i}. \"{pub['title']}\"")
        print(f"     📖 {pub['journal']} ({pub['year']})")
        if pub.get('doi'):
            print(f"     🔗 DOI: {pub['doi']}")
    
    # Показываем академические профили
    print(f"\n🌐 АКАДЕМИЧЕСКИЕ ПРОФИЛИ ({len(demo_data['academic_profile']['academic_websites'])} найдено):")
    platform_names = {
        'scholar.google.com': 'Google Scholar',
        'researchgate.net': 'ResearchGate',
        'stanford.edu': 'Stanford Personal Page'
    }
    
    for i, website in enumerate(demo_data['academic_profile']['academic_websites'], 1):
        platform = next((name for domain, name in platform_names.items() if domain in website), 'Unknown Platform')
        print(f"  {i}. {platform}")
        print(f"     🔗 {website}")
    
    # Показываем метрики уверенности
    print(f"\n📊 МЕТРИКИ УВЕРЕННОСТИ:")
    confidence = demo_data['confidence_scores']
    print(f"  🎯 Общая уверенность: {confidence['overall']:.1%}")
    print(f"  🎓 Степени: {confidence['degrees']:.1%}")
    print(f"  💼 Должности: {confidence['positions']:.1%}")
    print(f"  📚 Публикации: {confidence['publications']:.1%}")
    print(f"  🏛️ Академический статус: {confidence['academic_status']:.1%}")
    
    return demo_data

async def demo_digital_twin_creation(academic_data):
    """Демонстрация создания цифрового двойника"""
    print("\n" + "="*70)
    print("🤖 СОЗДАНИЕ ЦИФРОВОГО ДВОЙНИКА")
    print("="*70)
    
    print("\n⏳ Анализируем собранные данные и создаем цифрового двойника...")
    
    # Создаем цифрового двойника
    twin_creator = DigitalTwinCreator()
    digital_twin = twin_creator.create_digital_twin(
        academic_data['email'],
        academic_data,
        academic_data['search_results']
    )
    
    print(f"✅ Цифровой двойник создан для {digital_twin.email}")
    
    # Основная информация
    print(f"\n👤 ОСНОВНАЯ ИНФОРМАЦИЯ:")
    print(f"  📧 Email: {digital_twin.email}")
    print(f"  👤 Имя: {digital_twin.name}")
    print(f"  🏛️ Основная аффилиация: {digital_twin.primary_affiliation}")
    
    # Профиль личности
    print(f"\n🧠 ПРОФИЛЬ ЛИЧНОСТИ:")
    personality = digital_twin.personality_profile
    print(f"  🎭 Стадия карьеры: {personality.career_stage}")
    print(f"  🎯 Уровень экспертизы: {personality.expertise_level}")
    print(f"  💬 Стиль коммуникации: {personality.communication_style}")
    print(f"  🔬 Фокус исследований: {personality.research_focus}")
    print(f"  🤝 Склонность к сотрудничеству: {personality.collaboration_tendency}")
    print(f"  💻 Цифровое присутствие: {personality.digital_presence}")
    
    # Сетевой анализ
    print(f"\n🕸️ СЕТЕВОЙ АНАЛИЗ:")
    network = digital_twin.network_analysis
    print(f"  👥 Размер сети: {network.network_size}")
    print(f"  📈 Показатель влияния: {network.influence_score:.2f}")
    print(f"  🎯 Показатель центральности: {network.centrality_score:.2f}")
    print(f"  🏛️ Институции ({len(network.institutions)}): {', '.join(network.institutions[:3])}")
    if len(network.collaborators) > 0:
        print(f"  🤝 Ключевые коллабораторы: {', '.join(network.collaborators[:3])}")
    
    # Карьерная траектория
    print(f"\n📈 КАРЬЕРНАЯ ТРАЕКТОРИЯ:")
    career = digital_twin.career_trajectory
    print(f"  📊 Прогрессия карьеры: {career.career_progression}")
    if career.experience_years:
        print(f"  ⏱️ Лет опыта: {career.experience_years}")
    print(f"  🎯 Ключевые вехи: {len(career.career_milestones)}")
    for milestone in career.career_milestones[:3]:
        print(f"    • {milestone['description']} ({milestone['year']})")
    
    # Метрики воздействия
    print(f"\n💥 МЕТРИКИ ВОЗДЕЙСТВИЯ:")
    impact = digital_twin.impact_metrics
    print(f"  🌟 Общий балл воздействия: {impact.overall_impact_score:.2f}")
    print(f"  📚 Влияние через публикации:")
    citation = impact.citation_impact
    print(f"    • Публикаций: {citation.get('publication_count', 0)}")
    print(f"    • Примерные цитирования: {citation.get('estimated_citations', 0)}")
    print(f"    • Оценка h-index: {citation.get('h_index_estimate', 0)}")
    
    research_impact = impact.research_impact
    print(f"  🔬 Исследовательское воздействие:")
    print(f"    • Широта исследований: {research_impact.get('research_breadth', 0)}")
    print(f"    • Видимость исследований: {research_impact.get('research_visibility', 0)}")
    print(f"    • Индикаторы инновационности: {research_impact.get('innovation_indicators', 0)}")
    
    # Показатели качества
    print(f"\n📊 ПОКАЗАТЕЛИ КАЧЕСТВА:")
    print(f"  🎯 Уверенность: {digital_twin.confidence_score:.1%}")
    print(f"  📈 Полнота данных: {digital_twin.completeness_score:.1%}")
    print(f"  📡 Источников данных: {len(digital_twin.data_sources)}")
    
    return digital_twin

def demo_visualization_data(digital_twin):
    """Демонстрация данных для визуализации"""
    print("\n" + "="*70)
    print("📊 ДАННЫЕ ДЛЯ ВИЗУАЛИЗАЦИИ")
    print("="*70)
    
    viz_data = digital_twin.visualization_data
    
    print(f"\n📋 Доступные разделы визуализации ({len(viz_data)}):")
    for section in viz_data.keys():
        print(f"  📊 {section}")
    
    # Демонстрируем радарную диаграмму навыков
    if 'skill_radar' in viz_data:
        print(f"\n🎯 РАДАРНАЯ ДИАГРАММА НАВЫКОВ:")
        radar = viz_data['skill_radar']
        for category, value in zip(radar['categories'], radar['values']):
            bar_length = int(value * 20)  # Масштабируем для визуализации
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"  {category:20} |{bar}| {value:.1%}")
    
    # Демонстрируем сетевой граф
    if 'network_graph' in viz_data:
        print(f"\n🕸️ СЕТЕВОЙ ГРАФ:")
        network_graph = viz_data['network_graph']
        print(f"  👤 Узлов в сети: {len(network_graph['nodes'])}")
        print(f"  🔗 Связей: {len(network_graph['edges'])}")
        
        # Показываем типы узлов
        node_types = {}
        for node in network_graph['nodes']:
            node_type = node['type']
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        for node_type, count in node_types.items():
            print(f"    {node_type}: {count}")
    
    # Демонстрируем облако исследовательских областей
    if 'research_areas_cloud' in viz_data:
        print(f"\n☁️ ОБЛАКО ИССЛЕДОВАТЕЛЬСКИХ ОБЛАСТЕЙ:")
        cloud = viz_data['research_areas_cloud']
        for word_data in cloud['words']:
            size_indicator = "●" * min(5, word_data['size'] // 10)
            print(f"  {size_indicator} {word_data['text']}")
    
    # Демонстрируем карьерную временную линию
    if 'career_timeline' in viz_data:
        print(f"\n📅 КАРЬЕРНАЯ ВРЕМЕННАЯ ЛИНИЯ:")
        timeline = viz_data['career_timeline']
        print(f"  📈 Прогрессия карьеры: {timeline['career_progression']}")
        if timeline.get('experience_years'):
            print(f"  ⏱️ Лет опыта: {timeline['experience_years']}")
        
        events = timeline['events']
        print(f"  🎯 События ({len(events)}):")
        for event in events[:5]:  # Показываем первые 5
            importance_stars = "⭐" * min(5, event['importance'])
            print(f"    {event['year']} - {event['description']} {importance_stars}")

def demo_json_export(digital_twin):
    """Демонстрация экспорта в JSON"""
    print("\n" + "="*70)
    print("💾 ЭКСПОРТ ДАННЫХ")
    print("="*70)
    
    twin_creator = DigitalTwinCreator()
    
    # Создаем сводку
    summary = twin_creator.generate_twin_summary(digital_twin)
    
    print(f"\n📋 КРАТКАЯ СВОДКА:")
    print(f"  👤 Личность:")
    identity = summary['identity']
    for key, value in identity.items():
        print(f"    {key}: {value}")
    
    print(f"  🎓 Академический статус:")
    academic_status = summary['academic_status']
    for key, value in academic_status.items():
        print(f"    {key}: {value}")
    
    print(f"  💥 Сводка воздействия:")
    impact_summary = summary['impact_summary']
    for key, value in impact_summary.items():
        print(f"    {key}: {value}")
    
    print(f"  📊 Метрики качества:")
    quality_metrics = summary['quality_metrics']
    for key, value in quality_metrics.items():
        if isinstance(value, float):
            print(f"    {key}: {value:.1%}")
        else:
            print(f"    {key}: {value}")
    
    # Сохраняем JSON
    json_filename = f"digital_twin_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_data = twin_creator.export_twin_to_json(digital_twin)
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        f.write(json_data)
    
    print(f"\n💾 Данные экспортированы в файл: {json_filename}")
    print(f"📊 Размер файла: {len(json_data)} символов")

async def main():
    """Основная демонстрационная функция"""
    print("🚀 ДЕМОНСТРАЦИЯ EMAIL INTELLIGENCE COLLECTOR")
    print("🎯 Академическая интеллектуальность и создание цифрового двойника")
    print("="*70)
    
    try:
        # 1. Демонстрация академической интеллектуальности
        academic_data = await demo_academic_intelligence()
        
        input("\n⏯️  Нажмите Enter для продолжения...")
        
        # 2. Создание цифрового двойника
        digital_twin = await demo_digital_twin_creation(academic_data)
        
        input("\n⏯️  Нажмите Enter для просмотра данных визуализации...")
        
        # 3. Демонстрация данных визуализации
        demo_visualization_data(digital_twin)
        
        input("\n⏯️  Нажмите Enter для экспорта данных...")
        
        # 4. Экспорт данных
        demo_json_export(digital_twin)
        
        print("\n" + "="*70)
        print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("="*70)
        print("\n📋 Что было продемонстрировано:")
        print("  ✅ Извлечение академических данных (степени, должности, публикации)")
        print("  ✅ Анализ исследовательских областей и институций")
        print("  ✅ Создание цифрового двойника с анализом личности")
        print("  ✅ Сетевой анализ и карьерная траектория")
        print("  ✅ Метрики воздействия и влияния")
        print("  ✅ Данные для визуализации (графики, диаграммы)")
        print("  ✅ Экспорт в JSON формат")
        
        print("\n🔥 Ключевые особенности системы:")
        print("  • Автоматическое извлечение академической информации")
        print("  • Интеллектуальный анализ личности и поведения")
        print("  • Построение карьерной траектории")
        print("  • Сетевой анализ связей и коллабораций")
        print("  • Метрики влияния и воздействия")
        print("  • Готовые данные для фронтенд визуализации")
        print("  • API для интеграции с веб-интерфейсом")
        
        print("\n🎯 Применение:")
        print("  • Исследование академических профилей")
        print("  • Анализ экспертизы и влияния")
        print("  • Построение карт знаний")
        print("  • Поиск коллабораторов и экспертов")
        print("  • Мониторинг академической карьеры")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка в демонстрации: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
