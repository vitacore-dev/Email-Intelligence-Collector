# Email Intelligence Collector (EIC)

![EIC Logo](docs/images/logo.png)

EIC - это мощная система для сбора и анализа информации из открытых источников интернета по заданному email-адресу с созданием детального профиля пользователя.

## 🚀 Возможности

- **Поиск по одному email**: Быстрый сбор информации по отдельному email-адресу
- **Массовая обработка**: Загрузка и обработка файлов с множественными email-адресами
- **Многоисточниковый сбор**: Интеграция с Google, LinkedIn, Twitter, GitHub, Facebook
- **Веб-скрапинг**: Автоматическое извлечение данных с веб-сайтов
- **Кэширование**: Сохранение результатов в базе данных для быстрого доступа
- **RESTful API**: Полнофункциональный API для интеграции
- **Современный UI**: Интуитивный веб-интерфейс на React.js
- **Масштабируемость**: Поддержка Docker и микросервисной архитектуры

## 🏗️ Архитектура системы

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  Data Collectors│    │   Database      │
│   (React.js)    │◄──►│   (FastAPI)     │◄──►│   (Scrapy, BS4) │◄──►│ (PostgreSQL +   │
│                 │    │                 │    │                 │    │  Elasticsearch) │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Технологический стек

### Backend
- **Python 3.11+** - Основной язык программирования
- **FastAPI** - Современный веб-фреймворк для API
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - Система миграций базы данных
- **Pydantic** - Валидация данных и сериализация
- **aiohttp** - Асинхронные HTTP запросы
- **BeautifulSoup4** - Парсинг HTML
- **Scrapy** - Веб-скрапинг

### Frontend
- **React.js 18+** - Библиотека для создания пользовательских интерфейсов
- **Vite** - Быстрый сборщик и dev-сервер
- **Tailwind CSS** - Utility-first CSS фреймворк
- **shadcn/ui** - Компоненты пользовательского интерфейса
- **Lucide Icons** - Набор иконок
- **Recharts** - Библиотека для графиков

### База данных
- **PostgreSQL** - Основная реляционная база данных
- **Elasticsearch** - Поисковая система для полнотекстового поиска
- **Redis** - Кэширование и очереди задач

### DevOps
- **Docker & Docker Compose** - Контейнеризация
- **GitHub Actions** - CI/CD
- **Nginx** - Веб-сервер и прокси

## 📁 Структура проекта

```
Email-Intelligence-Collector/
├── backend/                 # Backend API на FastAPI
│   ├── app/                # Основное приложение
│   │   ├── main.py         # Точка входа FastAPI
│   │   └── schemas.py      # Pydantic схемы
│   ├── modules/            # Модули для сбора данных
│   │   ├── data_collector.py      # Основной коллектор
│   │   ├── email_validator.py     # Валидация email
│   │   ├── file_processor.py      # Обработка файлов
│   │   ├── social_collectors.py   # Коллекторы соц. сетей
│   │   └── web_scraper.py         # Веб-скрапер
│   ├── database/           # Модели и миграции БД
│   │   ├── models.py       # SQLAlchemy модели
│   │   ├── connection.py   # Подключение к БД
│   │   └── migrations/     # Alembic миграции
│   ├── config/             # Конфигурационные файлы
│   │   └── settings.py     # Настройки приложения
│   ├── tests/              # Тесты
│   ├── requirements.txt    # Python зависимости
│   ├── Dockerfile         # Docker образ backend
│   └── .env.example       # Пример переменных окружения
├── frontend/               # Frontend на React.js
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── pages/          # Страницы приложения
│   │   ├── services/       # API сервисы
│   │   ├── utils/          # Утилиты
│   │   └── App.jsx         # Главный компонент
│   ├── public/             # Статические файлы
│   ├── package.json        # Node.js зависимости
│   └── Dockerfile         # Docker образ frontend
├── docs/                   # Документация
│   ├── api.md             # Документация API
│   ├── installation.md    # Руководство по установке
│   ├── usage.md           # Руководство пользователя
│   └── development.md     # Руководство разработчика
├── scripts/                # Скрипты для развертывания
├── docker-compose.yml      # Docker конфигурация
├── .gitignore             # Git ignore файл
└── README.md              # Этот файл
```

## 🚀 Быстрый старт

### Требования
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (опционально)

### Установка с Docker (рекомендуется)

1. **Клонирование репозитория**
```bash
git clone https://github.com/vitacore-dev/Email-Intelligence-Collector.git
cd Email-Intelligence-Collector
```

2. **Настройка переменных окружения**
```bash
cp backend/.env.example backend/.env
# Отредактируйте backend/.env файл с вашими настройками
```

3. **Запуск с Docker Compose**
```bash
docker-compose up -d
```

4. **Проверка работы**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API документация: http://localhost:8000/docs

### Ручная установка

#### Backend

1. **Создание виртуального окружения**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

2. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

3. **Настройка базы данных**
```bash
# Создайте базу данных PostgreSQL
createdb eic_db

# Запустите миграции
alembic upgrade head
```

4. **Запуск сервера**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

1. **Установка зависимостей**
```bash
cd frontend
npm install
```

2. **Настройка переменных окружения**
```bash
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

3. **Запуск dev-сервера**
```bash
npm run dev
```

## 📖 Использование

### Веб-интерфейс

1. Откройте http://localhost:3000 в браузере
2. Выберите тип поиска:
   - **Одиночный поиск**: Введите email-адрес
   - **Массовый поиск**: Загрузите CSV/TXT файл
3. Просмотрите результаты в удобном формате

### API

#### Поиск по одному email
```bash
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{"email": "example@domain.com", "force_refresh": false}'
```

#### Массовый поиск
```bash
curl -X POST "http://localhost:8000/api/bulk_search" \
     -F "file=@emails.csv"
```

#### Получение профиля
```bash
curl "http://localhost:8000/api/profile/example@domain.com"
```

Полная документация API доступна по адресу: http://localhost:8000/docs

## 🔧 Конфигурация

### Переменные окружения

Основные настройки в файле `backend/.env`:

```env
# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/eic_db

# API ключи
GOOGLE_API_KEY=your_google_api_key
GITHUB_API_KEY=your_github_token
TWITTER_API_KEY=your_twitter_api_key

# Лимиты
MAX_CONCURRENT_REQUESTS=10
RATE_LIMIT_PER_MINUTE=60
MAX_BULK_EMAILS=1000
```

### Настройка источников данных

Система поддерживает следующие источники:
- **Google Search** - Поиск по открытым данным
- **GitHub** - Поиск профилей разработчиков
- **LinkedIn** - Профессиональные профили (требует API ключ)
- **Twitter/X** - Социальные профили (требует API ключ)
- **Facebook** - Социальные профили (требует API ключ)

## 🧪 Тестирование

```bash
# Backend тесты
cd backend
pytest

# Frontend тесты
cd frontend
npm test
```

## 📊 Мониторинг

Система включает встроенные метрики:
- Количество обработанных email
- Статистика по источникам данных
- Производительность API
- Использование ресурсов

Доступ к статистике: http://localhost:8000/api/stats

## 🔒 Безопасность

- Валидация всех входных данных
- Rate limiting для API
- Логирование всех операций
- Защита от SQL инъекций
- CORS настройки
- Шифрование чувствительных данных

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🆘 Поддержка

- 📧 Email: support@vitacore.dev
- 🐛 Issues: [GitHub Issues](https://github.com/vitacore-dev/Email-Intelligence-Collector/issues)
- 📖 Документация: [docs/](docs/)

## 🙏 Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) - За отличный веб-фреймворк
- [React](https://reactjs.org/) - За мощную библиотеку UI
- [Tailwind CSS](https://tailwindcss.com/) - За удобный CSS фреймворк
- [shadcn/ui](https://ui.shadcn.com/) - За красивые компоненты

---

**Email Intelligence Collector** - Собирайте данные умно и эффективно! 🚀

