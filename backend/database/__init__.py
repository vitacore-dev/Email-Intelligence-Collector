"""
Database module for Email Intelligence Collector

Содержит модели данных, подключения к базе данных и миграции.
"""

from .models import (
    EmailProfile,
    SearchHistory,
    DataSource,
    ApiUsage,
    SystemStats,
    Base
)
from .connection import (
    get_db,
    create_tables,
    drop_tables,
    init_database,
    DatabaseManager,
    db_manager,
    engine,
    SessionLocal
)

__all__ = [
    'EmailProfile',
    'SearchHistory', 
    'DataSource',
    'ApiUsage',
    'SystemStats',
    'Base',
    'get_db',
    'create_tables',
    'drop_tables',
    'init_database',
    'DatabaseManager',
    'db_manager',
    'engine',
    'SessionLocal'
]

