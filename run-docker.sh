#!/bin/bash

echo "🐳 Email Intelligence Collector - Docker Setup"
echo "==============================================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Переходим в директорию проекта
cd "$(dirname "$0")"

echo "📁 Текущая директория: $(pwd)"

# Проверяем наличие необходимых файлов
if [ ! -f "docker-compose.simple.yml" ]; then
    echo "❌ Файл docker-compose.simple.yml не найден"
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile не найден"
    exit 1
fi

if [ ! -f "frontend/Dockerfile" ]; then
    echo "❌ frontend/Dockerfile не найден"
    exit 1
fi

echo "✅ Все необходимые файлы найдены"

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker compose -f docker-compose.simple.yml down 2>/dev/null || true

# Удаляем старые образы (опционально)
read -p "🗑️  Удалить старые образы для пересборки? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Удаляем старые образы..."
    docker compose -f docker-compose.simple.yml down --rmi all --volumes --remove-orphans 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
fi

# Собираем и запускаем контейнеры
echo "🔨 Собираем образы..."
docker compose -f docker-compose.simple.yml build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при сборке образов"
    exit 1
fi

echo "🚀 Запускаем контейнеры..."
docker compose -f docker-compose.simple.yml up -d

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при запуске контейнеров"
    exit 1
fi

echo "⏳ Ждем запуска сервисов..."
sleep 15

# Проверяем статус контейнеров
echo "📊 Статус контейнеров:"
docker compose -f docker-compose.simple.yml ps

# Проверяем здоровье сервисов
echo ""
echo "🔍 Проверяем здоровье сервисов..."

# Проверяем backend
echo -n "Backend API (http://localhost:8000): "
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Работает"
else
    echo "❌ Недоступен"
    echo "📋 Логи backend:"
    docker compose -f docker-compose.simple.yml logs --tail=20 email-intelligence-collector
fi

# Проверяем frontend
echo -n "Frontend (http://localhost:5173): "
if curl -s -f http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Работает"
else
    echo "❌ Недоступен"
    echo "📋 Логи frontend:"
    docker compose -f docker-compose.simple.yml logs --tail=20 frontend
fi

echo ""
echo "🎉 Email Intelligence Collector запущен в Docker!"
echo ""
echo "📱 Доступ к приложению:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API документация: http://localhost:8000/docs"
echo ""
echo "🔧 Полезные команды:"
echo "   Просмотр логов: docker compose -f docker-compose.simple.yml logs -f"
echo "   Остановка: docker compose -f docker-compose.simple.yml down"
echo "   Перезапуск: docker compose -f docker-compose.simple.yml restart"
echo ""
echo "📊 Тестирование PDF анализа:"
echo "   1. Откройте http://localhost:5173"
echo "   2. Перейдите на вкладку 'PDF Анализ'"
echo "   3. Введите email: buch1202@mail.ru"
echo "   4. Нажмите 'Анализировать PDF'"
