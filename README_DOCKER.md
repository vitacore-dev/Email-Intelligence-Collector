# 🐳 Email Intelligence Collector - Docker Deployment Guide

## 🎯 Обзор

Этот проект полностью Docker-изирован с поддержкой production и development окружений. Docker конфигурация включает:

- **Multi-stage Dockerfile** для оптимизации размера образов
- **Health checks** для всех сервисов
- **Логирование** с ротацией
- **Volumes** для персистентности данных
- **Networks** для изоляции сервисов
- **Environment variables** для конфигурации

## 📋 Требования

- Docker Desktop 20.10+
- Docker Compose 1.29+
- 4GB RAM (минимум)
- 10GB свободного места

## 🚀 Быстрый старт

### 1. Установка Docker (если не установлен)

**macOS:**
```bash
# Homebrew
brew install --cask docker

# Или скачайте с https://docker.com/products/docker-desktop
```

**Проверка установки:**
```bash
docker --version
docker-compose --version
```

### 2. Клонирование и настройка

```bash
# Клонирование
git clone https://github.com/vitacore-dev/Email-Intelligence-Collector.git
cd Email-Intelligence-Collector

# Настройка переменных окружения
cp .env .env.local
# Отредактируйте .env.local при необходимости
```

### 3. Запуск проекта

```bash
# Простой запуск (только backend)
docker-compose -f docker-compose.simple.yml up

# Полный production запуск
make build && make up

# Development режим
make dev-build && make dev-up
```

## 🏗️ Архитектура Docker

### Сервисы

| Сервис | Порт | Описание | Health Check |
|--------|------|----------|-------------|
| **frontend** | 3000 | React + Nginx | ✅ |
| **backend** | 8000 | FastAPI | ✅ |
| **db** | 5432 | PostgreSQL 15 | ✅ |
| **redis** | 6379 | Redis cache | ✅ |
| **elasticsearch** | 9200 | Search engine | ✅ |
| **nginx** | 80/443 | Reverse proxy | ✅ |

### Docker образы

```
┌─────────────────────────────────────────┐
│                Frontend                 │
│  Multi-stage: Node.js → Nginx          │
│  Size: ~50MB (optimized)               │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│                Backend                  │
│  Multi-stage: Python builder → Runtime │
│  Size: ~200MB (optimized)              │
│  User: non-root (security)             │
└─────────────────────────────────────────┘
```

## 📁 Docker файлы

### Структура
```
Email-Intelligence-Collector/
├── docker-compose.yml          # Production конфигурация
├── docker-compose.dev.yml      # Development конфигурация  
├── docker-compose.simple.yml   # Упрощенная конфигурация
├── Makefile                    # Команды управления
├── .env                        # Environment variables
├── backend/
│   ├── Dockerfile             # Multi-stage backend образ
│   ├── .dockerignore          # Исключения для сборки
│   └── requirements.txt       # Python зависимости
├── frontend/
│   ├── Dockerfile             # Multi-stage frontend образ
│   ├── .dockerignore          # Исключения для сборки
│   └── nginx.conf             # Nginx конфигурация
└── nginx/                     # Reverse proxy (optional)
```

## 🔧 Конфигурации

### Production (docker-compose.yml)
- **PostgreSQL** + **Elasticsearch** + **Redis**
- **Health checks** и **dependencies**
- **Volumes** для данных
- **Logging** с ротацией
- **Security**: non-root user, ограниченные ресурсы

### Development (docker-compose.dev.yml)
- **SQLite** вместо PostgreSQL (опционально)
- **Hot reload** для backend и frontend
- **Volume mounts** для live development
- **Debug режим**

### Simple (docker-compose.simple.yml)
- **Только backend** с SQLite
- **Минимальные зависимости**
- **Быстрый старт**

## 🛠️ Команды управления

### Makefile команды
```bash
# Просмотр всех команд
make help

# Production
make build          # Сборка образов
make up             # Запуск сервисов
make down           # Остановка
make restart        # Перезапуск

# Development
make dev-build      # Сборка dev образов
make dev-up         # Запуск dev сервисов
make dev-down       # Остановка dev

# Утилиты
make logs           # Все логи
make logs-backend   # Логи backend
make logs-frontend  # Логи frontend
make shell-backend  # Shell backend контейнера
make shell-db       # PostgreSQL shell
make clean          # Полная очистка
make health         # Проверка health checks
make status         # Статус контейнеров
```

### Docker Compose команды
```bash
# Запуск конкретных сервисов
docker-compose up backend redis

# Просмотр логов
docker-compose logs -f backend

# Выполнение команд в контейнере
docker-compose exec backend bash
docker-compose exec db psql -U postgres -d eic_db

# Масштабирование (если поддерживается)
docker-compose up --scale backend=2
```

## 🗂️ Управление данными

### Volumes
```bash
# Просмотр volumes
docker volume ls

# Backup данных
docker run --rm -v eic_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/db_backup.tar.gz /data

# Restore данных
docker run --rm -v eic_postgres_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/db_backup.tar.gz -C /
```

### Переменные окружения
```bash
# .env файл
DEBUG=False
SECRET_KEY=your-production-secret-key
POSTGRES_PASSWORD=secure-password

# Docker Compose автоматически подхватывает .env
```

## 🔍 Мониторинг и отладка

### Health Checks
```bash
# Проверка статуса всех сервисов
docker-compose ps

# Детальная информация о health checks
docker inspect $(docker-compose ps -q backend) | jq '.[0].State.Health'
```

### Логирование
```bash
# Настройка логирования (уже включена)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

# Просмотр логов
docker-compose logs -f --tail=100 backend
```

### Отладка проблем
```bash
# 1. Проверка ресурсов
docker stats

# 2. Проверка сети
docker network ls
docker network inspect eic-network

# 3. Проверка образов
docker images | grep eic

# 4. Очистка при проблемах
docker-compose down -v
docker system prune -f
```

## 🚀 Production Deployment

### 1. Подготовка сервера
```bash
# Требования
- Ubuntu 20.04+ / CentOS 8+ / Amazon Linux 2
- Docker 20.10+
- Docker Compose 1.29+
- 4GB+ RAM, 20GB+ storage
```

### 2. Настройка production переменных
```bash
# .env
DEBUG=False
SECRET_KEY=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 16)

# SSL сертификаты (если используется nginx)
# Добавьте сертификаты в nginx/ssl/
```

### 3. Запуск в production
```bash
# Сборка и запуск
make build
make up

# Применение миграций
make db-migrate

# Проверка здоровья
make health
```

### 4. Мониторинг production
```bash
# Автоматический перезапуск
restart: unless-stopped

# Логи в production
docker-compose logs --since=1h backend

# Мониторинг ресурсов
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## ⚡ Оптимизация производительности

### Образы
- **Multi-stage builds** для минимального размера
- **Layer caching** для быстрой пересборки
- **Non-root user** для безопасности
- **.dockerignore** для исключения ненужных файлов

### Runtime
- **Health checks** для автоматического восстановления
- **Resource limits** для предотвращения утечек
- **Logging rotation** для управления дисковым пространством
- **Dependencies** для правильного порядка запуска

## 🔒 Безопасность

### Container Security
```dockerfile
# Non-root user
USER appuser

# Read-only filesystem (где возможно)
read_only: true

# No privileged mode
privileged: false

# Limited capabilities
cap_drop:
  - ALL
```

### Network Security
```yaml
# Изолированная сеть
networks:
  eic-network:
    driver: bridge
    internal: true  # Для internal services
```

### Secrets Management
```bash
# Используйте Docker secrets или external secret management
# Никогда не храните секреты в образах
# Используйте .env файлы с правильными правами (600)
chmod 600 .env
```

## 🎯 Заключение

Docker конфигурация Email Intelligence Collector оптимизирована для:

✅ **Production готовность** - multi-stage builds, health checks, logging  
✅ **Development удобство** - hot reload, volume mounts, debug режим  
✅ **Масштабируемость** - независимые сервисы, балансировка нагрузки  
✅ **Безопасность** - non-root users, изолированные сети, secrets management  
✅ **Мониторинг** - health checks, structured logging, metrics  

Все готово для deploy в любое окружение! 🚀
