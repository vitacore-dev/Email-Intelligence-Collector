# 🐳 Docker Commands для Frontend

## ✅ Текущий статус

✅ **Frontend запущен в Docker!**
- Контейнер: `eic-frontend-dev`
- Порт: http://localhost:5173
- Node.js версия: 18
- Сборщик: Vite + React

## 🚀 Основные команды

### Проверить статус
```bash
docker ps | grep eic-frontend
```

### Просмотреть логи
```bash
docker logs eic-frontend-dev
docker logs -f eic-frontend-dev  # следить за логами в реальном времени
```

### Остановить/запустить
```bash
docker stop eic-frontend-dev
docker start eic-frontend-dev
```

### Перезапустить
```bash
docker restart eic-frontend-dev
```

### Удалить контейнер (если нужно пересобрать)
```bash
docker stop eic-frontend-dev
docker rm eic-frontend-dev
```

### Пересобрать образ
```bash
docker build -t eic-frontend:latest .
```

### Полный перезапуск
```bash
docker stop eic-frontend-dev && docker rm eic-frontend-dev
docker build -t eic-frontend:latest .
docker run -d -p 5173:5173 --name eic-frontend-dev eic-frontend:latest
```

## 🔧 Разработка с Docker

### Войти в контейнер для отладки
```bash
docker exec -it eic-frontend-dev sh
```

### Установить новые пакеты
```bash
# 1. Остановить контейнер
docker stop eic-frontend-dev

# 2. Добавить пакет в package.json

# 3. Пересобрать образ
docker build -t eic-frontend:latest .

# 4. Запустить заново
docker run -d -p 5173:5173 --name eic-frontend-dev eic-frontend:latest
```

### Просмотреть файлы в контейнере
```bash
docker exec eic-frontend-dev ls -la /app
```

## 🌐 Доступ к приложению

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001

### Тестирование
```bash
# Проверить доступность
curl http://localhost:5173

# Проверить API
curl http://localhost:8001/api/stats
```

## 📊 Что работает

✅ **Полный frontend с цифровым двойником**
- React + Vite + Tailwind CSS
- Все компоненты визуализации
- API интеграция с backend
- Responsive дизайн
- Radix UI компоненты

### Основные страницы:
1. **Одиночный поиск** - поиск по email
2. **Цифровой двойник** - полный анализ исследователя
   - Профиль и метрики
   - Радарная диаграмма
   - Сеть сотрудничества  
   - Временная линия
   - Детальная аналитика

## 🔄 Интеграция с Backend

Frontend автоматически подключается к backend API:
- Backend: `eic-app` контейнер (порт 8001)
- API Base URL: `http://localhost:8001/api`

### Эндпоинты для цифрового двойника:
- `/api/digital-twin/{email}`
- `/api/visualization/{email}`
- `/api/research-metrics/{email}`
- И другие...

## 🚨 Устранение проблем

### Контейнер не запускается
```bash
docker logs eic-frontend-dev
# Посмотреть ошибки и пересобрать при необходимости
```

### Порт занят
```bash
# Найти процесс на порту 5173
lsof -i :5173

# Или изменить порт в Dockerfile и пересобрать
```

### Проблемы с зависимостями
```bash
# Полная пересборка без кэша
docker build --no-cache -t eic-frontend:latest .
```

## 🎉 Готово к использованию!

Откройте http://localhost:5173 в браузере и тестируйте цифрового двойника! 🚀
