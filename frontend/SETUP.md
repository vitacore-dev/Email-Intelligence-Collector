# Быстрый старт Frontend

## ⚠️ Требования к системе

Для работы проекта необходимо:
- **Node.js версии 18 или выше** (текущая версия v12.13.0 устарела)
- npm или pnpm

## 🚀 Обновление Node.js

### Вариант 1: Через nvm (рекомендуется)
```bash
# Установите nvm, если ещё не установлен
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Перезапустите терминал или выполните:
source ~/.bashrc

# Установите последнюю LTS версию Node.js
nvm install --lts
nvm use --lts
```

### Вариант 2: Через официальный сайт
Скачайте и установите Node.js 18+ с [nodejs.org](https://nodejs.org/)

## 📦 Запуск проекта

После обновления Node.js:

```bash
# Перейдите в папку frontend
cd /Users/rafaelamirov/Documents/metod/Email-Intelligence-Collector/frontend

# Установите зависимости
npm install

# Запустите в режиме разработки
npm run dev
```

## 🎯 Что добавлено

### 1. API Service
- Централизованная работа с backend API
- Поддержка всех эндпоинтов цифрового двойника
- Обработка ошибок

### 2. Компонент DigitalTwin
- Табы: Обзор, Сеть, Временная линия, Метрики
- Интерактивные визуализации
- Экспорт данных в JSON/PDF

### 3. Компоненты визуализации
- **ResearchRadarChart**: Радарная диаграмма навыков
- **CollaborationNetwork**: Сеть сотрудничества
- **ResearchTimeline**: Временная линия активности
- **MetricsDisplay**: Детальные метрики

### 4. Улучшения UI
- Новая вкладка "Цифровой двойник"
- Поиск с автодополнением
- Адаптивный дизайн

## 🔗 Интеграция с Backend

Убедитесь, что backend запущен на порту 8001 с поддержкой эндпоинтов:
- `/api/digital-twin/{email}`
- `/api/visualization/{email}`
- `/api/network-analysis/{email}`
- И другие (см. README.md)

## 📊 Демо данные

Компоненты включают демо-данные для тестирования без backend:
- Фиктивные метрики исследователя
- Примеры сетей сотрудничества
- Тестовые временные линии

## 🚨 Устранение проблем

### Ошибка "Cannot use import statement"
- Обновите Node.js до версии 18+
- Убедитесь, что в package.json есть `"type": "module"`

### API ошибки
- Проверьте, что backend запущен на localhost:8001
- Убедитесь в настройке CORS
- Откройте Network tab в DevTools для отладки

## ✅ Проверка готовности

После запуска откройте [http://localhost:5173](http://localhost:5173) и:

1. Перейдите на вкладку "Цифровой двойник"
2. Введите тестовый email: `test@example.com`
3. Нажмите "Создать цифрового двойника"
4. Проверьте отображение демо-данных

## 📁 Структура файлов

```
frontend/
├── src/
│   ├── components/
│   │   ├── DigitalTwin.jsx           # Главный компонент
│   │   ├── SearchWithSuggestions.jsx # Поиск с автодополнением
│   │   └── visualizations/           # Компоненты визуализации
│   │       ├── ResearchRadarChart.jsx
│   │       ├── CollaborationNetwork.jsx
│   │       ├── ResearchTimeline.jsx
│   │       └── MetricsDisplay.jsx
│   ├── services/
│   │   └── api.js                    # API клиент
│   └── App.jsx                       # Основное приложение
├── README.md                         # Подробная документация
└── SETUP.md                          # Быстрый старт
```
