# Email Intelligence Collector - Frontend

## 🚀 Новые возможности: Цифровой двойник исследователя

Добавлена поддержка цифрового двойника исследователя с комплексной визуализацией данных и аналитикой.

### 📋 Основные компоненты

#### 1. API Service (`src/services/api.js`)
Централизованный сервис для работы с backend API:
- Методы для получения данных цифрового двойника
- Эндпоинты для визуализации и метрик
- Обработка ошибок и типизация запросов

#### 2. DigitalTwin (`src/components/DigitalTwin.jsx`)
Главный компонент цифрового двойника:
- **Обзор**: Профиль исследователя и ключевые метрики
- **Сеть**: Визуализация коллабораций и связей
- **Временная линия**: Динамика публикаций и активности
- **Метрики**: Детальные показатели исследований

#### 3. Компоненты визуализации (`src/components/visualizations/`)

##### ResearchRadarChart
- Радарная диаграмма исследовательского профиля
- Многомерная оценка активности исследователя
- Интерактивная визуализация с легендой

##### CollaborationNetwork
- Сеть научного сотрудничества
- Интерактивный граф связей между исследователями
- Физическая симуляция для расположения узлов

##### ResearchTimeline
- Временная линия публикаций и цитирований
- Динамика исследовательской активности
- Ключевые события в карьере

##### MetricsDisplay
- Ключевые показатели эффективности (KPI)
- Распределение по областям исследований
- Тренды роста и развития

#### 4. SearchWithSuggestions (`src/components/SearchWithSuggestions.jsx`)
Компонент поиска с автодополнением:
- Предложения на основе API
- История недавних поисков
- Интуитивный интерфейс

### 🔧 API Endpoints

Компоненты интегрированы с следующими эндпоинтами:

```javascript
// Основные данные цифрового двойника
GET /api/digital-twin/{email}
GET /api/visualization/{email}
GET /api/academic-profile/{email}

// Анализ сетей и связей
GET /api/network-analysis/{email}
GET /api/collaboration-graph/{email}

// Метрики и показатели
GET /api/research-metrics/{email}
GET /api/citation-analysis/{email}

// Временные данные
GET /api/research-timeline/{email}
GET /api/activity-timeline/{email}

// Тренды и прогнозы
GET /api/trending-topics/{email}
GET /api/research-predictions/{email}

// Экспорт данных
GET /api/export-profile/{email}?format={json|pdf}

// Вспомогательные эндпоинты
GET /api/search-suggestions?q={query}
POST /api/batch-analysis
GET /api/realtime-metrics/{email}
```

### 🎨 Стили и UI

Использует современную библиотеку компонентов:
- **Tailwind CSS** для стилизации
- **Radix UI** для базовых компонентов
- **Recharts** для графиков и диаграмм
- **Lucide React** для иконок

### 📱 Функциональность

#### Цифровой двойник включает:

1. **Профиль исследователя**
   - Основная информация (имя, организация, область исследований)
   - Ключевые метрики (публикации, цитирования, H-индекс)
   - Исследовательский профиль (радарная диаграмма)

2. **Сеть сотрудничества**
   - Интерактивный граф коллабораций
   - Ключевые соавторы и партнеры
   - Метрики центральности в сети

3. **Временная аналитика**
   - Динамика публикаций по годам
   - Рост цитирований во времени
   - Ключевые события в карьере

4. **Исследовательские метрики**
   - Индексы цитирования (H-индекс, i10-индекс)
   - Распределение по областям исследований
   - Тренды роста и прогнозы

### 🚀 Запуск и разработка

```bash
# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev

# Сборка для продакшена
npm run build

# Предварительный просмотр продакшен сборки
npm run preview
```

### 🔗 Интеграция с Backend

Убедитесь, что backend поддерживает новые эндпоинты:

1. Запустите backend сервер на порту 8001
2. Убедитесь, что CORS настроен для frontend домена
3. Проверьте доступность API эндпоинтов через `/api/`

### 📊 Структура данных

#### Пример ответа цифрового двойника:

```json
{
  "name": "Dr. Jane Smith",
  "email": "jane.smith@university.edu",
  "affiliation": "MIT Computer Science",
  "research_interests": ["Machine Learning", "AI Ethics", "Data Science"],
  "metrics": {
    "total_publications": 45,
    "total_citations": 892,
    "h_index": 14,
    "collaboration_score": 78
  },
  "network": {
    "nodes": [...],
    "links": [...]
  },
  "timeline": {
    "publications_by_year": [...],
    "events": [...]
  }
}
```

### 🎯 Расширения и кастомизация

Компоненты спроектированы для легкого расширения:

1. **Добавление новых метрик**: Расширьте `MetricsDisplay`
2. **Новые типы визуализации**: Создайте компоненты в `visualizations/`
3. **Дополнительные API**: Расширьте `api.js` сервис

### 🐛 Отладка

Для отладки проблем:

1. Проверьте консоль браузера на ошибки API
2. Убедитесь, что backend API доступен
3. Проверьте формат данных в Network tab DevTools

### 📝 Заметки

- Компоненты поддерживают fallback данные для демонстрации
- Все API запросы обрабатывают ошибки gracefully
- UI адаптивен и работает на мобильных устройствах
- Поддерживается темная тема через переключатель
