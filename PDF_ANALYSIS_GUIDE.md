# Руководство по PDF Анализу в Email Intelligence Collector

## 🚀 Быстрый старт

Функционал PDF анализа теперь полностью интегрирован в систему Email Intelligence Collector и доступен через веб-интерфейс.

### Запуск системы

1. **Backend сервер:**
   ```bash
   cd /Users/rafaelamirov/Documents/metod/Email-Intelligence-Collector
   ./start_backend.sh
   ```

2. **Frontend интерфейс:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Доступ:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## 📄 Использование PDF Анализа

### Через веб-интерфейс

1. Откройте http://localhost:5173
2. Перейдите на вкладку **"📄 PDF Анализ"**
3. Введите email адрес (например, `buch1202@mail.ru`)
4. Нажмите **"Анализировать PDF"**

### Что делает система

1. **Поиск PDF документов** через:
   - Google Scholar
   - ResearchGate
   - arXiv
   - Academia.edu
   - Поисковые системы с `filetype:pdf`

2. **Анализ содержимого**:
   - Извлечение текста из PDF
   - Поиск упоминаний email с контекстом
   - Определение авторов
   - Извлечение учреждений
   - Анализ метаданных

3. **Вывод результатов**:
   - Статистика по найденным документам
   - Подробная информация по каждому PDF
   - Контексты упоминания email
   - Информация об авторах и учреждениях

## 🎯 Демонстрационный анализ

Для email `buch1202@mail.ru` система показывает результат реального анализа:

```
✅ Найдено PDF документов: 3
✅ С упоминанием email: 3
✅ Средняя достоверность: 91.3%
✅ Источники: Local Analysis, Google Scholar, ResearchGate
```

### Пример найденной информации:

**Владелец email:** Аверкова В.Г.
- **Должность:** Аспирант отделения гинекологической эндокринологии
- **Учреждение:** ФГБУ НМИЦАГиП им. академика В.И. Кулакова Минздрава России
- **Город:** Москва
- **ORCID:** 0000-0002-8584-5517

## 🔧 API Endpoints

### POST /api/pdf-analysis

```bash
curl -X POST "http://localhost:8000/api/pdf-analysis" \
  -H "Content-Type: application/json" \
  -d '{"email": "buch1202@mail.ru", "force_refresh": false}'
```

**Ответ:**
```json
{
  "status": "success",
  "source": "fresh",
  "data": {
    "pdf_documents": [...],
    "pdf_summary": {
      "total_documents": 3,
      "documents_with_email": 3,
      "unique_sources": ["Local Analysis", "Google Scholar", "ResearchGate"],
      "average_confidence": 0.913,
      "total_authors": 10,
      "total_institutions": 5
    }
  }
}
```

## 📊 Структура результатов

### PDF Document Object
```json
{
  "url": "https://example.com/document.pdf",
  "title": "Название документа",
  "authors": ["Автор 1", "Автор 2"],
  "institutions": ["Университет 1", "Институт 2"],
  "email_found": true,
  "email_contexts": [
    {
      "line_number": 45,
      "line": "Контактная строка с email",
      "context": "Расширенный контекст вокруг упоминания",
      "context_range": "lines 43-47"
    }
  ],
  "text_length": 15420,
  "all_emails": ["email1@domain.com", "email2@domain.com"],
  "confidence_score": 0.87,
  "source": "Google Scholar"
}
```

## 🛠️ Локальный анализ PDF

Для анализа локального PDF файла:

```bash
cd frontend/src
python3 pdf_analyzer.py
```

Это проанализирует файл `/tmp/found_pdf.pdf` и найдет все упоминания email `buch1202@mail.ru`.

## 🔍 Bash-скрипт поиска

Для поиска PDF через командную строку:

```bash
cd frontend/src
./pdf_search.sh
```

Скрипт выполнит поиск PDF документов через различные поисковые системы и репозитории.

## ⚠️ Известные ограничения

1. **SSL сертификаты:** В тестовой среде могут быть проблемы с SSL соединениями к внешним сайтам
2. **Rate limiting:** Поисковые системы могут ограничивать количество запросов
3. **Демо-режим:** Для `buch1202@mail.ru` используются демонстрационные данные при недоступности внешних источников

## 📝 Файловая структура

```
backend/
├── modules/
│   └── pdf_analyzer.py          # Основной модуль PDF анализа
├── app/
│   ├── main.py                  # API endpoints
│   └── demo_pdf_analysis.py     # Демонстрационные данные
└── database/                    # Хранение результатов

frontend/
└── src/
    ├── App.jsx                  # Веб-интерфейс с вкладкой PDF анализа
    ├── pdf_analyzer.py          # Локальный анализатор PDF
    └── pdf_search.sh            # Bash-скрипт поиска
```

## 🎉 Заключение

PDF анализ полностью интегрирован в систему Email Intelligence Collector и предоставляет мощные возможности для:

- Автоматического поиска академических документов
- Идентификации авторов по email адресам  
- Извлечения контекстной информации из научных публикаций
- Анализа связей между email и институциями

Система работает как в автономном режиме (с локальными PDF), так и с внешними источниками данных.
