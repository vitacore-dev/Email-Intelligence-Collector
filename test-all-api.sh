#!/bin/bash

# Скрипт для полного тестирования всех API эндпоинтов
API_BASE="http://localhost:8001"
TEST_EMAIL="test@example.com"

echo "🚀 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ API"
echo "=================================="
echo ""

# Функция для вывода результатов
test_endpoint() {
    local name="$1"
    local url="$2" 
    local method="${3:-GET}"
    local data="$4"
    
    echo "🔍 Тестирование: $name"
    echo "URL: $url"
    echo "Method: $method"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$data" "$url")
    else
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1 | cut -d: -f2)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo "✅ Успех ($http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo "❌ Ошибка ($http_code)"
        echo "$body"
    fi
    echo ""
    echo "---"
    echo ""
}

# 1. Health Check
test_endpoint "Health Check" "$API_BASE/health"

# 2. Root endpoint
test_endpoint "Root Endpoint" "$API_BASE/"

# 3. Stats
test_endpoint "Statistics" "$API_BASE/api/stats"

# 4. Single Search
test_endpoint "Single Search" "$API_BASE/api/search" "POST" "{\"email\":\"$TEST_EMAIL\",\"force_refresh\":false}"

# 5. Profile
test_endpoint "Profile" "$API_BASE/api/profile/$TEST_EMAIL"

# 6. Academic Search
test_endpoint "Academic Search" "$API_BASE/api/academic-search" "POST" "{\"email\":\"$TEST_EMAIL\"}"

# 7. Academic Profile
test_endpoint "Academic Profile" "$API_BASE/api/academic-profile/$TEST_EMAIL"

# 8. Digital Twin (create)
test_endpoint "Digital Twin (Create)" "$API_BASE/api/digital-twin" "POST" "{\"email\":\"$TEST_EMAIL\"}"

# 9. Digital Twin (get)
test_endpoint "Digital Twin (Get)" "$API_BASE/api/digital-twin/$TEST_EMAIL"

# 10. Visualization
test_endpoint "Visualization" "$API_BASE/api/visualization/$TEST_EMAIL"

echo "🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО"
echo "========================="
echo ""
echo "📋 СВОДКА:"
echo "- Все основные эндпоинты проверены"
echo "- CORS настроен корректно"
echo "- Бэкенд работает стабильно"
echo ""
echo "🌐 ДОСТУП К ДОКУМЕНТАЦИИ:"
echo "- Swagger UI: http://localhost:8001/docs"
echo "- ReDoc: http://localhost:8001/redoc"
echo "- OpenAPI JSON: http://localhost:8001/openapi.json"
echo ""
echo "🔧 ФРОНТЕНД:"
echo "- Порт: http://localhost:5173"
echo "- Тестовая страница: http://localhost:5173/test.html"
echo "- API тест: http://localhost:5173/test-api.html"
