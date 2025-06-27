#!/bin/bash

# Email Intelligence Collector - Docker Launcher
set -e

echo "🚀 Email Intelligence Collector - Docker Setup"
echo "=============================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Путь к Docker Desktop
DOCKER_PATH="/Applications/Docker.app/Contents/Resources/bin/docker"

# Проверяем наличие Docker Desktop
if [ ! -f "$DOCKER_PATH" ]; then
    print_error "Docker Desktop не найден. Убедитесь, что Docker Desktop установлен."
    exit 1
fi

# Проверяем, что Docker запущен
if ! $DOCKER_PATH info &> /dev/null; then
    print_error "Docker не запущен. Запустите Docker Desktop и попробуйте снова."
    exit 1
fi

print_status "Docker и Docker Compose найдены"

# Останавливаем существующие контейнеры если они запущены
print_status "Остановка существующих контейнеров..."
$DOCKER_PATH compose -f docker-compose.simple.yml down --remove-orphans 2>/dev/null || true

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    print_status "Создание .env файла..."
    cp .env.docker .env
    print_warning "Создан файл .env. Вы можете отредактировать его для настройки API ключей."
fi

# Проверяем наличие образа и собираем если нужно
print_status "Сборка Docker образа..."
$DOCKER_PATH compose -f docker-compose.simple.yml build

# Запускаем контейнер
print_status "Запуск контейнера Email Intelligence Collector..."
$DOCKER_PATH compose -f docker-compose.simple.yml up -d

# Ждем пока сервис запустится
print_status "Ожидание запуска сервиса..."
sleep 10

# Проверяем статус
if $DOCKER_PATH compose -f docker-compose.simple.yml ps | grep -q "Up"; then
    print_success "✅ Email Intelligence Collector успешно запущен!"
    echo ""
    echo "📱 Доступные сервисы:"
    echo "   🌐 API: http://localhost:8001"
    echo "   📚 Документация: http://localhost:8001/docs"
    echo "   ❤️  Проверка здоровья: http://localhost:8001/health"
    echo ""
    echo "🔍 Проверяем API..."
    
    # Проверяем API
    if curl -s -f http://localhost:8001/health > /dev/null; then
        print_success "API отвечает корректно!"
        
        # Выводим статистику
        echo ""
        echo "📊 Статистика системы:"
        curl -s http://localhost:8001/api/stats | python3 -m json.tool 2>/dev/null || echo "Статистика недоступна"
        
    else
        print_warning "API пока не отвечает. Возможно сервис еще запускается."
        print_status "Попробуйте проверить через несколько секунд: curl http://localhost:8001/health"
    fi
    
    echo ""
    echo "📝 Полезные команды:"
    echo "   Просмотр логов: $DOCKER_PATH compose -f docker-compose.simple.yml logs -f"
    echo "   Остановка: $DOCKER_PATH compose -f docker-compose.simple.yml down"
    echo "   Перезапуск: $DOCKER_PATH compose -f docker-compose.simple.yml restart"
    echo "   Статус: $DOCKER_PATH compose -f docker-compose.simple.yml ps"
    
else
    print_error "❌ Не удалось запустить контейнер"
    print_status "Проверяем логи..."
    $DOCKER_PATH compose -f docker-compose.simple.yml logs --tail=20
    exit 1
fi

echo ""
print_success "🎉 Запуск завершен! Приложение готово к использованию."
