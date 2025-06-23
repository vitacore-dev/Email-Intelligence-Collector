from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False  # Только для SQLite
    } if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG  # Логирование SQL запросов в режиме отладки
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db() -> Session:
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Создание всех таблиц в базе данных"""
    try:
        from .models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def drop_tables():
    """Удаление всех таблиц из базы данных"""
    try:
        from .models import Base
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise

def init_database():
    """Инициализация базы данных"""
    try:
        create_tables()
        
        # Создание начальных данных
        db = SessionLocal()
        try:
            from .models import DataSource
            
            # Проверяем, есть ли уже источники данных
            existing_sources = db.query(DataSource).count()
            
            if existing_sources == 0:
                # Создаем начальные источники данных
                initial_sources = [
                    DataSource(
                        name="Google Search",
                        url="https://www.google.com",
                        is_active=True,
                        api_key_required=False,
                        rate_limit=100
                    ),
                    DataSource(
                        name="LinkedIn",
                        url="https://www.linkedin.com",
                        is_active=True,
                        api_key_required=True,
                        rate_limit=50
                    ),
                    DataSource(
                        name="Twitter",
                        url="https://twitter.com",
                        is_active=True,
                        api_key_required=True,
                        rate_limit=300
                    ),
                    DataSource(
                        name="GitHub",
                        url="https://github.com",
                        is_active=True,
                        api_key_required=True,
                        rate_limit=5000
                    ),
                    DataSource(
                        name="Facebook",
                        url="https://www.facebook.com",
                        is_active=False,
                        api_key_required=True,
                        rate_limit=200
                    )
                ]
                
                for source in initial_sources:
                    db.add(source)
                
                db.commit()
                logger.info("Initial data sources created")
            
        finally:
            db.close()
            
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_session(self) -> Session:
        """Получение новой сессии"""
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Проверка состояния базы данных"""
        try:
            db = self.get_session()
            try:
                # Простой запрос для проверки подключения
                db.execute("SELECT 1")
                return True
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Получение статистики базы данных"""
        try:
            db = self.get_session()
            try:
                from .models import EmailProfile, SearchHistory, ApiUsage
                
                stats = {
                    'total_profiles': db.query(EmailProfile).count(),
                    'total_searches': db.query(SearchHistory).count(),
                    'total_api_calls': db.query(ApiUsage).count(),
                    'verified_profiles': db.query(EmailProfile).filter(
                        EmailProfile.is_verified == True
                    ).count()
                }
                
                return stats
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """Очистка старых данных"""
        try:
            from datetime import datetime, timedelta
            from .models import SearchHistory, ApiUsage
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            db = self.get_session()
            try:
                # Удаление старой истории поиска
                deleted_searches = db.query(SearchHistory).filter(
                    SearchHistory.created_at < cutoff_date
                ).delete()
                
                # Удаление старых записей API
                deleted_api_calls = db.query(ApiUsage).filter(
                    ApiUsage.created_at < cutoff_date
                ).delete()
                
                db.commit()
                
                logger.info(f"Cleaned up {deleted_searches} search records and {deleted_api_calls} API records")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

# Глобальный экземпляр менеджера
db_manager = DatabaseManager()

