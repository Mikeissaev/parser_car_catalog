# Инструкция по использованию Toyota JDM Frame Parser

## Обзор

Проект состоит из двух основных компонентов:
1. **main.py** - парсер списка моделей Toyota
2. **frame_parse.py** - парсер кузовов для каждой модели

## Предварительные требования

### Системные требования
- Python 3.7+
- Google Chrome (последняя версия)
- Интернет соединение

### Установка зависимостей
```bash
pip install selenium webdriver-manager
```

## Пошаговое использование

### Шаг 1: Парсинг списка моделей (если еще не выполнен)
```bash
python main.py
```
**Результат**: Создается файл `toyota_jdm_models.json` со списком всех моделей Toyota.

### Шаг 2: Парсинг кузовов

#### Тестовый запуск (рекомендуется для первого раза)
Отредактируйте файл `frame_parse.py`, найдите строку в конце файла:
```python
# Парсинг всех моделей
scrape_toyota_frames()
```

Замените на:
```python
# Тестовый запуск (5 моделей)
scrape_toyota_frames(max_models=5, delay_between_requests=2)
```

Затем запустите:
```bash
python frame_parse.py
```

#### Полный парсинг всех моделей
После успешного тестирования верните настройки:
```python
# Парсинг всех моделей
scrape_toyota_frames()
```

И запустите:
```bash
python frame_parse.py
```

## Варианты конфигурации

### Возобновление парсинга с определенной модели
```python
# Начать с 50-й модели
scrape_toyota_frames(start_index=50)
```

### Парсинг диапазона моделей
```python
# Парсить 30 моделей начиная с 20-й
scrape_toyota_frames(start_index=20, max_models=30)
```

### Настройка задержек
```python
# Увеличить задержку до 5 секунд между запросами
scrape_toyota_frames(delay_between_requests=5)
```

## Мониторинг процесса

### Просмотр логов в реальном времени
```bash
# Windows PowerShell
Get-Content logs/toyota_frame_parser.log -Wait

# Или просто откройте файл в текстовом редакторе
```

### Проверка результатов
```bash
# Проверить размер созданного файла
ls -la toyota_jdm_frames.json

# Посмотреть первые строки результата
head toyota_jdm_frames.json
```

## Структура результата

Файл `toyota_jdm_frames.json` содержит:
```json
{
  "parsing_info": {
    "timestamp": "2025-01-10T19:22:07.123456",
    "total_models_processed": 127,
    "total_frames_found": 850,
    "start_index": 0,
    "end_index": 126
  },
  "models": [
    {
      "name": "86",
      "frame_name_url": "https://toyota.epc-data.com/86/",
      "frames": [
        {
          "frame_name": "ZN6",
          "frame_url": "https://toyota.epc-data.com/86/zn6/"
        }
      ],
      "frames_count": 1
    }
  ]
}
```

## Устранение проблем

### Проблема: "Файл toyota_jdm_models.json не найден"
**Решение**: Сначала запустите `python main.py` для создания списка моделей.

### Проблема: "Chrome binary not found"
**Решение**: Установите Google Chrome или убедитесь, что он добавлен в PATH.

### Проблема: Парсер не находит кузова
**Решение**: 
1. Проверьте интернет соединение
2. Увеличьте задержки между запросами
3. Проверите логи на наличие ошибок

### Проблема: Процесс останавливается
**Решение**:
1. Проверьте логи для выявления ошибки
2. Возобновите парсинг с последнего успешного индекса
3. Увеличьте таймауты в коде

## Оптимизация производительности

### Для быстрого тестирования
```python
scrape_toyota_frames(max_models=10, delay_between_requests=1)
```

### Для стабильного парсинга
```python
scrape_toyota_frames(delay_between_requests=5)
```

### Для парсинга больших объемов
```python
# Парсить по частям
scrape_toyota_frames(start_index=0, max_models=50)
scrape_toyota_frames(start_index=50, max_models=50)
scrape_toyota_frames(start_index=100)
```

## Ожидаемое время выполнения

- **Тестовый запуск (5 моделей)**: ~30 секунд
- **Полный парсинг (127 моделей)**: ~6-10 минут
- **Время зависит от**: скорости интернета, нагрузки на сервер, настроек задержек

## Файлы результатов

После выполнения у вас будут созданы:
- `toyota_jdm_models.json` - список моделей
- `toyota_jdm_frames.json` - модели с кузовами
- `logs/toyota_frame_parser.log` - подробные логи процесса

## Дополнительные возможности

### Изменение селекторов
Если структура сайта изменилась, отредактируйте список селекторов в функции `parse_frames_from_model_page`:
```python
frame_selectors = [
    "ul.category2 h4 a",      # Основной селектор
    "table ul.category2 h4 a", # Более специфичный
    ".category2 a",           # Альтернативный
    "ul.category2 a",         # Запасной вариант
]
```

### Отладка
Для отладки конкретной модели добавьте в код:
```python
# Сохранение HTML страницы для анализа
with open(f"debug_{model_name}.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)
```

## Поддержка

При возникновении проблем:
1. Проверьте логи в директории `logs/`
2. Убедитесь в наличии всех зависимостей
3. Проверьте доступность сайта toyota.epc-data.com
4. Обратитесь к документации в директории `memory_bank/`
