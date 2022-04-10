import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service("./chromedriver.exe"), options=options)
driver.set_window_size(600, 1000)
driver.set_window_position(-2000, -2000)

links = []
with open("mvideo_links.txt") as file:
    for line in file: 
        line = line.strip()
        links.append(line)

def getLastPage(soup: BeautifulSoup):
    buttons_container = soup.find('div',{'class':'bottom-controls'})
    lastPageElement = buttons_container.find_all('li', {'class':'ng-star-inserted'})[-1].findChild('a', recursive=True)
    return lastPageElement.get_text()

def getCards(soup: BeautifulSoup):
    return soup.findChildren('mvid-plp-product-card-mobile', recursive=True)

def is_aviable(card: BeautifulSoup):
    aviable = card.findChild('mvid-plp-notification-block', recursive=True).findChild('div', recursive=True).get_text()
    if aviable.strip() == 'Нет в наличии':
        return False
    else:
         return True

def parseCard(card: BeautifulSoup):
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

items = []
for link in links:
    postfix = '/f/skidka=da'
    driver.set_window_position(-2000, -2000)
    driver.get(link.split('?')[0]+postfix)
    driver.execute_script("document.body.style.zoom='15%'")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    lastPage = 1
    try:
        lastPage = int(getLastPage(soup))
    except (IndexError, AttributeError):
        print('Last page not found')
    print('Last page for %s is %s'%(link.split('?')[0]+postfix, lastPage))

    for i in range(lastPage):
        driver.delete_all_cookies()
        postfix = '/f/skidka=da?page=%s'%str(i+1)

        driver.get(link.split('?')[0]+postfix)
        driver.execute_script("document.body.style.zoom='12%'")
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(1.7)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        cards = getCards(soup)
        for card in cards:
            try:
                data = parseCard(card)
                items.append(data)
            except:
                pass
        
        try:
            if not is_aviable(cards[-1]): break
        except:
            pass
        print("Found %s cards, totally %s items"%(len(cards), len(items)))

with open('mvideo_items.txt', 'w', encoding='utf-8') as file:
    for e in items:
        file.write('%s\n'%e)

driver.close()

