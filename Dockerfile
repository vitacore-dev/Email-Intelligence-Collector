# Email Intelligence Collector Docker Image - Comprehensive System
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    PORT=8000 \
    DEBUG=True \
    MAX_PROCESSING_TIME=300 \
    ENABLE_COMPREHENSIVE_ANALYSIS=True

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY backend/requirements.txt /app/backend_requirements.txt

# Устанавливаем основные зависимости
RUN pip install --upgrade pip && \
    pip install -r /app/backend_requirements.txt

# Дополнительные зависимости для поисковых систем
RUN pip install lxml beautifulsoup4 fake-useragent tldextract url-normalize

# Загружаем модель spaCy (если возможно)
RUN python -m spacy download en_core_web_sm || echo "spaCy модель не загружена"

# Копируем backend код
COPY backend/ /app/backend/

# Создаем необходимые директории
RUN mkdir -p /app/data && \
    mkdir -p /app/backend/logs && \
    chmod -R 755 /app

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Рабочая директория для backend
WORKDIR /app/backend

# Открываем порт
EXPOSE 8000

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
