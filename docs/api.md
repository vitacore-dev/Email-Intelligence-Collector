# API Документация

Email Intelligence Collector предоставляет RESTful API для интеграции с внешними системами.

## Базовый URL

```
http://localhost:8000
```

## Аутентификация

В текущей версии API не требует аутентификации. В продакшн версии будет добавлена аутентификация через JWT токены.

## Endpoints

### 1. Проверка состояния

#### GET /health
Проверка работоспособности API.

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. Поиск по одному email

#### POST /api/search
Поиск информации по одному email-адресу.

**Параметры запроса:**
```json
{
  "email": "example@domain.com",
  "force_refresh": false
}
```

**Параметры:**
- `email` (string, обязательный) - Email-адрес для поиска
- `force_refresh` (boolean, опциональный) - Принудительное обновление, игнорируя кэш

**Ответ:**
```json
{
  "status": "success",
  "source": "cache",
  "data": {
    "email": "example@domain.com",
    "person_info": {
      "name": "John Doe",
      "location": "New York, USA",
      "occupation": "Software Engineer",
      "company": "Tech Corp",
      "bio": "Passionate developer"
    },
    "social_profiles": [
      {
        "platform": "LinkedIn",
        "url": "https://linkedin.com/in/johndoe",
        "username": "johndoe",
        "verified": true
      }
    ],
    "websites": [
      "https://johndoe.dev"
    ],
    "phone_numbers": [
      "+1-555-123-4567"
    ],
    "addresses": [
      "123 Main St, New York, NY"
    ],
    "sources": [
      "Google Search",
      "LinkedIn",
      "GitHub"
    ],
    "confidence_score": 0.85,
    "last_updated": "2024-01-01T12:00:00Z"
  }
}
```

### 3. Массовый поиск

#### POST /api/bulk_search
Массовый поиск по файлу с email-адресами.

**Параметры запроса:**
- `file` (file) - CSV или TXT файл с email-адресами

**Ответ:**
```json
{
  "total": 100,
  "processed": 95,
  "existing": 30,
  "new": 65,
  "invalid": 5,
  "results": [
    {
      "email": "user1@example.com",
      "status": "new",
      "data": { /* профиль данных */ }
    },
    {
      "email": "user2@example.com", 
      "status": "from_cache",
      "data": { /* профиль данных */ }
    },
    {
      "email": "invalid-email",
      "status": "invalid",
      "error": "Invalid email format",
      "data": null
    }
  ]
}
```

### 4. Получение профиля

#### GET /api/profile/{email}
Получение сохраненного профиля по email.

**Параметры:**
- `email` (string) - Email-адрес

**Ответ:**
```json
{
  "status": "success",
  "data": {
    /* данные профиля */
  }
}
```

### 5. Удаление профиля

#### DELETE /api/profile/{email}
Удаление профиля из базы данных.

**Параметры:**
- `email` (string) - Email-адрес

**Ответ:**
```json
{
  "status": "success",
  "message": "Профиль удален"
}
```

### 6. Статистика системы

#### GET /api/stats
Получение статистики работы системы.

**Ответ:**
```json
{
  "total_profiles": 1500,
  "total_searches": 2300,
  "recent_searches": [
    {
      "email": "recent@example.com",
      "search_type": "single",
      "results_found": 5,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

## Коды ошибок

### HTTP Status Codes

- `200` - Успешный запрос
- `400` - Неверные параметры запроса
- `404` - Ресурс не найден
- `422` - Ошибка валидации данных
- `429` - Превышен лимит запросов
- `500` - Внутренняя ошибка сервера

### Формат ошибок

```json
{
  "detail": "Описание ошибки"
}
```

## Rate Limiting

API имеет ограничения на количество запросов:
- 60 запросов в минуту для одиночного поиска
- 10 запросов в минуту для массового поиска
- 100 запросов в минуту для получения профилей

## Примеры использования

### Python

```python
import requests

# Поиск по email
response = requests.post(
    'http://localhost:8000/api/search',
    json={'email': 'example@domain.com'}
)
data = response.json()
print(data)

# Массовый поиск
with open('emails.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/bulk_search',
        files={'file': f}
    )
    data = response.json()
    print(f"Обработано: {data['processed']}/{data['total']}")
```

### JavaScript

```javascript
// Поиск по email
const searchEmail = async (email) => {
  const response = await fetch('http://localhost:8000/api/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, force_refresh: false })
  });
  
  const data = await response.json();
  return data;
};

// Массовый поиск
const bulkSearch = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/bulk_search', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data;
};
```

### cURL

```bash
# Поиск по email
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{"email": "example@domain.com"}'

# Массовый поиск
curl -X POST "http://localhost:8000/api/bulk_search" \
     -F "file=@emails.csv"

# Получение профиля
curl "http://localhost:8000/api/profile/example@domain.com"

# Статистика
curl "http://localhost:8000/api/stats"
```

## Swagger UI

Интерактивная документация API доступна по адресу:
```
http://localhost:8000/docs
```

## Схемы данных

### EmailRequest
```json
{
  "email": "string",
  "force_refresh": "boolean"
}
```

### PersonInfo
```json
{
  "name": "string",
  "location": "string", 
  "occupation": "string",
  "company": "string",
  "bio": "string",
  "avatar_url": "string"
}
```

### SocialProfile
```json
{
  "platform": "string",
  "url": "string",
  "username": "string",
  "followers": "integer",
  "verified": "boolean"
}
```

### EmailProfileData
```json
{
  "email": "string",
  "person_info": "PersonInfo",
  "social_profiles": ["SocialProfile"],
  "websites": ["string"],
  "phone_numbers": ["string"],
  "addresses": ["string"],
  "sources": ["string"],
  "confidence_score": "float",
  "last_updated": "datetime"
}
```

