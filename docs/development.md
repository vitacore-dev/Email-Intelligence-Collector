# Руководство разработчика

Это руководство предназначено для разработчиков, которые хотят внести вклад в проект Email Intelligence Collector или создать собственные расширения.

## Архитектура проекта

### Общая архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React.js)    │◄──►│   (FastAPI)     │◄──►│ (PostgreSQL +   │
│                 │    │                 │    │  Elasticsearch) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │ Data Collectors │              │
         │              │ (Async Workers) │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Redis       │    │   External APIs │    │   File Storage  │
│   (Caching)     │    │ (Social Media)  │    │   (Uploads)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Backend архитектура

```
backend/
├── app/                    # FastAPI приложение
│   ├── main.py            # Точка входа
│   ├── schemas.py         # Pydantic модели
│   └── dependencies.py    # Зависимости FastAPI
├── modules/               # Бизнес-логика
│   ├── data_collector.py  # Основной коллектор
│   ├── social_collectors.py # Коллекторы соц. сетей
│   ├── web_scraper.py     # Веб-скрапинг
│   ├── email_validator.py # Валидация email
│   └── file_processor.py  # Обработка файлов
├── database/              # Слой данных
│   ├── models.py          # SQLAlchemy модели
│   ├── connection.py      # Подключение к БД
│   └── migrations/        # Alembic миграции
└── config/                # Конфигурация
    └── settings.py        # Настройки приложения
```

### Frontend архитектура

```
frontend/src/
├── components/            # React компоненты
│   ├── ui/               # Базовые UI компоненты
│   ├── forms/            # Формы
│   └── layout/           # Компоненты макета
├── pages/                # Страницы приложения
├── services/             # API сервисы
├── hooks/                # Кастомные React хуки
├── utils/                # Утилиты
└── types/                # TypeScript типы
```

## Настройка среды разработки

### Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Git

### Клонирование и настройка

```bash
# Клонирование репозитория
git clone https://github.com/vitacore-dev/Email-Intelligence-Collector.git
cd Email-Intelligence-Collector

# Создание ветки для разработки
git checkout -b feature/your-feature-name
```

### Backend разработка

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Установка зависимостей для разработки
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Настройка pre-commit хуков
pre-commit install

# Копирование конфигурации
cp .env.example .env
```

### Frontend разработка

```bash
cd frontend

# Установка зависимостей
npm install

# Настройка переменных окружения
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
```

### База данных

```bash
# Создание базы данных для разработки
createdb eic_dev

# Запуск миграций
cd backend
alembic upgrade head

# Заполнение тестовыми данными
python scripts/seed_data.py
```

## Стандарты кодирования

### Python (Backend)

#### Форматирование
Используем **Black** для форматирования:
```bash
black --line-length 88 .
```

#### Линтинг
Используем **flake8** и **mypy**:
```bash
flake8 .
mypy .
```

#### Импорты
Сортировка импортов с **isort**:
```bash
isort .
```

#### Пример кода
```python
from typing import Dict, List, Optional
import asyncio
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class DataCollector:
    """Коллектор данных с типизацией и документацией."""
    
    def __init__(self, email: str) -> None:
        self.email = email.lower().strip()
        self.results: Dict[str, Any] = {}
    
    async def collect_data(self) -> Optional[Dict[str, Any]]:
        """
        Сбор данных по email-адресу.
        
        Returns:
            Словарь с собранными данными или None при ошибке.
            
        Raises:
            HTTPException: При ошибке валидации email.
        """
        try:
            # Логика сбора данных
            return self.results
        except Exception as e:
            logger.error(f"Error collecting data for {self.email}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
```

### JavaScript/TypeScript (Frontend)

#### Форматирование
Используем **Prettier**:
```bash
npm run format
```

#### Линтинг
Используем **ESLint**:
```bash
npm run lint
```

#### Пример компонента
```tsx
import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useEmailSearch } from '@/hooks/useEmailSearch';

interface EmailSearchProps {
  onResult: (data: EmailData) => void;
}

export const EmailSearch: React.FC<EmailSearchProps> = ({ onResult }) => {
  const [email, setEmail] = useState('');
  const { searchEmail, isLoading, error } = useEmailSearch();

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const result = await searchEmail(email);
      onResult(result);
    } catch (err) {
      console.error('Search failed:', err);
    }
  }, [email, searchEmail, onResult]);

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter email address"
        required
      />
      <Button type="submit" disabled={isLoading}>
        {isLoading ? 'Searching...' : 'Search'}
      </Button>
      {error && <p className="text-red-500">{error}</p>}
    </form>
  );
};
```

## Тестирование

### Backend тесты

#### Структура тестов
```
backend/tests/
├── unit/                  # Юнит-тесты
│   ├── test_collectors.py
│   ├── test_validators.py
│   └── test_models.py
├── integration/           # Интеграционные тесты
│   ├── test_api.py
│   └── test_database.py
└── fixtures/              # Тестовые данные
    └── sample_data.json
```

#### Запуск тестов
```bash
# Все тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html

# Конкретный тест
pytest tests/unit/test_collectors.py::test_email_validation
```

#### Пример теста
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from modules.email_validator import EmailValidator

client = TestClient(app)


class TestEmailValidator:
    """Тесты валидатора email."""
    
    def test_valid_email(self):
        """Тест валидного email."""
        assert EmailValidator.is_valid("test@example.com") is True
    
    def test_invalid_email(self):
        """Тест невалидного email."""
        assert EmailValidator.is_valid("invalid-email") is False
    
    @pytest.mark.parametrize("email,expected", [
        ("user@domain.com", True),
        ("user.name@domain.co.uk", True),
        ("user+tag@domain.com", True),
        ("@domain.com", False),
        ("user@", False),
        ("", False),
    ])
    def test_email_validation_cases(self, email, expected):
        """Параметризованный тест различных случаев."""
        assert EmailValidator.is_valid(email) is expected


class TestSearchAPI:
    """Тесты API поиска."""
    
    def test_search_valid_email(self):
        """Тест поиска с валидным email."""
        response = client.post(
            "/api/search",
            json={"email": "test@example.com", "force_refresh": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_search_invalid_email(self):
        """Тест поиска с невалидным email."""
        response = client.post(
            "/api/search",
            json={"email": "invalid-email", "force_refresh": False}
        )
        assert response.status_code == 400
```

### Frontend тесты

#### Структура тестов
```
frontend/src/
├── __tests__/             # Тесты
│   ├── components/
│   ├── hooks/
│   └── utils/
└── __mocks__/             # Моки
    └── api.ts
```

#### Запуск тестов
```bash
# Все тесты
npm test

# С покрытием
npm run test:coverage

# В watch режиме
npm run test:watch
```

#### Пример теста
```tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EmailSearch } from '@/components/EmailSearch';
import { useEmailSearch } from '@/hooks/useEmailSearch';

// Мок хука
jest.mock('@/hooks/useEmailSearch');
const mockUseEmailSearch = useEmailSearch as jest.MockedFunction<typeof useEmailSearch>;

describe('EmailSearch', () => {
  const mockOnResult = jest.fn();
  const mockSearchEmail = jest.fn();

  beforeEach(() => {
    mockUseEmailSearch.mockReturnValue({
      searchEmail: mockSearchEmail,
      isLoading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders email input and search button', () => {
    render(<EmailSearch onResult={mockOnResult} />);
    
    expect(screen.getByPlaceholderText('Enter email address')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
  });

  it('calls searchEmail when form is submitted', async () => {
    const testEmail = 'test@example.com';
    const mockResult = { email: testEmail, data: {} };
    
    mockSearchEmail.mockResolvedValue(mockResult);
    
    render(<EmailSearch onResult={mockOnResult} />);
    
    const input = screen.getByPlaceholderText('Enter email address');
    const button = screen.getByRole('button', { name: 'Search' });
    
    fireEvent.change(input, { target: { value: testEmail } });
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(mockSearchEmail).toHaveBeenCalledWith(testEmail);
      expect(mockOnResult).toHaveBeenCalledWith(mockResult);
    });
  });
});
```

## Добавление новых функций

### Создание нового коллектора

1. **Создайте класс коллектора**:
```python
# backend/modules/collectors/instagram_collector.py
from .base_collector import BaseCollector

class InstagramCollector(BaseCollector):
    """Коллектор для Instagram."""
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """Сбор данных из Instagram."""
        # Реализация логики сбора
        pass
```

2. **Добавьте в основной коллектор**:
```python
# backend/modules/data_collector.py
from .collectors.instagram_collector import InstagramCollector

class DataCollector:
    def _init_collectors(self):
        self.collectors = [
            # ... существующие коллекторы
            InstagramCollector(self.email),
        ]
```

3. **Добавьте тесты**:
```python
# backend/tests/unit/test_instagram_collector.py
class TestInstagramCollector:
    def test_collect_data(self):
        # Тесты коллектора
        pass
```

### Добавление нового API endpoint

1. **Создайте endpoint**:
```python
# backend/app/main.py
@app.get("/api/sources")
async def get_data_sources(db: Session = Depends(get_db)):
    """Получение списка источников данных."""
    sources = db.query(DataSource).all()
    return [source.to_dict() for source in sources]
```

2. **Добавьте схему**:
```python
# backend/app/schemas.py
class DataSourceResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    success_rate: float
```

3. **Добавьте тесты**:
```python
# backend/tests/integration/test_sources_api.py
def test_get_data_sources():
    response = client.get("/api/sources")
    assert response.status_code == 200
```

### Добавление нового React компонента

1. **Создайте компонент**:
```tsx
// frontend/src/components/DataSourcesList.tsx
import React from 'react';
import { Card } from '@/components/ui/card';

interface DataSource {
  id: number;
  name: string;
  isActive: boolean;
  successRate: number;
}

interface DataSourcesListProps {
  sources: DataSource[];
}

export const DataSourcesList: React.FC<DataSourcesListProps> = ({ sources }) => {
  return (
    <div className="grid gap-4">
      {sources.map((source) => (
        <Card key={source.id} className="p-4">
          <h3 className="font-semibold">{source.name}</h3>
          <p>Success Rate: {(source.successRate * 100).toFixed(1)}%</p>
          <span className={`badge ${source.isActive ? 'active' : 'inactive'}`}>
            {source.isActive ? 'Active' : 'Inactive'}
          </span>
        </Card>
      ))}
    </div>
  );
};
```

2. **Добавьте хук для API**:
```tsx
// frontend/src/hooks/useDataSources.ts
import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';

export const useDataSources = () => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSources = async () => {
      try {
        const data = await apiService.getDataSources();
        setSources(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSources();
  }, []);

  return { sources, loading, error };
};
```

3. **Добавьте тесты**:
```tsx
// frontend/src/__tests__/components/DataSourcesList.test.tsx
import { render, screen } from '@testing-library/react';
import { DataSourcesList } from '@/components/DataSourcesList';

const mockSources = [
  { id: 1, name: 'Google', isActive: true, successRate: 0.95 },
  { id: 2, name: 'LinkedIn', isActive: false, successRate: 0.80 },
];

describe('DataSourcesList', () => {
  it('renders list of data sources', () => {
    render(<DataSourcesList sources={mockSources} />);
    
    expect(screen.getByText('Google')).toBeInTheDocument();
    expect(screen.getByText('LinkedIn')).toBeInTheDocument();
    expect(screen.getByText('Success Rate: 95.0%')).toBeInTheDocument();
  });
});
```

## База данных

### Создание миграций

```bash
# Создание новой миграции
cd backend
alembic revision --autogenerate -m "Add new table"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

### Пример миграции
```python
# backend/database/migrations/versions/001_add_user_preferences.py
"""Add user preferences table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_user_preferences_user_id'), table_name='user_preferences')
    op.drop_table('user_preferences')
```

## Развертывание

### Docker разработка

```bash
# Сборка образов
docker-compose -f docker-compose.dev.yml build

# Запуск в режиме разработки
docker-compose -f docker-compose.dev.yml up

# Просмотр логов
docker-compose logs -f backend
```

### CI/CD Pipeline

Пример GitHub Actions:
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
    
    - name: Build
      run: |
        cd frontend
        npm run build
```

## Мониторинг и логирование

### Структурированное логирование

```python
import structlog

logger = structlog.get_logger()

async def collect_data(email: str):
    logger.info(
        "Starting data collection",
        email=email,
        collector="DataCollector"
    )
    
    try:
        # Логика сбора
        result = await some_operation()
        
        logger.info(
            "Data collection completed",
            email=email,
            sources_count=len(result.get('sources', [])),
            duration=time.time() - start_time
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Data collection failed",
            email=email,
            error=str(e),
            exc_info=True
        )
        raise
```

### Метрики

```python
from prometheus_client import Counter, Histogram, Gauge

# Счетчики
search_requests_total = Counter(
    'search_requests_total',
    'Total number of search requests',
    ['method', 'status']
)

# Гистограммы
search_duration = Histogram(
    'search_duration_seconds',
    'Time spent on search requests'
)

# Датчики
active_searches = Gauge(
    'active_searches',
    'Number of currently active searches'
)

# Использование
@search_duration.time()
async def search_email(email: str):
    search_requests_total.labels(method='single', status='started').inc()
    active_searches.inc()
    
    try:
        result = await perform_search(email)
        search_requests_total.labels(method='single', status='success').inc()
        return result
    except Exception as e:
        search_requests_total.labels(method='single', status='error').inc()
        raise
    finally:
        active_searches.dec()
```

## Безопасность

### Валидация входных данных

```python
from pydantic import BaseModel, validator, EmailStr

class EmailSearchRequest(BaseModel):
    email: EmailStr
    force_refresh: bool = False
    
    @validator('email')
    def validate_email_domain(cls, v):
        """Дополнительная валидация домена."""
        domain = v.split('@')[1]
        if domain in BLOCKED_DOMAINS:
            raise ValueError('Domain is blocked')
        return v

class BulkSearchRequest(BaseModel):
    max_emails: int = 1000
    
    @validator('max_emails')
    def validate_max_emails(cls, v):
        if v > 10000:
            raise ValueError('Too many emails')
        return v
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/search")
@limiter.limit("60/minute")
async def search_email(request: Request, email_request: EmailRequest):
    # Логика поиска
    pass
```

## Производительность

### Асинхронная обработка

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class DataCollector:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def collect_all_sources(self, email: str):
        """Параллельный сбор из всех источников."""
        tasks = []
        
        for collector in self.collectors:
            task = asyncio.create_task(
                self.safe_collect(collector, email)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self.merge_results(results)
    
    async def safe_collect(self, collector, email):
        """Безопасный сбор с таймаутом."""
        try:
            return await asyncio.wait_for(
                collector.collect(email),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            logger.warning(f"Timeout for {collector.__class__.__name__}")
            return None
        except Exception as e:
            logger.error(f"Error in {collector.__class__.__name__}: {e}")
            return None
```

### Кэширование

```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=3600):
    """Декоратор для кэширования результатов."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создание ключа кэша
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Попытка получить из кэша
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Выполнение функции
            result = await func(*args, **kwargs)
            
            # Сохранение в кэш
            redis_client.setex(
                cache_key,
                expiration,
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

@cache_result(expiration=1800)  # 30 минут
async def search_email(email: str):
    # Логика поиска
    pass
```

## Отладка

### Настройка отладчика

#### VS Code
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/backend/app/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/backend"
            }
        }
    ]
}
```

#### PyCharm
1. Создайте новую конфигурацию запуска
2. Выберите "Python"
3. Script path: `backend/app/main.py`
4. Working directory: `backend/`

### Профилирование

```python
import cProfile
import pstats
from functools import wraps

def profile(func):
    """Декоратор для профилирования функций."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        
        result = func(*args, **kwargs)
        
        pr.disable()
        stats = pstats.Stats(pr)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Топ 10 функций
        
        return result
    return wrapper

@profile
def slow_function():
    # Функция для профилирования
    pass
```

## Документация

### Автогенерация документации API

FastAPI автоматически генерирует документацию, но вы можете её настроить:

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Email Intelligence Collector API",
        version="1.0.0",
        description="API для сбора информации по email-адресам",
        routes=app.routes,
    )
    
    # Кастомизация схемы
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Документация кода

```python
def collect_email_data(email: str, sources: List[str] = None) -> Dict[str, Any]:
    """
    Сбор данных по email-адресу из указанных источников.
    
    Args:
        email: Email-адрес для поиска. Должен быть валидным.
        sources: Список источников для поиска. Если None, используются все доступные.
    
    Returns:
        Словарь с собранными данными:
        {
            'email': str,
            'person_info': dict,
            'social_profiles': list,
            'sources': list,
            'confidence_score': float
        }
    
    Raises:
        ValueError: Если email невалиден.
        HTTPException: Если произошла ошибка при сборе данных.
    
    Example:
        >>> data = collect_email_data('user@example.com')
        >>> print(data['person_info']['name'])
        'John Doe'
    """
    pass
```

## Вклад в проект

### Процесс разработки

1. **Fork репозитория**
2. **Создайте feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Внесите изменения**
4. **Добавьте тесты**
5. **Запустите линтеры**:
   ```bash
   # Backend
   cd backend
   black .
   flake8 .
   mypy .
   
   # Frontend
   cd frontend
   npm run lint
   npm run format
   ```
6. **Запустите тесты**:
   ```bash
   # Backend
   pytest
   
   # Frontend
   npm test
   ```
7. **Commit изменения**:
   ```bash
   git commit -m "feat: add amazing feature"
   ```
8. **Push в ваш fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
9. **Создайте Pull Request**

### Соглашения о коммитах

Используем [Conventional Commits](https://conventionalcommits.org/):

- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг
- `test:` - добавление тестов
- `chore:` - обновление зависимостей, конфигурации

### Code Review

При создании PR убедитесь, что:

- [ ] Код соответствует стандартам проекта
- [ ] Добавлены тесты для новой функциональности
- [ ] Все тесты проходят
- [ ] Документация обновлена
- [ ] PR имеет понятное описание
- [ ] Нет конфликтов с main веткой

## Поддержка

### Каналы связи

- 📧 **Email**: dev@vitacore.dev
- 💬 **Discord**: [EIC Developers](https://discord.gg/eic-dev)
- 🐛 **Issues**: [GitHub Issues](https://github.com/vitacore-dev/Email-Intelligence-Collector/issues)
- 📖 **Wiki**: [Project Wiki](https://github.com/vitacore-dev/Email-Intelligence-Collector/wiki)

### Ресурсы

- [Roadmap проекта](https://github.com/vitacore-dev/Email-Intelligence-Collector/projects)
- [Архитектурные решения](docs/architecture/)
- [Примеры интеграции](examples/)
- [Changelog](CHANGELOG.md)

---

**Спасибо за ваш вклад в Email Intelligence Collector!** 🚀

