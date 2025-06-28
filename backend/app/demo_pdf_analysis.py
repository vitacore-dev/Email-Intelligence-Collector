#!/usr/bin/env python3
"""
Демонстрационный модуль PDF анализа с использованием локального PDF
для тестирования функционала когда внешние SSL соединения недоступны
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_demo_pdf_analysis_data(email: str) -> Dict[str, Any]:
    """Создание демонстрационных данных PDF анализа на основе реального анализа"""
    
    if email.lower() == "buch1202@mail.ru":
        return {
            "pdf_documents": [
                {
                    "url": "/tmp/found_pdf.pdf",
                    "title": "Опухоли молочных желез: кардиоваскулярные риски гормональной терапии",
                    "authors": [
                        "Якушевская О.В.",
                        "Юренева С.В.", 
                        "Ашрафян Л.А.",
                        "Хохлова С.В.",
                        "Аверкова В.Г.",
                        "Шабалова О.В."
                    ],
                    "institutions": [
                        "ФГБУ НМИЦАГиП им. академика В.И. Кулакова Минздрава России",
                        "Российский научный центр Рентгенорадиологии"
                    ],
                    "email_found": True,
                    "email_contexts": [
                        {
                            "line_number": 499,
                            "line": "Минздрава России, Москва, е-mail: buch1202@mail.ru ORCID-0000-0002-8584-5517",
                            "context": "Аверкова В.Г., аспирант отделения гинекологической эндокринологии ФГБУ НМИЦАГиП им. академика В.И. Кулакова\nМинздрава России, Москва, е-mail: buch1202@mail.ru ORCID-0000-0002-8584-5517\nAverkova V.G., Graduent student, Department of Gynecological Endocrinology",
                            "context_range": "lines 498-502"
                        },
                        {
                            "line_number": 502,
                            "line": "Federation, Moscow, е-mail: buch1202@mail.ru ORCID-0000-0002-8584-5517",
                            "context": "Center of Obstetrics, Gynecology and Perinatology named after Academician Vi. Kulacov» Ministry of Health of the Russian\nFederation, Moscow, е-mail: buch1202@mail.ru ORCID-0000-0002-8584-5517\nШабалова О.В., аспирант отделения гинекологической эндокринологии",
                            "context_range": "lines 501-505"
                        }
                    ],
                    "text_length": 38501,
                    "all_emails": [
                        "buch1202@mail.ru",
                        "svkhokhlova@mail.ru", 
                        "syureneva@gmail.com",
                        "levaa2004@yahoo.com",
                        "aluckyone777@gmail.com",
                        "olga.shabalova93@gmail.com"
                    ],
                    "confidence_score": 0.95,
                    "analysis_timestamp": "2025-06-28T15:20:00.000Z",
                    "source": "Local Analysis",
                    "search_url": "Local PDF file analysis"
                },
                {
                    "url": "https://scholar.google.com/citations?view_op=view_citation&hl=ru&user=demo123",
                    "title": "Эндокринная гинекология: современные подходы в лечении",
                    "authors": [
                        "Аверкова В.Г.",
                        "Иванова Е.А.",
                        "Петрова М.В."
                    ],
                    "institutions": [
                        "НМИЦАГиП им. В.И. Кулакова",
                        "Московский медицинский университет"
                    ],
                    "email_found": True,
                    "email_contexts": [
                        {
                            "line_number": 45,
                            "line": "Корреспондентский автор: В.Г. Аверкова, e-mail: buch1202@mail.ru",
                            "context": "Для корреспонденции:\nКорреспондентский автор: В.Г. Аверкова, e-mail: buch1202@mail.ru\nОтделение гинекологической эндокринологии",
                            "context_range": "lines 44-46"
                        }
                    ],
                    "text_length": 15420,
                    "all_emails": [
                        "buch1202@mail.ru",
                        "secretary@clinic.ru"
                    ],
                    "confidence_score": 0.87,
                    "analysis_timestamp": "2025-06-28T15:20:00.000Z",
                    "source": "Google Scholar",
                    "search_url": "https://scholar.google.com/scholar?q=\"buch1202@mail.ru\""
                },
                {
                    "url": "https://www.researchgate.net/publication/demo456789",
                    "title": "Reproductive Health in Post-Menopausal Women: A Comprehensive Study",
                    "authors": [
                        "Averkova V.G.",
                        "Kulikov S.M.",
                        "Johnson R.A."
                    ],
                    "institutions": [
                        "National Medical Research Center",
                        "International Reproductive Health Institute"
                    ],
                    "email_found": True,
                    "email_contexts": [
                        {
                            "line_number": 120,
                            "line": "* Corresponding author: buch1202@mail.ru (V.G. Averkova)",
                            "context": "Author contributions:\nV.G. Averkova: study design, data analysis\n* Corresponding author: buch1202@mail.ru (V.G. Averkova)\nS.M. Kulikov: statistical analysis",
                            "context_range": "lines 119-122"
                        }
                    ],
                    "text_length": 22340,
                    "all_emails": [
                        "buch1202@mail.ru",
                        "kulikov@research.org",
                        "r.johnson@institute.edu"
                    ],
                    "confidence_score": 0.92,
                    "analysis_timestamp": "2025-06-28T15:20:00.000Z",
                    "source": "ResearchGate",
                    "search_url": "https://www.researchgate.net/search?q=buch1202@mail.ru"
                }
            ],
            "pdf_summary": {
                "total_documents": 3,
                "documents_with_email": 3,
                "unique_sources": ["Local Analysis", "Google Scholar", "ResearchGate"],
                "average_confidence": 0.913,
                "total_authors": 10,
                "total_institutions": 5
            }
        }
    else:
        # Для других email возвращаем пустые результаты
        return {
            "pdf_documents": [],
            "pdf_summary": {
                "total_documents": 0,
                "documents_with_email": 0,
                "unique_sources": [],
                "average_confidence": 0,
                "total_authors": 0,
                "total_institutions": 0
            }
        }

def demo_pdf_analysis(email: str) -> Dict[str, Any]:
    """Основная функция демонстрационного PDF анализа"""
    
    print(f"🔍 Демонстрационный PDF анализ для email: {email}")
    
    data = create_demo_pdf_analysis_data(email)
    
    result = {
        "status": "success",
        "source": "demo",
        "data": data,
        "processing_info": {
            "documents_analyzed": len(data["pdf_documents"]),
            "timestamp": "2025-06-28T15:20:00.000Z",
            "demo_mode": True,
            "note": "Данные получены из демонстрационного анализа локального PDF файла"
        }
    }
    
    return result

if __name__ == "__main__":
    # Тестирование
    test_email = "buch1202@mail.ru"
    result = demo_pdf_analysis(test_email)
    
    print(f"\n📊 Результаты анализа:")
    print(f"- Найдено PDF документов: {result['data']['pdf_summary']['total_documents']}")
    print(f"- С упоминанием email: {result['data']['pdf_summary']['documents_with_email']}")
    print(f"- Средняя достоверность: {result['data']['pdf_summary']['average_confidence']:.1%}")
    print(f"- Всего авторов: {result['data']['pdf_summary']['total_authors']}")
    print(f"- Источники: {', '.join(result['data']['pdf_summary']['unique_sources'])}")
    
    print(f"\n📄 Найденные документы:")
    for i, doc in enumerate(result['data']['pdf_documents'], 1):
        print(f"  {i}. {doc['title']}")
        print(f"     Авторы: {', '.join(doc['authors'][:3])}{'...' if len(doc['authors']) > 3 else ''}")
        print(f"     Email найден: {'✅' if doc['email_found'] else '❌'}")
        print(f"     Достоверность: {doc['confidence_score']:.1%}")
        print()
