# 🐳 Docker Setup Guide для Email Intelligence Collector

## 📋 Предварительные требования

Для запуска проекта с Docker необходимо установить:
- Docker Desktop для macOS
- Docker Compose (входит в Docker Desktop)

## 🚀 Установка Docker на macOS

### Вариант 1: Docker Desktop (Рекомендуется)

1. **Скачайте Docker Desktop**:
   - Перейдите на https://www.docker.com/products/docker-desktop
   - Скачайте версию для macOS (Apple Silicon или Intel)

2. **Установите Docker Desktop**:
   - Откройте скачанный `.dmg` файл
   - Перетащите Docker в папку Applications
   - Запустите Docker Desktop из Applications

3. **Проверьте установку**:
   ```bash
   docker --version
   docker-compose --version
   ```

### Вариант 2: Homebrew

```bash
# Установите Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установите Docker
brew install --cask docker

# Запустите Docker Desktop
open /Applications/Docker.app
```

## 🔧 Настройка проекта

После установки Docker:

1. **Клонируйте проект** (если еще не сделано):
   ```bash
   git clone https://github.com/vitacore-dev/Email-Intelligence-Collector.git
   cd Email-Intelligence-Collector
   ```

2. **Настройте переменные окружения**:
   ```bash
   cp .env .env.local
   # Отредактируйте .env.local под ваши нужды
   ```

3. **Запустите проект**:
   ```bash
   # Для разработки
   make dev-build
   make dev-up
   
   # Для production
   make build
   make up
   ```

## 🎯 Быстрый старт

### Минимальная конфигурация для тестирования

1. **Создайте упрощенный docker-compose**:
   ```bash
   # Копируем development конфигурацию
   cp docker-compose.dev.yml docker-compose.override.yml
   ```

2. **Запустите только необходимые сервисы**:
   ```bash
   docker-compose up backend redis
   ```

### Пошаговая проверка

1. **Проверьте Docker**:
   ```bash
   docker --version
   # Должно показать: Docker version 20.x.x или выше
   ```

2. **Проверьте Docker Compose**:
   ```bash
   docker-compose --version
   # Должно показать: docker-compose version 1.29.x или выше
   ```

3. **Соберите backend образ**:
   ```bash
   cd Email-Intelligence-Collector
   docker-compose build backend
   ```

4. **Запустите базовые сервисы**:
   ```bash
   docker-compose up -d redis
   docker-compose up backend
   ```

## 🛠️ Альтернативы без Docker

Если Docker не подходит, используйте локальную установку:

### Вариант 1: Локальный запуск (уже настроен)

```bash
cd Email-Intelligence-Collector
./start_backend.sh
```

### Вариант 2: Python virtual environment

```bash
cd Email-Intelligence-Collector/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📊 Архитектура без внешних зависимостей

Для упрощенного тестирования без PostgreSQL/Elasticsearch:

```yaml
# docker-compose.simple.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/eic.sqlite
      - DEBUG=True
    volumes:
      - ./backend/data:/app/data
      - ./backend/logs:/app/logs
```

Запуск:
```bash
docker-compose -f docker-compose.simple.yml up
```

## 🔍 Диагностика проблем

### Проблемы с Docker

1. **Docker не запускается**:
   ```bash
   # Перезапустите Docker Desktop
   killall Docker && open /Applications/Docker.app
   ```

2. **Нет доступа к Docker daemon**:
   ```bash
   # Убедитесь что Docker Desktop запущен
   docker ps
   ```

3. **Ошибки сборки**:
   ```bash
   # Очистите Docker кэш
   docker system prune -f
   docker builder prune -f
   ```

### Проблемы с портами

```bash
# Проверьте занятые порты
lsof -i :8000
lsof -i :3000
lsof -i :5432

# Завершите процессы если нужно
kill -9 <PID>
```

## 📝 Конфигурационные файлы

Проект включает следующие Docker конфигурации:

- `docker-compose.yml` - Production конфигурация
- `docker-compose.dev.yml` - Development конфигурация  
- `Dockerfile` (backend) - Multi-stage образ с оптимизацией
- `Dockerfile` (frontend) - React + Nginx образ
- `Makefile` - Упрощенное управление

## 🎉 После успешной установки

Когда Docker установлен и настроен:

1. **Проверьте статус сервисов**:
   ```bash
   make status
   ```

2. **Откройте приложение**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

3. **Мониторинг логов**:
   ```bash
   make logs
   ```

## 🆘 Помощь

Если возникли проблемы:

1. Проверьте Docker Desktop в системном трее/dock
2. Убедитесь что Docker Desktop полностью запущен
3. Попробуйте перезапустить Docker Desktop
4. Используйте альтернативный локальный запуск

**Docker конфигурация готова! 🚀**
