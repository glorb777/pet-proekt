import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

BASE_URLS = [
    # 1 дорогие
    "https://www.mvideo.ru/smartfony-i-svyaz-10/smartfony-205/f/tolko-v-nalichii=da?sort=price_desc",
    # 2 дешевые
    "https://www.mvideo.ru/smartfony-i-svyaz-10/smartfony-205/f/tolko-v-nalichii=da?sort=price_asc",
    # 3 популярные
    "https://www.mvideo.ru/smartfony-i-svyaz-10/smartfony-205/f/tolko-v-nalichii=da"
]

pages = 5

def setup_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver

def slow_scroll(driver):
    total_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    step = 400  # Размер шага прокрутки в пикселях 
    
    while current_position < total_height:
        current_position += step
        # Скроллим на новую позицию
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        
        # Ждем подгрузку контента
        time.sleep(0.3) 
        
        # Обновляем высоту
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height > total_height:
            total_height = new_height

def parse_card(soup_card):
    data = {}
    try:
        title_el = soup_card.find('a', class_='product-title__text')
        if not title_el: return None
        
        full_name = title_el.text.strip()
        data['Название модели'] = full_name
        data['Ссылка'] = 'https://www.mvideo.ru' + title_el['href']
        
        parts = full_name.split()
        data['Производитель'] = parts[1] if len(parts) > 1 else 'Unknown'

        # 2. Цена
        price_el = soup_card.find('span', class_='price__main-value')
        if price_el:
            raw_price = re.sub(r'[^\d]', '', price_el.text)
            data['Цена'] = int(raw_price) if raw_price else 0
        else:
            data['Цена'] = 0

        # Старая цена
        old_price_el = soup_card.find('span', class_='price__sale-value')
        if old_price_el:
            raw_old = re.sub(r'[^\d]', '', old_price_el.text)
            data['Старая цена'] = int(raw_old) if raw_old else 0
        else:
            data['Старая цена'] = 0
            
        # 3. Характеристики
        features = soup_card.find_all('li', class_='product-feature-list__item')
        
        # Дефолтные значения
        data['RAM'] = 0
        data['ROM'] = 0
        data['Экран'] = 0.0
        data['Камера'] = 0
        
        for feat in features:
            name = feat.find('span', class_='product-feature-list__name').text.lower()
            value_el = feat.find('span', class_='product-feature-list__value')
            if not value_el: continue
            value = value_el.text
            
            if 'память' in name:
                match = re.search(r'(\d+).*?(\d+)', value)
                if match:
                    data['RAM (ГБ)'] = int(match.group(1))
                    data['ROM (ГБ)'] = int(match.group(2))
            elif 'экран' in name:
                match = re.search(r'(\d+\.?\d*)', value)
                if match:
                    data['Экран (дюйм)'] = float(match.group(1))
            elif 'основная камера' in name:
                match = re.search(r'(\d+)', value)
                if match:
                    data['Камера (МП)'] = int(match.group(1))

    except Exception:
        return None
    return data

def main():
    driver = setup_driver()
    all_products = []

    try:
        # Итерируемся по списку
        for current_url in BASE_URLS:
            
            # Итерируемся по страницам
            for page in range(1, pages + 1):
                url = f"{current_url}&page={page}"
                driver.get(url)
                time.sleep(3)
                    
                # Скроллим
                slow_scroll(driver)
                time.sleep(2)
                    
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                cards = soup.find_all('div', class_='product-cards-layout__item')
                valid_count = 0
                for card in cards:
                    if card.find('mvid-skeleton-gradient-container'): continue
                        
                    product_data = parse_card(card)
                    if product_data and product_data['Цена'] > 0:
                        all_products.append(product_data)
                        valid_count += 1
            time.sleep(5) 
    finally:
        driver.quit()
        
if __name__ == "__main__":
    main()