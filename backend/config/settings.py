from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Основные настройки
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # База данных
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/eic_db"
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "email_profiles"
    
    # Redis для кэширования и очередей
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API ключи для сбора данных
    GOOGLE_API_KEY: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    LINKEDIN_API_KEY: Optional[str] = None
    GITHUB_API_KEY: Optional[str] = None
    
    # Настройки сбора данных
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    
    # Лимиты
    MAX_BULK_EMAILS: int = 1000
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/eic.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

