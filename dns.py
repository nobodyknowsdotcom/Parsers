import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_prefs = {}
chrome_options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
driver = webdriver.Chrome(service=Service("./chromedriver.exe"), options=chrome_options)
driver.set_window_position(-2000, -2000)

REQUEST_INTERVAL = 1

links = []
items = []
total_pages = 0
with open("categories.txt") as file:
    for line in file: 
        line = line.strip()
        if ('recipe' not in line):
            links.append(line)

def getLastPage(content : BeautifulSoup):
    try:
        pagination = content.find_all('li', {'class': 'pagination-widget__page'})[-1]
        last_page = int(pagination['data-page-number'])
    except:
        last_page = 1
    return last_page

def parseCard(content : BeautifulSoup):
    try:
        raw_old_price = content.find('span', {'class':'product-buy__prev'}).get_text()
        old_price = re.sub("[^0-9]", "", raw_old_price)

        raw_discount_price = content.find('div', {'class':'product-buy__price'}).get_text()
        discount_price = re.sub("[^0-9]", "", raw_discount_price.split('₽')[0])
    except:
        raw_old_price = content.find('div', {'class':'product-buy__price'}).get_text()
        old_price = re.sub("[^0-9]", "", raw_old_price)
        discount_price = old_price

    name = content.find('a', {'class':'catalog-product__name'}).findChild('span', recursive=True).get_text()
    url = 'https://www.dns-shop.ru'+content.find('a', {'class':'catalog-product__name'})['href']
    return [name, old_price, discount_price, url]

def getCategories(content : BeautifulSoup):
    categoriesParent = content.find('ol', {'class':'breadcrumb-list'}).findChildren('span', recursive=True)
    categories = []
    for e in categoriesParent:
        categories.append(e.get_text())
    return categories

for link in links[:100]:
    try:
        driver.get(link)
    except:
        continue

    content = BeautifulSoup(driver.page_source, 'lxml')
    last_page = getLastPage(content)
    categories = getCategories(content)

    if (last_page == 1):
        soup = BeautifulSoup(driver.page_source, 'lxml')
        cards = soup.find_all('div', {'data-id':"product"})
        for e in cards:
            try:
                name, old_price, discount_price, url = parseCard(e)
            except AttributeError:
                continue
            print(categories, old_price, discount_price, sep="/---/")
            items.append([categories, name, old_price, discount_price, url])
        print(link, len(items), sep=':')
    else:
        for i in range(last_page):
            driver.get(link+'?p=%s'%str(i+1))
            time.sleep(REQUEST_INTERVAL)
            print('Getting page %s of %s'%(str(i+1), link))

            soup = BeautifulSoup(driver.page_source, 'lxml')
            cards = soup.find_all('div', {'data-id':'product'})

            for e in cards:
                try:
                    name, old_price, discount_price, url = parseCard(e)
                    category = categories[-1]
                except AttributeError:
                    continue
                print(name, old_price, discount_price, category, sep="\t") 

driver.close()