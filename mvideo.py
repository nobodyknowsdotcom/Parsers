import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
driver = webdriver.Chrome(service=Service("./src/chromedriver.exe"), options=chrome_options)
driver.set_window_size(500, 800)

links = []
with open("mvideo_links.txt") as file:
    for line in file: 
        line = line.strip()
        links.append(line)

def getCards(soup: BeautifulSoup):
    return soup.findChildren('mvid-plp-product-card-mobile', recursive=True)

def getLastPage(soup: BeautifulSoup):
    buttons_container = soup.find('div',{'class':'bottom-controls'})
    lastPageElement = buttons_container.find_all('li', {'class':'ng-star-inserted'})[-2].findChild('a', recursive=True)
    return lastPageElement.get_text()

def parseCard(card: BeautifulSoup):
    name = card.find('a', {'class':'product-title__text'}).get_text()
    link = card.find('a', {'class':'product-title__text'})['href']
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
    return [name, price, discount_price, rating, feedbackCount, link]

items = []
for link in links:
    driver.delete_all_cookies()
    driver.get(link.split('?')[0]+'/f/skidka=da/tolko-v-nalichii=da')
    driver.execute_script("document.body.style.zoom='15%'")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    lastPage = 1
    try:
        lastPage = int(getLastPage(soup))
    except IndexError:
        print('IndexError')
    print('Last page for %s : %s'%(link, lastPage))

    for i in range(lastPage):
        driver.delete_all_cookies()
        driver.get(link.split('?')[0]+'/f/skidka=da/tolko-v-nalichii=da?page=%s'%str(i+1))
        driver.execute_script("document.body.style.zoom='5%'")
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        cards = getCards(soup)
        for card in cards:
            try:
                data = parseCard(card)
                print(data)
                items.append(data)
            except:
                pass
        print("Found %s cards, totally %s items"%(len(cards), len(items)))

with open('mvideo_items.txt', 'w', encoding='utf-8') as file:
    for e in items:
        file.write('%s\n'%e)

