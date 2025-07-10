import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def scrape_frames_for_models():
    """
    Парсит фреймы для каждой модели из файла toyota_jdm_models.json,
    добавляет их к данным модели и сохраняет в новый файл toyota_jdm_frames.json.
    """
    try:
        with open("toyota_jdm_models.json", "r") as f:
            data_to_update = json.load(f)
    except FileNotFoundError:
        print("Файл toyota_jdm_models.json не найден. Сначала запустите main.py")
        return

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

        for model in data_to_update.get("models", []):
            model_name = model.get("name")
            model_url = model.get("frame_name_url")

            if not model_url:
                model["frames"] = []
                continue

            print(f"Scraping frames for: {model_name}")
            driver.get(model_url)
            time.sleep(5)  # Ожидание загрузки

            # Поиск всех ссылок на фреймы
            frame_elements = driver.find_elements(By.CSS_SELECTOR, "ul.category2 h4 a")
            
            frames = []
            for el in frame_elements:
                frame_name = el.text.strip()
                frame_url = el.get_attribute("href")
                if frame_name and frame_url:
                    frames.append({"frame_name": frame_name, "url": frame_url})
            
            model["frames"] = frames
            print(f"  Found {len(frames)} frames.")

        # Сохранение обновленных данных в новый файл
        with open("toyota_jdm_frames.json", "w") as f:
            json.dump(data_to_update, f, indent=2, ensure_ascii=False)

        print("\nSuccessfully scraped and updated frames data into toyota_jdm_frames.json.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'cannot find Chrome binary' in str(e):
            print("Google Chrome не найден. Пожалуйста, установите Chrome и добавьте его в PATH.")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_frames_for_models()