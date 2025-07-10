# System Patterns - Toyota JDM Parser

## Архитектура системы

### Модульная структура
- **main.py**: Базовый парсер моделей Toyota
- **frame_parse.py**: Расширенный парсер кузовов с улучшенным функционалом
- **logs/**: Директория для файлов логирования
- **memory_bank/**: Документация и контекст проекта

### Паттерн "Pipeline Processing"
```
Главная страница → Список моделей → Страницы моделей → Кузова → JSON
```

## Ключевые технические решения

### 1. Selenium WebDriver
- **Выбор**: Chrome WebDriver с автоматической установкой через webdriver_manager
- **Конфигурация**: Headless режим для производительности
- **Таймауты**: Настраиваемые таймауты для стабильности

### 2. Система логирования
- **Двойное логирование**: Файл + консоль
- **Уровни**: INFO для основных событий, DEBUG для деталей, ERROR для ошибок
- **Кодировка**: UTF-8 для корректного отображения русского текста

### 3. Обработка ошибок
- **Graceful degradation**: Продолжение работы при ошибках отдельных элементов
- **Retry logic**: Множественные селекторы для поиска элементов
- **Resource cleanup**: Гарантированное закрытие WebDriver

### 4. Структура данных
```json
{
  "parsing_info": {
    "timestamp": "ISO datetime",
    "total_models_processed": "number",
    "total_frames_found": "number",
    "start_index": "number",
    "end_index": "number"
  },
  "models": [
    {
      "name": "Model Name",
      "frame_name_url": "URL",
      "frames": [
        {
          "frame_name": "Frame Code",
          "frame_url": "Frame URL"
        }
      ],
      "frames_count": "number"
    }
  ]
}
```

## Паттерны селекторов

### Приоритетные селекторы для кузовов:
1. `"ul.category2 h4 a"` - Основной селектор
2. `"table ul.category2 h4 a"` - Более специфичный
3. `".category2 a"` - Альтернативный
4. `"ul.category2 a"` - Запасной вариант

### Стратегия поиска элементов:
- Последовательная проверка селекторов
- Остановка на первом успешном результате
- Логирование используемого селектора

## Управление ресурсами

### WebDriver Management
- Инициализация с проверкой ошибок
- Настройка таймаутов на уровне драйвера
- Обязательное закрытие в блоке finally

### Memory Management
- Очистка списков элементов после обработки
- Минимизация хранения DOM элементов
- Периодическая сборка мусора при длительной работе

## Масштабируемость

### Batch Processing
- Возможность парсинга по частям (start_index, max_models)
- Настраиваемые задержки между запросами
- Сохранение промежуточных результатов

### Error Recovery
- Логирование ошибок без остановки процесса
- Пропуск проблемных моделей
- Возможность возобновления с любого индекса

## Конфигурационные паттерны

### Chrome Options
```python
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
```

### Timeout Configuration
- Page load timeout: 30 секунд
- Implicit wait: 10 секунд
- Explicit wait: 15 секунд
- Custom wait between requests: 3 секунды (настраиваемо)
