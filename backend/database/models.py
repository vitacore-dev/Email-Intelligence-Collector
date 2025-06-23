from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

class EmailProfile(Base):
    """Модель профиля email-адреса"""
    
    __tablename__ = "email_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    data = Column(JSON, nullable=False)  # Основные данные профиля
    source_count = Column(Integer, default=0)  # Количество источников
    confidence_score = Column(Float, default=0.0)  # Рейтинг достоверности
    is_verified = Column(Boolean, default=False)  # Верифицирован ли профиль
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'email': self.email,
            'data': self.data,
            'source_count': self.source_count,
            'confidence_score': self.confidence_score,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<EmailProfile(email='{self.email}', sources={self.source_count})>"

class SearchHistory(Base):
    """Модель истории поисков"""
    
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    search_type = Column(String(50), nullable=False)  # 'single' или 'bulk'
    results_found = Column(Integer, default=0)
    ip_address = Column(String(45))  # IPv4 или IPv6
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'email': self.email,
            'search_type': self.search_type,
            'results_found': self.results_found,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<SearchHistory(email='{self.email}', type='{self.search_type}')>"

class DataSource(Base):
    """Модель источников данных"""
    
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    url = Column(String(500))
    is_active = Column(Boolean, default=True)
    api_key_required = Column(Boolean, default=False)
    rate_limit = Column(Integer, default=100)  # Запросов в час
    success_rate = Column(Float, default=0.0)  # Процент успешных запросов
    last_used = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'is_active': self.is_active,
            'api_key_required': self.api_key_required,
            'rate_limit': self.rate_limit,
            'success_rate': self.success_rate,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<DataSource(name='{self.name}', active={self.is_active})>"

class ApiUsage(Base):
    """Модель использования API"""
    
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    response_status = Column(Integer)
    response_time = Column(Float)  # Время ответа в секундах
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'endpoint': self.endpoint,
            'method': self.method,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'response_status': self.response_status,
            'response_time': self.response_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<ApiUsage(endpoint='{self.endpoint}', status={self.response_status})>"

class SystemStats(Base):
    """Модель системной статистики"""
    
    __tablename__ = "system_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), default='counter')  # counter, gauge, histogram
    tags = Column(JSON)  # Дополнительные теги для метрики
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_type': self.metric_type,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<SystemStats(metric='{self.metric_name}', value={self.metric_value})>"

