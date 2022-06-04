import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
driver = webdriver.Chrome(service=Service("./chromedriver.exe"), options=chrome_options)
driver.set_window_position(2000, 2000)
links = []
all_links = []

def getLinks(driver, url, list):
    if url not in all_links:
        try:
            driver.get(url)
        except:
            pass
        soup = BeautifulSoup(driver.page_source, 'lxml')
        links = soup.find_all('a', {'class':'subcategory__item'})
        if len(links) > 0:
            for e in links:
                getLinks(driver, 'https://www.dns-shop.ru'+e['href'], list)
        else:
            if 'recipe' in url:
                link = '/'.join(url.split('/')[:7])+'/'
                if not link in list:
                    list.append(link)
            else: 
                link = '/'.join(url.split('/')[:6])+'/'
                if not link in list:
                    list.append(link)      
            print(link)
    all_links.append(url)

driver.get('https://www.dns-shop.ru/catalog/')
soup = BeautifulSoup(driver.page_source, 'lxml')
for e in soup.find_all('div', {'class': ['subcategory__item', 'subcategory__item_with-childs']}):
    category = e.find('a', {'class': 'subcategory__childs-item'})['href']
    getLinks(driver, 'https://www.dns-shop.ru'+category, links)

with open('categories.txt', 'w') as f:
    for item in links:
        f.write("%s\n" % item)

driver.close()