import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
def dns_search_uc(query: str, limit: int = 5, timeout: int = 10):
    # Определяем пути к Chrome и ChromeDriver на Render
    STORAGE_DIR = "/opt/render/project/.render"
    CHROME_PATH = os.path.join(STORAGE_DIR, "chrome", "opt", "google", "chrome", "google-chrome")
    CHROMEDRIVER_PATH = os.path.join(STORAGE_DIR, "chromedriver", "chromedriver")
# Конфигурация опций Chrome
options = uc.ChromeOptions()
options.binary_location = CHROME_PATH  # Явно указываем путь к браузеру
options.add_argument("--headless=new")  # Используем новый headless-режим
options.add_argument("--no-sandbox")  # Обязательный аргумент для Linux-серверов
options.add_argument("--disable-dev-shm-usage")  # Решает проблемы с памятью
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1366,768")
options.add_argument(
    "--disable-blink-features=AutomationControlled")  # Маскировка автоматизации[citation:1][citation:6]
results = []
# Инициализируем драйвер с указанием пути
driver = uc.Chrome(
    options=options,
    driver_executable_path=CHROMEDRIVER_PATH,  # Указываем путь к chromedriver
    use_subprocess=True  # Важно для стабильной работы
)
try:
    driver.get(f"https://www.dns-shop.ru/search/?q={query}")
    # Явное ожидание загрузки хотя бы одного товара
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".catalog-product"))
    )
    time.sleep(1.5)  # Краткая пауза для завершения динамической подгрузки
    html = driver.page_source
except Exception as e:
    print(f"Ошибка при загрузке страницы: {e}")
    return results
finally:
    driver.quit()  # Закрываем драйвер
# Парсинг HTML с помощью BeautifulSoup
soup = BeautifulSoup(html, "lxml")
for card in soup.select(".catalog-product"):
    title_el = card.select_one("a.catalog-product__name")
    if not title_el:
        continue
    title = title_el.get_text(strip=True)
    href = title_el.get("href")
    url = "https://www.dns-shop.ru" + href if href and href.startswith(
        "/") else "https://www.dns-shop.ru" + href if href else "#"
    price_el = card.select_one(".product-buy__price")
    price = price_el.get_text(strip=True) if price_el else "Цена не указана"
    results.append((title, price, url))
    if len(results) >= limit:
        break
return results