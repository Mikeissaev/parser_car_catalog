import json
import time
import logging
import os
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)


def setup_logging():
    """Настройка системы логирования"""
    # Создаем директорию для логов если её нет
    os.makedirs("logs", exist_ok=True)

    # Настройка логгера
    logger = logging.getLogger("toyota_frame_parser")
    logger.setLevel(logging.INFO)

    # Удаляем существующие обработчики чтобы избежать дублирования
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Создаем обработчик для записи в файл
    file_handler = logging.FileHandler("logs/toyota_frame_parser.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Создаем форматтер
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def load_models_data():
    """Загружает данные моделей из JSON файла"""
    try:
        with open("toyota_jdm_models.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            "Файл toyota_jdm_models.json не найден. Сначала запустите main.py для получения списка моделей."
        )
    except json.JSONDecodeError:
        raise ValueError("Ошибка при чтении JSON файла toyota_jdm_models.json")


def get_random_user_agent():
    """Возвращает случайный User-Agent для обхода блокировки"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    return random.choice(user_agents)


def setup_driver(use_random_ua=False):
    """Настройка и инициализация Chrome WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Запуск в фоновом режиме
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1920,1080")

    # Используем случайный User-Agent если указано
    if use_random_ua:
        user_agent = get_random_user_agent()
        options.add_argument(f"--user-agent={user_agent}")
    else:
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    # Инициализация драйвера
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # Скрываем признаки автоматизации
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    # Настройка таймаутов
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(30)

    return driver


def parse_frames_from_model_page_with_retry(
    driver, model_url, model_name, logger, wait_time=3, max_retries=5
):
    """
    Парсит кузова (frames) с страницы конкретной модели с retry логикой

    Args:
        driver: WebDriver instance
        model_url: URL страницы модели
        model_name: Название модели
        logger: Logger instance
        wait_time: Время ожидания между запросами
        max_retries: Максимальное количество попыток

    Returns:
        list: Список словарей с данными о кузовах
    """
    frames = []

    # Расширенный список селекторов для поиска кузовов
    frame_selectors = [
        "ul.category2 h4 a",  # Основной селектор из примера HTML
        "table ul.category2 h4 a",  # Более специфичный селектор
        ".category2 a",  # Альтернативный селектор
        "ul.category2 a",  # Еще один вариант
        "li h4 a",  # Общий селектор для заголовков в списках
        "table a[href*='/']",  # Ссылки в таблицах
        "div.category2 a",  # Если используются div вместо ul
        "a[href*='/"
        + model_name.lower().replace(" ", "_")
        + "/']",  # Ссылки содержащие имя модели
    ]

    # Различные стратегии обхода блокировки
    retry_strategies = [
        {"wait_time": wait_time, "use_js": False, "clear_cache": False},
        {"wait_time": wait_time * 2, "use_js": True, "clear_cache": False},
        {"wait_time": wait_time * 3, "use_js": False, "clear_cache": True},
        {"wait_time": wait_time * 2, "use_js": True, "clear_cache": True},
        {"wait_time": wait_time * 4, "use_js": True, "clear_cache": True},
    ]

    for attempt in range(max_retries):
        try:
            strategy = retry_strategies[min(attempt, len(retry_strategies) - 1)]

            logger.info(
                f"Попытка {attempt + 1}/{max_retries} парсинга модели {model_name}"
            )
            logger.debug(
                f"Стратегия: wait={strategy['wait_time']}s, js={strategy['use_js']}, clear_cache={strategy['clear_cache']}"
            )

            # Очистка кэша если требуется
            if strategy["clear_cache"] and attempt > 0:
                try:
                    driver.delete_all_cookies()
                    driver.execute_script("window.localStorage.clear();")
                    driver.execute_script("window.sessionStorage.clear();")
                    logger.debug("Кэш и cookies очищены")
                except Exception as e:
                    logger.warning(f"Ошибка при очистке кэша: {e}")

            # Переходим на страницу модели
            driver.get(model_url)

            # Ждем загрузки страницы
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Дополнительная пауза для полной загрузки контента
            time.sleep(strategy["wait_time"])

            # Если используем JavaScript, прокручиваем страницу для загрузки контента
            if strategy["use_js"]:
                try:
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    time.sleep(2)
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"Ошибка при прокрутке страницы: {e}")

            # Пробуем разные селекторы
            frame_elements = []
            for selector in frame_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        frame_elements = elements
                        logger.info(
                            f"Найдено {len(elements)} кузовов с селектором: {selector}"
                        )
                        break
                except Exception as e:
                    logger.debug(f"Ошибка с селектором {selector}: {e}")
                    continue

            # Если элементы найдены, извлекаем данные
            if frame_elements:
                for element in frame_elements:
                    try:
                        frame_name = element.text.strip()
                        frame_url = element.get_attribute("href")

                        if frame_name and frame_url:
                            frames.append(
                                {"frame_name": frame_name, "frame_url": frame_url}
                            )
                            logger.debug(f"Найден кузов: {frame_name} -> {frame_url}")

                    except Exception as e:
                        logger.warning(f"Ошибка при извлечении данных кузова: {e}")
                        continue

                if frames:
                    logger.info(
                        f"Успешно извлечено {len(frames)} кузовов для модели {model_name}"
                    )
                    return frames
                else:
                    logger.warning(
                        f"Элементы найдены, но данные не извлечены для модели {model_name}"
                    )

            # Если кузова не найдены, пробуем альтернативные методы
            if not frames:
                logger.warning(
                    f"Попытка {attempt + 1}: Кузова не найдены для модели {model_name}"
                )

                # Сохраняем HTML для отладки при последней попытке
                if attempt == max_retries - 1:
                    try:
                        debug_filename = f"debug_{model_name.replace(' ', '_').replace('/', '_')}_attempt_{attempt + 1}.html"
                        with open(debug_filename, "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        logger.info(
                            f"HTML страницы сохранен в {debug_filename} для отладки"
                        )
                    except Exception as e:
                        logger.warning(f"Ошибка при сохранении HTML: {e}")

                # Увеличиваем задержку перед следующей попыткой
                if attempt < max_retries - 1:
                    retry_delay = random.uniform(3, 8)
                    logger.info(
                        f"Пауза {retry_delay:.1f} сек. перед следующей попыткой"
                    )
                    time.sleep(retry_delay)

        except TimeoutException:
            logger.warning(
                f"Попытка {attempt + 1}: Таймаут при загрузке страницы модели {model_name}"
            )
        except WebDriverException as e:
            logger.warning(
                f"Попытка {attempt + 1}: Ошибка WebDriver при парсинге модели {model_name}: {e}"
            )
        except Exception as e:
            logger.warning(
                f"Попытка {attempt + 1}: Неожиданная ошибка при парсинге модели {model_name}: {e}"
            )

        # Пауза между попытками (кроме последней)
        if attempt < max_retries - 1:
            retry_delay = random.uniform(2, 5)
            time.sleep(retry_delay)

    # Если все попытки неудачны
    logger.error(
        f"Не удалось получить кузова для модели {model_name} после {max_retries} попыток"
    )
    return frames


def parse_frames_from_model_page(driver, model_url, model_name, logger, wait_time=3):
    """
    Обертка для функции парсинга с retry логикой
    """
    return parse_frames_from_model_page_with_retry(
        driver, model_url, model_name, logger, wait_time
    )


def scrape_toyota_frames(start_index=0, max_models=None, delay_between_requests=3):
    """
    Основная функция для парсинга кузовов Toyota

    Args:
        start_index: Индекс модели с которой начать парсинг (для возобновления)
        max_models: Максимальное количество моделей для парсинга (None = все)
        delay_between_requests: Задержка между запросами в секундах
    """
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск парсера кузовов Toyota")
    logger.info(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    driver = None

    try:
        # Загружаем данные моделей
        logger.info("Загрузка данных моделей из toyota_jdm_models.json")
        models_data = load_models_data()
        models = models_data.get("models", [])

        if not models:
            logger.error("Список моделей пуст")
            return

        # Определяем диапазон моделей для парсинга
        end_index = (
            len(models)
            if max_models is None
            else min(start_index + max_models, len(models))
        )
        models_to_process = models[start_index:end_index]

        logger.info(f"Всего моделей в файле: {len(models)}")
        logger.info(
            f"Будет обработано моделей: {len(models_to_process)} (с {start_index} по {end_index-1})"
        )

        # Инициализация драйвера
        logger.info("Инициализация Chrome WebDriver")
        driver = setup_driver()
        logger.info("WebDriver успешно инициализирован")

        # Структура для результата
        result_data = {
            "parsing_info": {
                "timestamp": datetime.now().isoformat(),
                "total_models_processed": 0,
                "total_frames_found": 0,
                "start_index": start_index,
                "end_index": end_index - 1,
            },
            "models": [],
        }

        # Счетчики для статистики
        models_with_zero_frames = 0
        models_retried = 0

        # Парсинг каждой модели
        for i, model in enumerate(models_to_process, start=start_index):
            model_name = model.get("name", "Unknown")
            model_url = model.get("frame_name_url", "")

            logger.info(f"[{i+1}/{len(models)}] Обработка модели: {model_name}")

            if not model_url:
                logger.warning(f"URL не найден для модели {model_name}")
                continue

            # Парсим кузова для текущей модели
            frames = parse_frames_from_model_page(
                driver, model_url, model_name, logger, delay_between_requests
            )

            # Если кузова не найдены, пробуем дополнительные методы
            if not frames:
                models_with_zero_frames += 1
                logger.warning(
                    f"⚠️ Модель {model_name} имеет 0 кузовов - это подозрительно!"
                )

                # Пробуем с другим User-Agent
                logger.info(
                    f"Попытка с новым WebDriver и случайным User-Agent для {model_name}"
                )
                try:
                    # Закрываем текущий драйвер
                    driver.quit()

                    # Создаем новый с случайным User-Agent
                    driver = setup_driver(use_random_ua=True)
                    models_retried += 1

                    # Увеличенная пауза перед повторной попыткой
                    retry_delay = random.uniform(5, 10)
                    logger.info(
                        f"Пауза {retry_delay:.1f} сек. перед повторной попыткой"
                    )
                    time.sleep(retry_delay)

                    # Повторная попытка парсинга
                    frames = parse_frames_from_model_page_with_retry(
                        driver,
                        model_url,
                        model_name,
                        logger,
                        delay_between_requests * 2,
                        max_retries=3,
                    )

                    if frames:
                        logger.info(
                            f"✅ Успешно получены кузова для {model_name} после смены User-Agent"
                        )
                        models_with_zero_frames -= 1
                    else:
                        logger.error(
                            f"❌ Не удалось получить кузова для {model_name} даже после смены User-Agent"
                        )

                except Exception as e:
                    logger.error(
                        f"Ошибка при смене WebDriver для модели {model_name}: {e}"
                    )
                    # Пересоздаем драйвер в случае ошибки
                    try:
                        driver = setup_driver()
                    except Exception as e2:
                        logger.error(
                            f"Критическая ошибка при пересоздании WebDriver: {e2}"
                        )
                        break

            # Добавляем данные модели с кузовами в результат
            model_data = {
                "name": model_name,
                "frame_name_url": model_url,
                "frames": frames,
                "frames_count": len(frames),
            }

            result_data["models"].append(model_data)
            result_data["parsing_info"]["total_frames_found"] += len(frames)

            # Логирование результата
            if len(frames) > 0:
                logger.info(f"✅ Модель {model_name}: найдено {len(frames)} кузовов")
            else:
                logger.warning(f"⚠️ Модель {model_name}: найдено {len(frames)} кузовов")

            # Пауза между запросами для избежания блокировки
            if i < end_index - 1:  # Не делаем паузу после последней модели
                base_delay = delay_between_requests
                # Увеличиваем задержку если было много неудачных попыток
                if models_with_zero_frames > 3:
                    base_delay *= 2
                    logger.debug(
                        f"Увеличена задержка до {base_delay} сек. из-за проблем с парсингом"
                    )

                logger.debug(f"Пауза {base_delay} сек. перед следующим запросом")
                time.sleep(base_delay)

        # Дополнительная статистика
        result_data["parsing_info"]["models_with_zero_frames"] = models_with_zero_frames
        result_data["parsing_info"]["models_retried"] = models_retried

        # Обновляем статистику
        result_data["parsing_info"]["total_models_processed"] = len(
            result_data["models"]
        )

        # Сохраняем результат в файл
        output_filename = "toyota_jdm_frames.json"
        logger.info(f"Сохранение результатов в файл: {output_filename}")

        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

        # Финальная статистика
        logger.info("=" * 60)
        logger.info("ПАРСИНГ ЗАВЕРШЕН")
        logger.info(
            f"Обработано моделей: {result_data['parsing_info']['total_models_processed']}"
        )
        logger.info(
            f"Найдено кузовов: {result_data['parsing_info']['total_frames_found']}"
        )
        logger.info(f"Моделей с 0 кузовов: {models_with_zero_frames}")
        logger.info(f"Моделей с повторными попытками: {models_retried}")

        # Вычисляем процент успешности
        total_processed = result_data["parsing_info"]["total_models_processed"]
        success_rate = (
            ((total_processed - models_with_zero_frames) / total_processed * 100)
            if total_processed > 0
            else 0
        )
        logger.info(f"Процент успешности: {success_rate:.1f}%")

        if models_with_zero_frames > 0:
            logger.warning(
                f"⚠️ ВНИМАНИЕ: {models_with_zero_frames} моделей имеют 0 кузовов - требуется проверка!"
            )
        else:
            logger.info("✅ Все модели успешно обработаны!")

        logger.info(f"Результат сохранен в: {output_filename}")
        logger.info(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

    except FileNotFoundError as e:
        logger.error(f"Файл не найден: {e}")
    except ValueError as e:
        logger.error(f"Ошибка данных: {e}")
    except WebDriverException as e:
        logger.error(f"Ошибка WebDriver: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        logger.exception("Детали ошибки:")

    finally:
        # Корректное закрытие драйвера
        if driver is not None:
            try:
                logger.info("Закрытие WebDriver")
                driver.quit()
                logger.info("WebDriver успешно закрыт")
            except Exception as e:
                logger.warning(f"Ошибка при закрытии WebDriver: {e}")


if __name__ == "__main__":
    # Примеры использования:

    # Парсинг всех моделей
    scrape_toyota_frames()

    # Парсинг с определенного индекса (для возобновления)
    # scrape_toyota_frames(start_index=50)

    # Парсинг только первых 10 моделей для тестирования
    # scrape_toyota_frames(max_models=10, delay_between_requests=2)

    # Парсинг с 20-й модели, максимум 30 моделей
    # scrape_toyota_frames(start_index=20, max_models=30, delay_between_requests=5)
