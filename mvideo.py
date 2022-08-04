import math
import random
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# Количество показываемых товаров на странице - 16/32/48/72
SHOW_COUNT = 72
# Настройка ChromeDriver'а
options = Options()
options.add_argument("--disable-gpu")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

items = []
requests_count = 0

def read_links():
    result = []
    with open("mvideo_links.txt", mode='r', encoding='utf-8') as file:
        for line in file: 
            line = line.strip()
            result.append(line)

def get_last_page(soup: BeautifulSoup) -> str:
    buttons_container = soup.find('div',{'class':'bottom-controls'})
    lastPageElement = buttons_container.find_all('li', {'class':'ng-star-inserted'})[-1].findChild('a', recursive=True)
    return lastPageElement.get_text()

def get_cards(soup: BeautifulSoup) -> BeautifulSoup:
    return soup.findChildren('mvid-plp-product-card-mobile', recursive=True)

def is_on_stock(card: BeautifulSoup) -> bool:
    aviable = card.findChild('mvid-plp-notification-block', recursive=True).findChild('div', recursive=True).get_text()
    if aviable.strip() == 'Нет в наличии':
        return False
    else:
         return True

def parse_card(card: BeautifulSoup) -> [str, ]:
    name = card.find('a', {'class':'product-title__text'}).get_text()
    link = card.find('a', {'class':'product-title__text'})['href']
    categories = []
    for e in soup.find('ul', {'itemtype':'http://schema.org/BreadcrumbList'}).findChildren('span', recursive=True)[1:]:
        categories.append(e.get_text())
    try:
        rating = card.find('mvid-plp-product-rating', {'class':'ng-star-inserted'}).findChild('span', recursive=True).get_text()
    except:
        rating = 0
    try:
        feedbackCount = card.find('span', {'class':'product-rating__feedback'}).get_text()
    except:
        feedbackCount = 0
    try:
        priceBlock = card.find('div', {'class':'price-block'})
        prices = priceBlock.find('div', {'class':['price', 'price--mobile', 'ng-star-inserted']}).findChildren('span', recursive=False)
        discount_price = re.sub("[^0-9]", "", prices[0].get_text())
        price = re.sub("[^0-9]", "", prices[1].get_text())
    except:
        price = discount_price
    return [name, price, discount_price, rating, feedbackCount, link, categories]

links = read_links()
for link in links:
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.set_window_size(600, 1000)
    driver.set_window_position(2000, 2000)

    try: 
        postfix = '/f/skidka=da/tolko-v-nalichii=da?showCount=%s' % SHOW_COUNT
        driver.get(link.split('?')[0]+postfix)
    except selenium.common.exceptions.WebDriverException: 
        pass

    driver.implicitly_wait(5)
    try:
        btn = WebDriverWait(driver, 10).until(
            lambda wd: wd.find_element(By.CSS_SELECTOR, '.count.ng-star-inserted'))
    except selenium.common.TimeoutException:
        print('Products count not found!')
        continue
    driver.execute_script("document.body.style.zoom='15%'")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products_count = soup.select_one('.count.ng-star-inserted').get_text()
        lastPage = math.ceil(int(products_count) / SHOW_COUNT)
    except (IndexError, AttributeError):
        print('Products count not found!')
        continue

    print('Last page for %s is %s'%(link.split('?')[0]+postfix, lastPage))

    for i in range(lastPage):
        try:
            postfix = '/f/skidka=da/tolko-v-nalichii=da?showCount=%s?page=%s' % (SHOW_COUNT, str(i+1))
            driver.get(link.split('?')[0]+postfix)
        except selenium.common.TimeoutException:
            print('Error processing %s' % link.split('?')[0]+postfix)
            continue
        driver.execute_script("document.body.style.zoom='5%'")

        driver.implicitly_wait(5)
        try:
            btn = WebDriverWait(driver, 10).until(
            lambda wd: wd.find_element(By.CLASS_NAME, 'price__main-value'))
        except selenium.common.TimeoutException:
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = get_cards(soup)
        for card in cards:
            try:
                name, price, discount_price, rating, feedbackCount, url, categories = parse_card(card)
                items.append([name, price, discount_price, rating, feedbackCount, url, categories])
            except:
                print('Card processing error')
        try:
            if not is_on_stock(cards[-1]): break
        except:
            pass
        requests_count += 1
        print("Found %s cards, totally %s items"%(len(cards), len(items)))
    driver.close()

try:
    driver.close()
except:
    pass

