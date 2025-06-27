#!/bin/bash

# Email Intelligence Collector - Управление Docker контейнером
set -e

export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_info() {
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

show_help() {
    echo "Email Intelligence Collector - Управление Docker контейнером"
    echo ""
    echo "Использование: ./manage.sh [команда]"
    echo ""
    echo "Команды:"
    echo "  start     - Запустить контейнер"
    echo "  stop      - Остановить контейнер"
    echo "  restart   - Перезапустить контейнер"
    echo "  build     - Пересобрать образ"
    echo "  logs      - Показать логи"
    echo "  status    - Показать статус"
    echo "  health    - Проверить здоровье API"
    echo "  stats     - Показать статистику API"
    echo "  shell     - Войти в контейнер"
    echo "  init-db   - Инициализировать базу данных"
    echo "  clean     - Очистить все данные"
    echo "  help      - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  ./manage.sh start"
    echo "  ./manage.sh logs"
    echo "  ./manage.sh health"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker не найден. Убедитесь, что Docker Desktop установлен и запущен."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker не запущен. Запустите Docker Desktop."
        exit 1
    fi
}

start_container() {
    print_info "Запуск Email Intelligence Collector..."
    
    if docker compose -f docker-compose.simple.yml ps | grep -q "Up"; then
        print_warning "Контейнер уже запущен"
        return
    fi
    
    docker compose -f docker-compose.simple.yml up -d
    
    print_info "Ожидание запуска..."
    sleep 15
    
    if docker compose -f docker-compose.simple.yml ps | grep -q "Up"; then
        print_success "Контейнер успешно запущен!"
        show_urls
    else
        print_error "Не удалось запустить контейнер"
        docker compose -f docker-compose.simple.yml logs --tail=10
    fi
}

stop_container() {
    print_info "Остановка контейнера..."
    docker compose -f docker-compose.simple.yml down
    print_success "Контейнер остановлен"
}

restart_container() {
    print_info "Перезапуск контейнера..."
    stop_container
    start_container
}

build_image() {
    print_info "Пересборка образа..."
    docker compose -f docker-compose.simple.yml build --no-cache
    print_success "Образ пересобран"
}

show_logs() {
    print_info "Логи контейнера:"
    docker compose -f docker-compose.simple.yml logs --tail=50 -f
}

show_status() {
    print_info "Статус контейнера:"
    docker compose -f docker-compose.simple.yml ps
}

check_health() {
    print_info "Проверка здоровья сервисов..."
    
    # Check API
    if curl -s -f http://localhost:8001/health > /dev/null; then
        print_success "✅ API работает корректно!"
        curl -s http://localhost:8001/health | python3 -m json.tool 2>/dev/null || echo ""
    else
        print_error "❌ API не отвечает"
    fi
    
    # Check Frontend
    if curl -s -f http://localhost:3000/ > /dev/null; then
        print_success "✅ Frontend работает корректно!"
    else
        print_error "❌ Frontend не отвечает"
    fi
}

show_stats() {
    print_info "Статистика API:"
    
    if curl -s -f http://localhost:8001/api/stats > /dev/null; then
        curl -s http://localhost:8001/api/stats | python3 -m json.tool 2>/dev/null || echo "Статистика недоступна"
    else
        print_error "Не удалось получить статистику"
        return 1
    fi
}

enter_shell() {
    print_info "Вход в контейнер..."
    docker exec -it eic-app /bin/bash
}

init_database() {
    print_info "Инициализация базы данных..."
    
    docker exec eic-app python -c "
import sys
sys.path.append('/app/backend')
from database.connection import engine
from database.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
" && print_success "База данных инициализирована" || print_error "Ошибка инициализации базы данных"
}

clean_all() {
    print_warning "Это удалит все данные и контейнеры. Продолжить? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
        print_info "Очистка всех данных..."
        docker compose -f docker-compose.simple.yml down -v
        docker system prune -f
        print_success "Данные очищены"
    else
        print_info "Отменено"
    fi
}

show_urls() {
    echo ""
    echo "📱 Доступные сервисы:"
    echo "   🌐 Frontend: http://localhost:3000"
    echo "   🚀 API: http://localhost:8001"
    echo "   📚 Документация: http://localhost:8001/docs"
    echo "   ❤️  Проверка здоровья: http://localhost:8001/health"
    echo "   📊 Статистика: http://localhost:8001/api/stats"
    echo ""
}

# Основная логика
case "${1:-help}" in
    start)
        check_docker
        start_container
        ;;
    stop)
        check_docker
        stop_container
        ;;
    restart)
        check_docker
        restart_container
        ;;
    build)
        check_docker
        build_image
        ;;
    logs)
        check_docker
        show_logs
        ;;
    status)
        check_docker
        show_status
        ;;
    health)
        check_health
        ;;
    stats)
        show_stats
        ;;
    shell)
        check_docker
        enter_shell
        ;;
    init-db)
        check_docker
        init_database
        ;;
    clean)
        check_docker
        clean_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Неизвестная команда: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
