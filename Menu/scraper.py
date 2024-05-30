import requests
import bs4
import fitz  # PyMuPDF
import re
import json
import sqlite3
from urllib.parse import urljoin

# URLs of the restaurants
urls = {
    'Mezepoli': 'https://mezepoli.co.za',
    'Ciccio': 'https://ciccio.co.za',
    'The Big Mouth': 'https://www.thebigmouth.co.za',
    'Ukko': 'https://ukkorestaurant.co.za'
}

# Database setup
def init_db():
    conn = sqlite3.connect('menus.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menus (
            id INTEGER PRIMARY KEY,
            restaurant TEXT,
            item_type TEXT,
            item TEXT,
            price TEXT,
            UNIQUE(restaurant, item, price)
        )
    ''')
    conn.commit()
    conn.close()

def insert_menu_item(restaurant, item_type, item, price):
    conn = sqlite3.connect('menus.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO menus (restaurant, item_type, item, price)
        VALUES (?, ?, ?, ?)
    ''', (restaurant, item_type, item, price))
    conn.commit()
    conn.close()

def extract_menu_data(url, restaurant_name):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    menu_items = []

    for ul in soup.find_all(['ul', 'div', 'span'], class_=['menu', 'menu-items', 'menu-item', 'menu-section']):
        menu_items.extend(extract_items_with_regex(ul.get_text(), restaurant_name))

    pdf_links = soup.find_all('a', href=True)
    for link in pdf_links:
        href = link['href']
        if href.lower().endswith('.pdf'):
            full_url = urljoin(url, href)
            pdf_menu_items = extract_pdf_menu(full_url, restaurant_name)
            if pdf_menu_items:
                menu_items.extend(pdf_menu_items)

    return menu_items

def extract_pdf_menu(pdf_url, restaurant_name):
    menu_items = []
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()

        pdf_document = fitz.open(stream=response.content, filetype="pdf")
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            menu_items.extend(extract_items_with_regex(text, restaurant_name))
    except requests.RequestException as e:
        print(f"Error fetching PDF {pdf_url}: {e}")
    except Exception as e:
        print(f"Error reading PDF {pdf_url}: {e}")

    return menu_items

def extract_items_with_regex(text, restaurant_name):
    menu_items = []
    pattern = re.compile(r'(?P<item>[A-Za-z\s&\-,]+)[\s:\-]*(?P<price>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)')
    for match in pattern.finditer(text):
        item = match.group('item').strip()
        price = match.group('price').strip()
        if 'dessert' in item.lower() or 'salad' in item.lower() or 'wine' in item.lower():
            item_type = 'dessert' if 'dessert' in item.lower() else 'salad' if 'salad' in item.lower() else 'wine'
            menu_items.append({
                'restaurant': restaurant_name,
                'type': item_type,
                'item': item,
                'price': price
            })
            insert_menu_item(restaurant_name, item_type, item, price)
    return menu_items

def scrape_all_menus():
    init_db()
    for restaurant_name, url in urls.items():
        print(f"Processing {url}")
        menu_items = extract_menu_data(url, restaurant_name)
        if menu_items:
            print(f"Menu items found for {restaurant_name}")
        else:
            print(f"No menu items found for {restaurant_name}")

if __name__ == '__main__':
    scrape_all_menus()

