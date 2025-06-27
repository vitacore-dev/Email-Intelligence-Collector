# 🐳 Email Intelligence Collector - Docker Setup

Простой и быстрый запуск Email Intelligence Collector в Docker контейнере.

## 🚀 Быстрый старт

### 1. Запуск проекта

```bash
# Запуск контейнера
./manage.sh start

# Проверка здоровья API
./manage.sh health

# Просмотр статистики
./manage.sh stats
```

### 2. Доступ к сервисам

После запуска доступны следующие URL:

- **🌐 API**: http://localhost:8001
- **📚 Документация**: http://localhost:8001/docs
- **❤️ Здоровье**: http://localhost:8001/health
- **📊 Статистика**: http://localhost:8001/api/stats

## 📋 Управление контейнером

### Основные команды

```bash
# Показать все доступные команды
./manage.sh help

# Запустить контейнер
./manage.sh start

# Остановить контейнер
./manage.sh stop

# Перезапустить контейнер
./manage.sh restart

# Показать статус
./manage.sh status

# Показать логи
./manage.sh logs

# Войти в контейнер
./manage.sh shell
```

### Сборка и обслуживание

```bash
# Пересобрать образ
./manage.sh build

# Инициализировать базу данных
./manage.sh init-db

# Очистить все данные (с подтверждением)
./manage.sh clean
```

## 🧪 Тестирование API

### Поиск по email

```bash
# Поиск информации по email
curl -X POST "http://localhost:8001/api/search" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "force_refresh": false}'

# Принудительное обновление данных
curl -X POST "http://localhost:8001/api/search" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "force_refresh": true}'
```

### Получение профиля

```bash
# Получить существующий профиль
curl "http://localhost:8001/api/profile/test@example.com"
```

### Статистика системы

```bash
# Общая статистика
curl "http://localhost:8001/api/stats"

# Проверка здоровья
curl "http://localhost:8001/health"
```

## 📊 Архитектура Docker setup

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Docker Host   │    │   EIC Container │    │   SQLite DB     │
│   (macOS)       │◄──►│   (FastAPI)     │◄──►│   (Persistent)  │
│   Port 8001     │    │   Port 8000     │    │   Volume        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Production Ready Features

- ✅ Health Checks
- ✅ Логирование 
- ✅ Graceful Shutdown
- ✅ Resource Limits
- ✅ Security (non-root user)
- ✅ Persistent Storage
- ✅ Auto-restart Policy

**Email Intelligence Collector успешно запущен в Docker! 🚀**
