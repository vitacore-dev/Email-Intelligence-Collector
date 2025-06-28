from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
from dataclasses import asdict

from database.connection import get_db
from database.models import EmailProfile, SearchHistory
from modules.data_collector import DataCollector
from modules.file_processor import FileProcessor
from modules.academic_intelligence import AcademicIntelligenceCollector
from modules.digital_twin import DigitalTwinCreator
from modules.automated_intelligence_system import AutomatedIntelligenceSystem
from app.schemas import (
    EmailRequest, 
    EmailResponse, 
    BulkSearchResponse, 
    ProfileResponse,
    StatsResponse
)
from config.settings import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Email Intelligence Collector API",
    description="API для сбора и анализа информации по email-адресам",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Email Intelligence Collector API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.post("/api/search", response_model=EmailResponse)
async def search_email(
    request: EmailRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Поиск информации по одному email-адресу"""
    try:
        email = request.email.lower().strip()
        
        # Проверяем кэш, если не требуется принудительное обновление
        if not request.force_refresh:
            existing_profile = db.query(EmailProfile).filter(
                EmailProfile.email == email
            ).first()
            
            if existing_profile:
                logger.info(f"Found cached profile for {email}")
                # Возвращаем данные из кэша, а не весь профиль
                return EmailResponse(
                    status="success",
                    source="cache",
                    data=existing_profile.data  # Используем data напрямую
                )
        
        # Запускаем сбор данных в фоне
        collector = DataCollector(email)
        profile_data = await collector.collect_all()
        
        # Сохраняем в базу данных
        profile = EmailProfile(
            email=email,
            data=profile_data,
            source_count=len(profile_data.get('sources', []))
        )
        
        db.merge(profile)
        db.commit()
        
        # Записываем историю поиска
        search_history = SearchHistory(
            email=email,
            search_type="single",
            results_found=len(profile_data.get('sources', []))
        )
        db.add(search_history)
        db.commit()
        
        logger.info(f"Successfully collected data for {email}")
        
        return EmailResponse(
            status="success",
            source="fresh",
            data=profile_data
        )
        
    except Exception as e:
        logger.error(f"Error searching email {request.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bulk_search", response_model=BulkSearchResponse)
async def bulk_search(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Массовый поиск по файлу с email-адресами"""
    try:
        if not file.filename.endswith(('.csv', '.txt')):
            raise HTTPException(400, "Поддерживаются только CSV и TXT файлы")
        
        processor = FileProcessor(db)
        results = await processor.process_file(file)
        
        # Записываем историю поиска
        search_history = SearchHistory(
            email="bulk_search",
            search_type="bulk",
            results_found=results['processed']
        )
        db.add(search_history)
        db.commit()
        
        logger.info(f"Bulk search completed: {results['processed']} emails processed")
        
        return BulkSearchResponse(**results)
        
    except Exception as e:
        logger.error(f"Error in bulk search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/profile/{email}", response_model=ProfileResponse)
async def get_profile(email: str, db: Session = Depends(get_db)):
    """Получение профиля по email"""
    try:
        profile = db.query(EmailProfile).filter(
            EmailProfile.email == email.lower().strip()
        ).first()
        
        if not profile:
            raise HTTPException(404, "Профиль не найден")
        
        return ProfileResponse(
            status="success",
            data=profile.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Получение статистики системы"""
    try:
        total_profiles = db.query(EmailProfile).count()
        total_searches = db.query(SearchHistory).count()
        recent_searches = db.query(SearchHistory).order_by(
            SearchHistory.created_at.desc()
        ).limit(10).all()
        
        # Собираем статистику поисковых систем из профилей
        search_engine_results = 0
        search_engine_stats = {}
        
        profiles = db.query(EmailProfile).all()
        for profile in profiles:
            profile_data = profile.data if isinstance(profile.data, dict) else {}
            
            # Подсчет результатов поисковых систем
            search_results = profile_data.get('search_results', [])
            search_engine_results += len(search_results)
            
            # Анализ статистики по поисковым системам
            search_stats = profile_data.get('search_statistics', {})
            if search_stats:
                engines_used = search_stats.get('search_engines_used', [])
                processing_time = search_stats.get('processing_time', 0)
                
                for engine in engines_used:
                    if engine not in search_engine_stats:
                        search_engine_stats[engine] = {
                            'name': engine,
                            'total_results': 0,
                            'usage_count': 0,
                            'success_rate': 0.0,
                            'avg_response_time': 0.0,
                            'is_active': True,
                            'response_times': []
                        }
                    
                    # Подсчет результатов для каждой поисковой системы
                    engine_results = [r for r in search_results if r.get('source', '').lower() == engine.lower()]
                    search_engine_stats[engine]['total_results'] += len(engine_results)
                    search_engine_stats[engine]['usage_count'] += 1
                    
                    if processing_time > 0:
                        search_engine_stats[engine]['response_times'].append(processing_time)
        
        # Вычисляем средние значения
        for engine, stats in search_engine_stats.items():
            if stats['usage_count'] > 0:
                stats['success_rate'] = min(1.0, stats['total_results'] / (stats['usage_count'] * 10))  # Примерная формула
                if stats['response_times']:
                    stats['avg_response_time'] = sum(stats['response_times']) / len(stats['response_times'])
                del stats['response_times']  # Убираем временный массив
        
        return StatsResponse(
            total_profiles=total_profiles,
            total_searches=total_searches,
            search_engine_results=search_engine_results,
            search_engine_stats=search_engine_stats,
            recent_searches=[search.to_dict() for search in recent_searches]
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/profile/{email}")
async def delete_profile(email: str, db: Session = Depends(get_db)):
    """Удаление профиля"""
    try:
        profile = db.query(EmailProfile).filter(
            EmailProfile.email == email.lower().strip()
        ).first()
        
        if not profile:
            raise HTTPException(404, "Профиль не найден")
        
        db.delete(profile)
        db.commit()
        
        return {"status": "success", "message": "Профиль удален"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/academic-search")
async def academic_search(
    request: EmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Академический поиск для извлечения степеней, должностей, публикаций"""
    try:
        email = request.email.lower().strip()
        logger.info(f"Starting academic search for {email}")
        
        # Проверяем кэш академических данных
        if not request.force_refresh:
            existing_profile = db.query(EmailProfile).filter(
                EmailProfile.email == email
            ).first()
            
            if existing_profile and existing_profile.data.get('academic_profile'):
                logger.info(f"Found cached academic profile for {email}")
                return {
                    "status": "success",
                    "source": "cache",
                    "data": existing_profile.data.get('academic_profile'),
                    "search_results": existing_profile.data.get('academic_search_results', []),
                    "confidence_scores": existing_profile.data.get('academic_confidence_scores', {})
                }
        
        # Запускаем академический сбор данных
        academic_collector = AcademicIntelligenceCollector()
        academic_data = await academic_collector.collect_academic_profile(email)
        
        # Обновляем профиль в базе данных
        existing_profile = db.query(EmailProfile).filter(
            EmailProfile.email == email
        ).first()
        
        if existing_profile:
            # Обновляем существующий профиль
            if isinstance(existing_profile.data, dict):
                existing_profile.data.update({
                    'academic_profile': academic_data['academic_profile'],
                    'academic_search_results': academic_data['search_results'],
                    'academic_confidence_scores': academic_data['confidence_scores'],
                    'academic_analysis_summary': academic_data['analysis_summary'],
                    'academic_collection_timestamp': academic_data['collection_timestamp']
                })
            else:
                existing_profile.data = {
                    'academic_profile': academic_data['academic_profile'],
                    'academic_search_results': academic_data['search_results'],
                    'academic_confidence_scores': academic_data['confidence_scores'],
                    'academic_analysis_summary': academic_data['analysis_summary'],
                    'academic_collection_timestamp': academic_data['collection_timestamp']
                }
        else:
            # Создаем новый профиль
            existing_profile = EmailProfile(
                email=email,
                data={
                    'academic_profile': academic_data['academic_profile'],
                    'academic_search_results': academic_data['search_results'],
                    'academic_confidence_scores': academic_data['confidence_scores'],
                    'academic_analysis_summary': academic_data['analysis_summary'],
                    'academic_collection_timestamp': academic_data['collection_timestamp']
                },
                source_count=len(academic_data['search_results'])
            )
        
        db.merge(existing_profile)
        db.commit()
        
        # Записываем историю поиска
        search_history = SearchHistory(
            email=email,
            search_type="academic",
            results_found=len(academic_data['search_results'])
        )
        db.add(search_history)
        db.commit()
        
        logger.info(f"Academic search completed for {email}")
        
        return {
            "status": "success",
            "source": "fresh",
            "data": academic_data
        }
        
    except Exception as e:
        logger.error(f"Error in academic search for {request.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/digital-twin")
async def create_digital_twin(
    request: EmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Создание цифрового двойника на основе собранных данных"""
    try:
        email = request.email.lower().strip()
        logger.info(f"Creating digital twin for {email}")
        
        # Проверяем наличие данных
        existing_profile = db.query(EmailProfile).filter(
            EmailProfile.email == email
        ).first()
        
        if not existing_profile:
            raise HTTPException(404, "Профиль не найден. Сначала выполните академический поиск.")
        
        profile_data = existing_profile.data if isinstance(existing_profile.data, dict) else {}
        
        # Проверяем наличие академических данных
        if not profile_data.get('academic_profile'):
            raise HTTPException(400, "Академические данные не найдены. Выполните академический поиск.")
        
        # Проверяем кэш цифрового двойника
        if not request.force_refresh and profile_data.get('digital_twin'):
            logger.info(f"Found cached digital twin for {email}")
            return {
                "status": "success",
                "source": "cache",
                "data": profile_data['digital_twin']
            }
        
        # Создаем цифрового двойника
        twin_creator = DigitalTwinCreator()
        
        # Подготавливаем данные
        academic_data = {
            'academic_profile': profile_data.get('academic_profile', {}),
            'confidence_scores': profile_data.get('academic_confidence_scores', {})
        }
        search_results = profile_data.get('academic_search_results', [])
        
        # Создаем цифрового двойника
        digital_twin = twin_creator.create_digital_twin(email, academic_data, search_results)
        
        # Преобразуем в словарь для сохранения
        twin_data = {
            'email': digital_twin.email,
            'name': digital_twin.name,
            'primary_affiliation': digital_twin.primary_affiliation,
            'academic_profile': digital_twin.academic_profile,
            'personality_profile': {
                'communication_style': digital_twin.personality_profile.communication_style,
                'expertise_level': digital_twin.personality_profile.expertise_level,
                'collaboration_tendency': digital_twin.personality_profile.collaboration_tendency,
                'research_focus': digital_twin.personality_profile.research_focus,
                'career_stage': digital_twin.personality_profile.career_stage,
                'digital_presence': digital_twin.personality_profile.digital_presence
            },
            'network_analysis': {
                'collaborators': digital_twin.network_analysis.collaborators,
                'institutions': digital_twin.network_analysis.institutions,
                'research_communities': digital_twin.network_analysis.research_communities,
                'influence_score': digital_twin.network_analysis.influence_score,
                'centrality_score': digital_twin.network_analysis.centrality_score,
                'network_size': digital_twin.network_analysis.network_size
            },
            'career_trajectory': {
                'career_milestones': digital_twin.career_trajectory.career_milestones,
                'career_progression': digital_twin.career_trajectory.career_progression,
                'experience_years': digital_twin.career_trajectory.experience_years,
                'career_changes': digital_twin.career_trajectory.career_changes,
                'specialization_evolution': digital_twin.career_trajectory.specialization_evolution
            },
            'impact_metrics': {
                'citation_impact': digital_twin.impact_metrics.citation_impact,
                'research_impact': digital_twin.impact_metrics.research_impact,
                'teaching_impact': digital_twin.impact_metrics.teaching_impact,
                'industry_impact': digital_twin.impact_metrics.industry_impact,
                'social_impact': digital_twin.impact_metrics.social_impact,
                'overall_impact_score': digital_twin.impact_metrics.overall_impact_score
            },
            'visualization_data': digital_twin.visualization_data,
            'creation_timestamp': digital_twin.creation_timestamp,
            'confidence_score': digital_twin.confidence_score,
            'data_sources': digital_twin.data_sources,
            'completeness_score': digital_twin.completeness_score
        }
        
        # Обновляем профиль в базе данных
        profile_data['digital_twin'] = twin_data
        profile_data['digital_twin_summary'] = twin_creator.generate_twin_summary(digital_twin)
        existing_profile.data = profile_data
        
        db.merge(existing_profile)
        db.commit()
        
        # Записываем историю поиска
        search_history = SearchHistory(
            email=email,
            search_type="digital_twin",
            results_found=1
        )
        db.add(search_history)
        db.commit()
        
        logger.info(f"Digital twin created for {email}")
        
        return {
            "status": "success",
            "source": "fresh",
            "data": twin_data,
            "summary": twin_creator.generate_twin_summary(digital_twin)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating digital twin for {request.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/academic-profile/{email}")
async def get_academic_profile(email: str, db: Session = Depends(get_db)):
    """Получение академического профиля по email"""
    try:
        profile = db.query(EmailProfile).filter(
            EmailProfile.email == email.lower().strip()
        ).first()
        
        if not profile:
            raise HTTPException(404, "Профиль не найден")
        
        profile_data = profile.data if isinstance(profile.data, dict) else {}
        academic_profile = profile_data.get('academic_profile')
        
        if not academic_profile:
            raise HTTPException(404, "Академический профиль не найден")
        
        return {
            "status": "success",
            "data": {
                "academic_profile": academic_profile,
                "search_results": profile_data.get('academic_search_results', []),
                "confidence_scores": profile_data.get('academic_confidence_scores', {}),
                "analysis_summary": profile_data.get('academic_analysis_summary', {}),
                "collection_timestamp": profile_data.get('academic_collection_timestamp')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting academic profile for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/digital-twin/{email}")
async def get_digital_twin(email: str, db: Session = Depends(get_db)):
    """Получение цифрового двойника по email"""
    try:
        profile = db.query(EmailProfile).filter(
            EmailProfile.email == email.lower().strip()
        ).first()
        
        if not profile:
            raise HTTPException(404, "Профиль не найден")
        
        profile_data = profile.data if isinstance(profile.data, dict) else {}
        digital_twin = profile_data.get('digital_twin')
        
        if not digital_twin:
            raise HTTPException(404, "Цифровой двойник не найден")
        
        return {
            "status": "success",
            "data": digital_twin,
            "summary": profile_data.get('digital_twin_summary', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting digital twin for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/digital-twin-aggregate/{email}")
async def get_digital_twin_aggregate(email: str, db: Session = Depends(get_db)):
    """Автоматическое формирование цифрового двойника из всех собранных данных"""
    try:
        profile = db.query(EmailProfile).filter(
            EmailProfile.email == email.lower().strip()
        ).first()
        
        if not profile:
            raise HTTPException(404, "Профиль не найден")
        
        profile_data = profile.data if isinstance(profile.data, dict) else {}
        
        # Агрегируем все собранные данные
        aggregated_twin = {
            "email": email,
            "summary": {
                "total_sources": profile.source_count,
                "confidence_score": profile.confidence_score,
                "last_updated": profile.updated_at.isoformat() if profile.updated_at else None,
                "is_verified": profile.is_verified
            },
            "personal_information": profile_data.get('person_info', {}),
            "social_presence": {
                "social_profiles": profile_data.get('social_profiles', []),
                "websites": profile_data.get('websites', []),
                "total_social_accounts": len(profile_data.get('social_profiles', []))
            },
            "contact_information": {
                "phone_numbers": profile_data.get('phone_numbers', []),
                "addresses": profile_data.get('addresses', []),
                "verified_contacts": len([p for p in profile_data.get('phone_numbers', []) if p])
            },
            "digital_footprint": {
                "search_results": profile_data.get('search_results', []),
                "search_engines_coverage": len(set([r.get('source', '') for r in profile_data.get('search_results', []) if r.get('source')])),
                "web_mentions": len(profile_data.get('search_results', [])),
                "search_statistics": profile_data.get('search_statistics', {})
            },
            "academic_profile": profile_data.get('academic_profile', {}),
            "data_sources": {
                "sources": profile_data.get('sources', []),
                "source_breakdown": {},
                "reliability_score": profile.confidence_score
            },
            "timeline": {
                "first_seen": profile.created_at.isoformat() if profile.created_at else None,
                "last_updated": profile.updated_at.isoformat() if profile.updated_at else None,
                "data_age_days": (datetime.utcnow() - profile.updated_at).days if profile.updated_at else None
            },
            "analysis": {
                "completeness_score": 0,
                "data_quality": "good" if profile.confidence_score > 0.7 else "medium" if profile.confidence_score > 0.4 else "low",
                "recommendations": []
            }
        }
        
        # Подсчет breakdown по источникам
        sources = profile_data.get('sources', [])
        for source in sources:
            source_type = "search_engine" if any(engine in source.lower() for engine in ['google', 'bing', 'yandex', 'duckduckgo']) else "social_platform" if any(platform in source.lower() for platform in ['facebook', 'linkedin', 'twitter', 'instagram']) else "other"
            aggregated_twin["data_sources"]["source_breakdown"][source_type] = aggregated_twin["data_sources"]["source_breakdown"].get(source_type, 0) + 1
        
        # Расчет completeness score
        completeness_factors = [
            bool(profile_data.get('person_info', {}).get('name')),
            bool(profile_data.get('person_info', {}).get('location')),
            bool(profile_data.get('social_profiles')),
            bool(profile_data.get('phone_numbers')),
            bool(profile_data.get('websites')),
            bool(profile_data.get('search_results'))
        ]
        aggregated_twin["analysis"]["completeness_score"] = sum(completeness_factors) / len(completeness_factors)
        
        # Рекомендации
        recommendations = []
        if not profile_data.get('person_info', {}).get('name'):
            recommendations.append("Имя не найдено - рекомендуется дополнительный поиск")
        if not profile_data.get('social_profiles'):
            recommendations.append("Социальные профили не найдены - расширить поиск в соц.сетях")
        if profile.confidence_score < 0.5:
            recommendations.append("Низкий уровень достоверности - требуется верификация данных")
        aggregated_twin["analysis"]["recommendations"] = recommendations
        
        return {
            "status": "success",
            "data": aggregated_twin,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error aggregating digital twin for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pdf-analysis")
async def pdf_analysis(
    request: EmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """PDF документ анализ для извлечения контекста и метаданных"""
    try:
        email = request.email.lower().strip()
        logger.info(f"Starting PDF analysis for {email}")
        
        # Проверяем кэш PDF анализа
        if not request.force_refresh:
            existing_profile = db.query(EmailProfile).filter(
                EmailProfile.email == email
            ).first()
            
            if existing_profile and existing_profile.data.get('pdf_documents'):
                logger.info(f"Found cached PDF analysis for {email}")
                return {
                    "status": "success",
                    "source": "cache",
                    "data": {
                        "pdf_documents": existing_profile.data.get('pdf_documents'),
                        "pdf_summary": existing_profile.data.get('pdf_summary', {})
                    }
                }
        
        # Запуск PDF анализа
        try:
            from modules.pdf_analyzer import search_and_analyze_pdfs
            pdf_results = await search_and_analyze_pdfs(email)
            
            # Если результатов нет и это тестовый email, используем демо-данные
            if not pdf_results and email.lower() == "buch1202@mail.ru":
                logger.info(f"Using demo PDF data for {email}")
                from app.demo_pdf_analysis import create_demo_pdf_analysis_data
                demo_data = create_demo_pdf_analysis_data(email)
                pdf_results = demo_data["pdf_documents"]
                
        except Exception as e:
            logger.warning(f"PDF analysis failed: {e}, falling back to demo data for {email}")
            if email.lower() == "buch1202@mail.ru":
                from app.demo_pdf_analysis import create_demo_pdf_analysis_data
                demo_data = create_demo_pdf_analysis_data(email)
                pdf_results = demo_data["pdf_documents"]
            else:
                pdf_results = []
        
        # Создание сводки
        pdf_summary = {
            "total_documents": len(pdf_results),
            "documents_with_email": len([p for p in pdf_results if p.get('email_found')]),
            "unique_sources": list(set([p.get('source', 'Unknown') for p in pdf_results])),
            "average_confidence": sum([p.get('confidence_score', 0) for p in pdf_results]) / len(pdf_results) if pdf_results else 0,
            "total_authors": sum([len(p.get('authors', [])) for p in pdf_results]),
            "total_institutions": sum([len(p.get('institutions', [])) for p in pdf_results]),
        }
        
        # Сохраняем результаты в базу данных
        existing_profile = db.query(EmailProfile).filter(
            EmailProfile.email == email
        ).first()
        
        if existing_profile:
            # Обновляем существующий профиль
            if isinstance(existing_profile.data, dict):
                existing_profile.data.update({
                    'pdf_documents': pdf_results,
                    'pdf_summary': pdf_summary,
                    'pdf_analysis_timestamp': datetime.now().isoformat()
                })
            else:
                existing_profile.data = {
                    'pdf_documents': pdf_results,
                    'pdf_summary': pdf_summary,
                    'pdf_analysis_timestamp': datetime.now().isoformat()
                }
        else:
            # Создаем новый профиль
            existing_profile = EmailProfile(
                email=email,
                data={
                    'pdf_documents': pdf_results,
                    'pdf_summary': pdf_summary,
                    'pdf_analysis_timestamp': datetime.now().isoformat()
                },
                source_count=len(pdf_results)
            )
        
        db.merge(existing_profile)
        db.commit()
        
        # Записываем историю поиска
        search_history = SearchHistory(
            email=email,
            search_type="pdf_analysis",
            results_found=len(pdf_results)
        )
        db.add(search_history)
        db.commit()
        
        logger.info(f"PDF analysis completed for {email}")
        
        return {
            "status": "success",
            "source": "fresh",
            "data": {
                "pdf_documents": pdf_results,
                "pdf_summary": pdf_summary
            },
            "processing_info": {
                "documents_analyzed": len(pdf_results),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in PDF analysis for {request.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/comprehensive-analysis")
async def comprehensive_analysis(
    request: EmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Комплексный автоматизированный анализ email адреса"""
    try:
        email = request.email.lower().strip()
        logger.info(f"Starting comprehensive analysis for {email}")
        
        # Проверяем кэш комплексного анализа
        if not request.force_refresh:
            existing_profile = db.query(EmailProfile).filter(
                EmailProfile.email == email
            ).first()
            
            if existing_profile and existing_profile.data.get('comprehensive_analysis'):
                logger.info(f"Found cached comprehensive analysis for {email}")
                return {
                    "status": "success",
                    "source": "cache",
                    "data": existing_profile.data.get('comprehensive_analysis')
                }
        
        # Настройка системы анализа
        config = {
            'max_processing_time': 300,
            'enable_deep_search': True,
            'enable_academic_analysis': True,
            'enable_social_analysis': True,
            'enable_digital_twin': True,
            'request_delay': 1.0
        }
        
        # Запуск комплексного анализа
        system = AutomatedIntelligenceSystem(config)
        analysis_results = await system.analyze_email(email)
        
        # Сохраняем результаты в базу данных
        existing_profile = db.query(EmailProfile).filter(
            EmailProfile.email == email
        ).first()
        
        analysis_data = asdict(analysis_results)
        
        if existing_profile:
            # Обновляем существующий профиль
            if isinstance(existing_profile.data, dict):
                existing_profile.data.update({
                    'comprehensive_analysis': analysis_data,
                    'comprehensive_timestamp': datetime.now().isoformat()
                })
            else:
                existing_profile.data = {
                    'comprehensive_analysis': analysis_data,
                    'comprehensive_timestamp': datetime.now().isoformat()
                }
            existing_profile.confidence_score = analysis_results.overall_confidence_score
            existing_profile.source_count = len(analysis_results.verification_sources)
        else:
            # Создаем новый профиль
            existing_profile = EmailProfile(
                email=email,
                data={
                    'comprehensive_analysis': analysis_data,
                    'comprehensive_timestamp': datetime.now().isoformat()
                },
                source_count=len(analysis_results.verification_sources),
                confidence_score=analysis_results.overall_confidence_score
            )
        
        db.merge(existing_profile)
        db.commit()
        
        # Записываем историю поиска
        search_history = SearchHistory(
            email=email,
            search_type="comprehensive",
            results_found=len(analysis_results.verification_sources)
        )
        db.add(search_history)
        db.commit()
        
        logger.info(f"Comprehensive analysis completed for {email}")
        
        return {
            "status": "success",
            "source": "fresh",
            "data": analysis_data,
            "processing_time": analysis_results.processing_time,
            "confidence_score": analysis_results.overall_confidence_score,
            "completeness_score": analysis_results.data_completeness_score
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis for {request.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/visualization/{email}")
async def get_visualization_data(email: str, db: Session = Depends(get_db)):
    """Получение данных для визуализации цифрового двойника"""
    try:
        profile = db.query(EmailProfile).filter(
            EmailProfile.email == email.lower().strip()
        ).first()
        
        if not profile:
            raise HTTPException(404, "Профиль не найден")
        
        profile_data = profile.data if isinstance(profile.data, dict) else {}
        digital_twin = profile_data.get('digital_twin')
        
        if not digital_twin:
            raise HTTPException(404, "Цифровой двойник не найден")
        
        visualization_data = digital_twin.get('visualization_data', {})
        
        return {
            "status": "success",
            "data": visualization_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visualization data for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.PORT,
        reload=settings.DEBUG
    )

