from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import time


def scrape_toyota_models():
    url = "https://toyota.epc-data.com/"

    try:
        # Настройка Chrome с автоматической установкой драйвера
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Запуск в фоновом режиме
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

        driver.get(url)
        time.sleep(10)  # Увеличиваем время ожидания

        # Сохраняем HTML для анализа
        with open("page.html", "w") as f:
            f.write(driver.page_source)

        # Селектор для моделей и ссылок
        selectors = [
            "ul.category2 h4 a",
        ]

        models_data = []
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                models_data = [
                    {
                        "name": el.text.strip(),
                        "frame_name_url": el.get_attribute("href"),
                    }
                    for el in elements
                ]
                break

        if not models_data:
            print("No models found. Check saved page.html for structure.")
            return

        with open("toyota_jdm_models.json", "w") as f:
            json.dump({"models": models_data}, f, indent=2)

        print(f"Successfully scraped {len(models_data)} models")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_toyota_models()
