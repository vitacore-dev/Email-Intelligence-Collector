# Улучшенный веб-скрапер (EnhancedWebScraper)

## Обзор

Улучшенный веб-скрапер представляет собой значительное обновление оригинального модуля `web_scraper.py` с добавлением следующих возможностей:

### Новые функции

1. **Адаптивные селекторы** - автоматическая настройка CSS-селекторов в зависимости от платформы
2. **NLP анализ** - извлечение именованных сущностей, анализ тональности, продвинутое извлечение ключевых слов
3. **Интеллектуальное кеширование** - хранение результатов с TTL для повышения производительности
4. **Адаптивное ограничение скорости** - умное управление задержками между запросами
5. **Расширенная обработка ошибок** - детальное отслеживание и анализ ошибок
6. **Параллельная обработка** - асинхронное выполнение множественных запросов
7. **Подробная статистика** - метрики производительности и отчеты

## Установка

### Основные зависимости

```bash
# Установка дополнительных зависимостей
pip install -r requirements_webscraper.txt

# Загрузка модели spaCy для английского языка
python -m spacy download en_core_web_sm

# Загрузка данных NLTK (выполнится автоматически при первом запуске)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
```

### Проверка установки

```python
from backend.modules.web_scraper import EnhancedWebScraper
print("Установка прошла успешно!")
```

## Быстрый старт

### Базовое использование

```python
import asyncio
from backend.modules.web_scraper import EnhancedWebScraper

async def basic_scraping():
    email = "test@example.com"
    urls = ["https://example.com/profile"]
    
    async with EnhancedWebScraper(email) as scraper:
        results = await scraper.scrape_websites_enhanced(urls)
        
        print("Персональная информация:", results['person_info'])
        print("Контакты:", results['contact_info'])
        print("Социальные ссылки:", results['social_links'])

# Запуск
asyncio.run(basic_scraping())
```

### Продвинутая конфигурация

```python
from backend.modules.web_scraper import EnhancedWebScraper, ScrapingConfig, SelectorConfig

# Настройка параметров
config = ScrapingConfig(
    max_pages=20,
    concurrent_requests=5,
    timeout=60,
    retry_attempts=3,
    cache_ttl=3600,  # 1 час
    delay_between_requests=2.0
)

# Настройка селекторов
selector_config = SelectorConfig()
selector_config.platform_selectors['mysite.com'] = {
    'name': ['.profile-name', '.user-title'],
    'job': ['.job-description'],
    'company': ['.company-info']
}

async def advanced_scraping():
    async with EnhancedWebScraper(email, config, selector_config) as scraper:
        results = await scraper.scrape_websites_enhanced(urls)
        # Обработка результатов...
```

## Конфигурация

### ScrapingConfig

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `max_pages` | int | 10 | Максимальное количество страниц для обработки |
| `concurrent_requests` | int | 5 | Количество параллельных запросов |
| `timeout` | int | 30 | Таймаут запроса в секундах |
| `retry_attempts` | int | 3 | Количество попыток при ошибке |
| `retry_delay` | float | 1.0 | Задержка между попытками |
| `cache_ttl` | int | 3600 | Время жизни кеша в секундах |
| `delay_between_requests` | float | 1.0 | Базовая задержка между запросами |

### SelectorConfig

Позволяет настраивать CSS-селекторы для различных типов информации:

- `name_selectors` - селекторы для имен
- `job_selectors` - селекторы для должностей
- `company_selectors` - селекторы для компаний
- `location_selectors` - селекторы для местоположений
- `platform_selectors` - специфичные селекторы для платформ

## Результаты

### Структура ответа

```python
{
    'person_info': {
        'name': 'John Doe',
        'occupation': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'San Francisco, CA'
    },
    'contact_info': {
        'emails': ['john@example.com'],
        'phones': ['+1-555-123-4567'],
        'addresses': ['123 Main St, SF, CA']
    },
    'social_links': [
        {
            'platform': 'LinkedIn',
            'url': 'https://linkedin.com/in/johndoe',
            'text': 'LinkedIn Profile',
            'context': 'Professional network'
        }
    ],
    'content_analysis': {
        'https://example.com': {
            'title': 'John Doe - Profile',
            'keywords': [
                {
                    'word': 'software',
                    'frequency': 5,
                    'pos_tags': ['NN']
                }
            ],
            'meta_info': {...}
        }
    },
    'nlp_analysis': {
        'https://example.com': {
            'sentiment': {
                'polarity': 0.1,
                'subjectivity': 0.4
            },
            'entities_spacy': {
                'PERSON': ['John Doe'],
                'ORG': ['Tech Corp']
            },
            'entities_nltk': {...},
            'language_detected': 'en'
        }
    },
    'performance_stats': {
        'total_urls': 1,
        'successful_scrapes': 1,
        'failed_scrapes': 0,
        'duration': 2.34
    },
    'errors': {
        'total_errors': 0,
        'error_types': {},
        'affected_urls': 0
    }
}
```

## NLP Возможности

### Извлечение именованных сущностей

Скрапер использует как spaCy, так и NLTK для извлечения именованных сущностей:

- **PERSON** - имена людей
- **ORG/ORGANIZATION** - названия организаций
- **GPE/LOCATION** - географические локации
- **MONEY** - денежные суммы
- **DATE** - даты

### Анализ тональности

Определяет эмоциональную окраску текста:
- **polarity** (-1 до 1): негативность/позитивность
- **subjectivity** (0 до 1): объективность/субъективность

### Продвинутое извлечение ключевых слов

Использует POS-теги для фильтрации значимых слов и предоставляет:
- Частоту употребления
- Грамматические теги (части речи)
- Ранжирование по важности

## Обработка ошибок

Скрапер отслеживает различные типы ошибок:

- **client_error** - ошибки HTTP клиента
- **http_error** - HTTP статусы ошибок
- **content_type_error** - неподходящий тип контента
- **unexpected_error** - неожиданные ошибки
- **general_error** - общие ошибки

Каждая ошибка логируется с контекстом и количеством попыток.

## Производительность

### Кеширование

- Автоматическое кеширование результатов
- Настраиваемое время жизни (TTL)
- Проверка валидности кеша

### Адаптивное ограничение скорости

- Автоматическая корректировка задержек
- Индивидуальные настройки для каждого домена
- Уменьшение задержки при успешных запросах
- Увеличение при ошибках

### Параллельная обработка

- Асинхронные запросы
- Семафор для ограничения конкурентности
- Gathering результатов с обработкой исключений

## Примеры использования

Полные примеры использования доступны в файле `web_scraper_example.py`:

1. **Базовое использование** - простой скрапинг
2. **Продвинутая конфигурация** - настройка параметров
3. **NLP анализ** - работа с лингвистическими данными
4. **Обработка ошибок** - управление ошибками
5. **Анализ производительности** - метрики и статистика
6. **Экспорт результатов** - сохранение данных

## Обратная совместимость

Новый скрапер полностью совместим со старым API:

```python
# Старый способ (продолжает работать)
scraper = WebScraper(email)
results = await scraper.scrape_websites(urls)

# Новый способ
async with EnhancedWebScraper(email) as scraper:
    results = await scraper.scrape_websites_enhanced(urls)
```

## Мониторинг и отладка

### Статистика скрапера

```python
stats = scraper.get_scraping_stats()
print(f"Размер кеша: {stats['cache_size']}")
print(f"Ошибки: {stats['error_summary']}")
print(f"Задержки по доменам: {stats['rate_limiter_stats']['current_delays']}")
```

### Логирование

Все ошибки и важные события логируются с использованием стандартного модуля `logging`:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('backend.modules.web_scraper')
```

## Ограничения и рекомендации

1. **Ресурсы**: NLP анализ требует больше CPU и памяти
2. **Модели**: Убедитесь, что модель spaCy установлена
3. **Сетевые ограничения**: Соблюдайте robots.txt и условия использования сайтов
4. **Производительность**: Настройте `concurrent_requests` в зависимости от ресурсов

## Устранение неполадок

### Ошибка импорта spaCy

```bash
python -m spacy download en_core_web_sm
```

### Ошибки NLTK

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### Проблемы с производительностью

1. Уменьшите `concurrent_requests`
2. Увеличьте `delay_between_requests`
3. Уменьшите `cache_ttl` для экономии памяти

### Ошибки сети

1. Проверьте подключение к интернету
2. Убедитесь, что целевые сайты доступны
3. Рассмотрите использование прокси для заблокированных ресурсов
