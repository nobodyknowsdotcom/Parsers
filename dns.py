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

for link in links[:200]:
    driver.get(link)
    last_page = getLastPage(driver)
    
    print(last_page)
    for i in range(last_page):
        driver.get(link+'?p=%s'%str(i+1))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        cards = soup.find_all('a', {'class':'catalog-product__name'})
        for e in cards:
            item = e.findChild('span', recursive=True).get_text()
            items.append(item)
            print(item)

with open('items.txt', 'w') as f:
    for item in items:
        f.write("%s\n" % item)

driver.close()