from dis import dis
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
driver = webdriver.Chrome(service=Service("./src/chromedriver.exe"), options=chrome_options)

links = []
items = []
with open("categories.txt") as file:
    for line in file: 
        line = line.strip()
        links.append(line)

def getLastPage(driver):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    try:
        pagination = soup.find_all('li', {'class': 'pagination-widget__page'})[-1]
        last_page = int(pagination['data-page-number'])
    except:
        last_page = 1
    return last_page

def parseCard(content):
    try:
        old_price = content.find('div', {'class':'catalog-product__price-old'}).get_text()
        discount_price = content.find('div', {'class':'catalog-product__price-actual'}).get_text()
    except:
        old_price = content.find('div', {'class':'product-buy__price'}).get_text()
        discount_price = old_price
    name = content.find('a', {'class':'catalog-product__name'}).findChild('span', recursive=True).get_text()
    url = content.find('a', {'class':'catalog-product__name'})['href']
    return [name, old_price, discount_price, url]

for link in links[:10]:
    driver.get(link)
    last_page = getLastPage(driver)
    print(last_page)
    
    if last_page == 1:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        cards = soup.find_all('div', {'class':['catalog-product', 'ui-button-widget']})
        for e in cards:
            data = parseCard(e)
            items.append(data)
            print(*data, sep='\t')
            continue

    
    for i in range(last_page):
        driver.get(link+'?p=%s'%str(i+1))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        cards = soup.find_all('div', {'class':'catalog-product'})
        for e in cards:
            data = parseCard(e)
            items.append(data)
            print(*data, sep='\t')

with open('items.txt', 'w', encoding='utf-8') as f:
    for item in items:
        f.write("%s\n" % item)

driver.close()