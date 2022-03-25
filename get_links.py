import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
driver = webdriver.Chrome(service=Service("./src/chromedriver.exe"), options=chrome_options)
links = []
all_links = []

def getChildLinks(driver, url, list):
    if url not in all_links:
        try:
            driver.get(url)
        except:
            pass
        time.sleep(0.2)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        links = soup.find_all('a', {'class':'subcategory__item'})
        if len(links) > 0:
            for e in links:
                getChildLinks(driver, 'https://www.dns-shop.ru'+e['href'], list)
        else:
            print('%s added to list'%url)
            list.append(url)
    all_links.append(url)

driver.get('https://www.dns-shop.ru/catalog/')
soup = BeautifulSoup(driver.page_source, 'lxml')
for e in soup.find_all('div', {'class': ['subcategory__item', 'subcategory__item_with-childs']}):
    category = e.find('a', {'class': 'subcategory__childs-item'})['href']
    time.sleep(0.5)
    getChildLinks(driver, 'https://www.dns-shop.ru'+category, links)

with open('categories.txt', 'w') as f:
    for item in links:
        f.write("%s\n" % item)

driver.close()