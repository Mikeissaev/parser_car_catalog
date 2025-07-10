# Tech Context - Toyota JDM Parser

## Технологический стек

### Основные технологии
- **Python 3.x**: Основной язык программирования
- **Selenium WebDriver**: Автоматизация браузера для веб-скрапинга
- **Chrome WebDriver**: Браузерный движок для парсинга
- **JSON**: Формат хранения и обмена данными

### Зависимости Python
```python
selenium>=4.0.0
webdriver-manager>=3.8.0
```

### Системные требования
- **ОС**: Windows 10 (текущая среда)
- **Python**: 3.7+
- **Chrome Browser**: Последняя версия
- **RAM**: Минимум 4GB для стабильной работы
- **Дисковое пространство**: 100MB+ для логов и данных

## Структура проекта

```
parser_car_catalog/
├── main.py                    # Базовый парсер моделей
├── frame_parse.py            # Расширенный парсер кузовов
├── toyota_jdm_models.json    # Результат парсинга моделей
├── toyota_jdm_frames.json    # Результат парсинга кузовов
├── page.html                 # Отладочный HTML файл
├── pyproject.toml           # Конфигурация проекта
├── README.md                # Документация проекта
├── .gitignore              # Git исключения
├── .python-version         # Версия Python
├── logs/                   # Директория логов
│   ├── toyota_parser.log
│   └── toyota_frame_parser.log
└── memory_bank/            # Документация проекта
    ├── projectbrief.md
    ├── productContext.md
    ├── systemPatterns.md
    ├── techContext.md
    ├── activeContext.md
    └── progress.md
```

## Конфигурация разработки

### Python Environment
- **Версия**: Указана в `.python-version`
- **Менеджер пакетов**: pip/poetry (pyproject.toml)
- **Виртуальное окружение**: Рекомендуется

### WebDriver Configuration
```python
# Chrome Options для production
options = webdriver.ChromeOptions()
options.add_argument("--headless")           # Без GUI
options.add_argument("--disable-gpu")        # Отключение GPU
options.add_argument("--no-sandbox")         # Безопасность
options.add_argument("--disable-dev-shm-usage")  # Memory management
options.add_argument("--window-size=1920,1080")  # Размер окна
```

### Logging Configuration
```python
# Настройка логирования
logger = logging.getLogger("toyota_frame_parser")
logger.setLevel(logging.INFO)

# Файловый обработчик
file_handler = logging.FileHandler("logs/toyota_frame_parser.log", encoding="utf-8")

# Консольный обработчик
console_handler = logging.StreamHandler()

# Форматтер
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
```

## Технические ограничения

### Сетевые ограничения
- **Rate Limiting**: Задержки между запросами (3+ секунды)
- **Timeout Settings**: 30 сек для загрузки страницы, 15 сек для элементов
- **User-Agent**: Эмуляция реального браузера

### Память и производительность
- **Headless Mode**: Экономия ресурсов
- **Batch Processing**: Обработка по частям для больших объемов
- **Resource Cleanup**: Обязательное закрытие WebDriver

### Обработка ошибок
- **Network Timeouts**: Автоматическое восстановление
- **Element Not Found**: Множественные селекторы
- **WebDriver Crashes**: Graceful shutdown

## Паттерны использования

### Запуск базового парсера
```bash
python main.py
```

### Запуск парсера кузовов
```bash
# Полный парсинг
python frame_parse.py

# Тестовый запуск (10 моделей)
# Изменить в коде: scrape_toyota_frames(max_models=10)

# Возобновление с 50-й модели
# Изменить в коде: scrape_toyota_frames(start_index=50)
```

### Мониторинг процесса
```bash
# Просмотр логов в реальном времени
tail -f logs/toyota_frame_parser.log

# Проверка статуса
ls -la *.json
```

## Интеграционные возможности

### Входные данные
- **toyota_jdm_models.json**: Список моделей от main.py
- **HTML структура**: Селекторы `ul.category2 h4 a`

### Выходные данные
- **toyota_jdm_frames.json**: Структурированные данные с кузовами
- **Логи**: Детальная информация о процессе парсинга

### API совместимость
- **JSON Schema**: Стандартизированная структура данных
- **REST-ready**: Данные готовы для REST API
- **Database-ready**: Структура подходит для реляционных БД

## Безопасность и этика

### Веб-скрапинг этика
- **Respectful crawling**: Задержки между запросами
- **robots.txt**: Соблюдение правил сайта
- **Rate limiting**: Предотвращение перегрузки сервера

### Обработка данных
- **UTF-8 encoding**: Корректная обработка японских символов
- **Error logging**: Отслеживание проблем без остановки
- **Data validation**: Проверка корректности извлеченных данных
