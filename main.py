from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import time


# Функция для парсинга моделей Toyota с сайта
# https://toyota.epc-data.com/
def scrape_toyota_models():
    url = "https://toyota.epc-data.com/"

    try:
        # Настройка Chrome с автоматической установкой драйвера
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Запуск в фоновом режиме (без окна браузера)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = None  # Явно объявляем driver
        # Инициализация драйвера Chrome с помощью webdriver_manager
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

        # Открываем целевую страницу
        driver.get(url)
        time.sleep(10)  # Ждем загрузки страницы (можно уменьшить при стабильном интернете)

        # Сохраняем HTML-код страницы для отладки и анализа структуры
        with open("page.html", "w") as f:
            f.write(driver.page_source)

        # Селектор для поиска ссылок на модели автомобилей
        selectors = [
            "ul.category2 h4 a",
        ]

        models_data = []
        for selector in selectors:
            # Ищем элементы по CSS-селектору
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                # Формируем список моделей: имя и ссылка на фрейм
                models_data = [
                    {
                        "name": el.text.strip(),
                        "frame_name_url": el.get_attribute("href"),
                    }
                    for el in elements
                ]
                break  # Если нашли элементы, прекращаем перебор селекторов

        if not models_data:
            print("No models found. Check saved page.html for structure.")
            return

        # Сохраняем результат в JSON-файл
        with open("toyota_jdm_models.json", "w") as f:
            json.dump({"models": models_data}, f, indent=2)

        print(f"Successfully scraped {len(models_data)} models")

    except Exception as e:
        # Обработка ошибок
        print(f"An error occurred: {e}")
        if 'cannot find Chrome binary' in str(e):
            print("Google Chrome не найден. Пожалуйста, установите Chrome и добавьте его в PATH.")
    finally:
        # Корректное завершение работы драйвера
        if 'driver' in locals() and driver is not None:
            driver.quit()


# Точка входа: запуск парсера при запуске скрипта напрямую
if __name__ == "__main__":
    scrape_toyota_models()
