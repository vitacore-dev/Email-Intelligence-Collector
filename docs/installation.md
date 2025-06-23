# Руководство по установке

Это подробное руководство поможет вам установить и настроить Email Intelligence Collector в различных окружениях.

## Системные требования

### Минимальные требования
- **CPU**: 2 ядра
- **RAM**: 4 GB
- **Диск**: 10 GB свободного места
- **ОС**: Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+

### Рекомендуемые требования
- **CPU**: 4+ ядра
- **RAM**: 8+ GB
- **Диск**: 50+ GB SSD
- **ОС**: Linux (Ubuntu 22.04+)

## Установка зависимостей

### Python 3.11+

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

#### macOS
```bash
brew install python@3.11
```

#### Windows
Скачайте и установите Python 3.11+ с [python.org](https://python.org)

### Node.js 18+

#### Ubuntu/Debian
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### macOS
```bash
brew install node@18
```

#### Windows
Скачайте и установите Node.js с [nodejs.org](https://nodejs.org)

### PostgreSQL 13+

#### Ubuntu/Debian
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Windows
Скачайте и установите PostgreSQL с [postgresql.org](https://postgresql.org)

### Redis 6+

#### Ubuntu/Debian
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Windows
Скачайте Redis для Windows или используйте WSL

## Установка через Docker (Рекомендуется)

### 1. Установка Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### macOS/Windows
Установите Docker Desktop с [docker.com](https://docker.com)

### 2. Клонирование репозитория
```bash
git clone https://github.com/vitacore-dev/Email-Intelligence-Collector.git
cd Email-Intelligence-Collector
```

### 3. Настройка переменных окружения
```bash
cp backend/.env.example backend/.env
```

Отредактируйте `backend/.env`:
```env
# База данных
DATABASE_URL=postgresql://postgres:password@db:5432/eic_db

# API ключи (получите на соответствующих платформах)
GOOGLE_API_KEY=your_google_api_key
GITHUB_API_KEY=your_github_token
TWITTER_API_KEY=your_twitter_api_key
LINKEDIN_API_KEY=your_linkedin_api_key

# Настройки безопасности
SECRET_KEY=your-very-secure-secret-key-here
```

### 4. Запуск системы
```bash
docker-compose up -d
```

### 5. Проверка работы
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API документация: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Elasticsearch: http://localhost:9200

## Ручная установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/vitacore-dev/Email-Intelligence-Collector.git
cd Email-Intelligence-Collector
```

### 2. Настройка Backend

#### Создание виртуального окружения
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

#### Установка зависимостей
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Настройка базы данных
```bash
# Создание пользователя и базы данных PostgreSQL
sudo -u postgres psql
```

В PostgreSQL консоли:
```sql
CREATE USER eic_user WITH PASSWORD 'your_password';
CREATE DATABASE eic_db OWNER eic_user;
GRANT ALL PRIVILEGES ON DATABASE eic_db TO eic_user;
\q
```

#### Настройка переменных окружения
```bash
cp .env.example .env
```

Отредактируйте `.env`:
```env
DATABASE_URL=postgresql://eic_user:your_password@localhost:5432/eic_db
```

#### Запуск миграций
```bash
alembic upgrade head
```

#### Запуск backend сервера
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Настройка Frontend

#### Установка зависимостей
```bash
cd ../frontend
npm install
```

#### Настройка переменных окружения
```bash
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

#### Запуск frontend сервера
```bash
npm run dev
```

## Настройка API ключей

### Google API
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Custom Search API
4. Создайте API ключ
5. Добавьте ключ в `.env` как `GOOGLE_API_KEY`

### GitHub API
1. Перейдите в [GitHub Settings](https://github.com/settings/tokens)
2. Создайте Personal Access Token
3. Выберите scope: `public_repo`, `user:email`
4. Добавьте токен в `.env` как `GITHUB_API_KEY`

### Twitter API
1. Подайте заявку на [Twitter Developer](https://developer.twitter.com/)
2. Создайте приложение
3. Получите API ключи
4. Добавьте ключи в `.env` как `TWITTER_API_KEY`

### LinkedIn API
1. Создайте приложение в [LinkedIn Developer](https://developer.linkedin.com/)
2. Получите Client ID и Client Secret
3. Добавьте в `.env` как `LINKEDIN_API_KEY`

## Настройка Elasticsearch (Опционально)

### Установка
```bash
# Ubuntu/Debian
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
sudo apt update
sudo apt install elasticsearch

# macOS
brew install elasticsearch

# Запуск
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
```

### Настройка
Добавьте в `.env`:
```env
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=email_profiles
```

## Настройка Nginx (Продакшн)

### Установка
```bash
sudo apt install nginx
```

### Конфигурация
Создайте файл `/etc/nginx/sites-available/eic`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API документация
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Активируйте конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/eic /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Мониторинг и логи

### Логи приложения
```bash
# Backend логи
tail -f backend/logs/eic.log

# Docker логи
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Системные логи
```bash
# Nginx логи
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# PostgreSQL логи
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

## Резервное копирование

### База данных
```bash
# Создание бэкапа
pg_dump -h localhost -U eic_user eic_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление
psql -h localhost -U eic_user eic_db < backup_20240101_120000.sql
```

### Файлы приложения
```bash
# Создание архива
tar -czf eic_backup_$(date +%Y%m%d_%H%M%S).tar.gz Email-Intelligence-Collector/
```

## Обновление системы

### Docker версия
```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

### Ручная установка
```bash
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart eic-backend

# Frontend
cd ../frontend
npm install
npm run build
sudo systemctl restart nginx
```

## Устранение неполадок

### Проблемы с базой данных
```bash
# Проверка подключения
psql -h localhost -U eic_user -d eic_db -c "SELECT version();"

# Пересоздание базы данных
dropdb eic_db
createdb eic_db
alembic upgrade head
```

### Проблемы с портами
```bash
# Проверка занятых портов
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :3000

# Остановка процессов
sudo kill -9 $(sudo lsof -t -i:8000)
```

### Проблемы с правами доступа
```bash
# Исправление прав на файлы
sudo chown -R $USER:$USER Email-Intelligence-Collector/
chmod +x scripts/*.sh
```

## Производительность

### Оптимизация PostgreSQL
Отредактируйте `/etc/postgresql/13/main/postgresql.conf`:
```
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### Оптимизация Redis
Отредактируйте `/etc/redis/redis.conf`:
```
maxmemory 512mb
maxmemory-policy allkeys-lru
```

Перезапустите сервисы:
```bash
sudo systemctl restart postgresql
sudo systemctl restart redis
```

## Безопасность

### Firewall
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 5432  # PostgreSQL только локально
sudo ufw deny 6379  # Redis только локально
```

### Обновления безопасности
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
```

### Мониторинг безопасности
```bash
# Установка fail2ban
sudo apt install fail2ban

# Настройка для Nginx
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

## Поддержка

Если у вас возникли проблемы с установкой:

1. Проверьте [FAQ](docs/faq.md)
2. Создайте [Issue на GitHub](https://github.com/vitacore-dev/Email-Intelligence-Collector/issues)
3. Обратитесь к [документации API](docs/api.md)
4. Напишите на support@vitacore.dev

