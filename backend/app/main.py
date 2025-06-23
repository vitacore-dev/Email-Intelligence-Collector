from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database.connection import get_db
from database.models import EmailProfile, SearchHistory
from modules.data_collector import DataCollector
from modules.file_processor import FileProcessor
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
                return EmailResponse(
                    status="success",
                    source="cache",
                    data=existing_profile.to_dict()
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
        
        return StatsResponse(
            total_profiles=total_profiles,
            total_searches=total_searches,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=settings.PORT,
        reload=settings.DEBUG
    )

