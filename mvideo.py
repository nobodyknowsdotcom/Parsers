import random
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

USER_AGENTS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (X11; Linux i686; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (X11; Linux i686; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; WOW64; Trident/4.0;)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.0)',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.112',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.112',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.112',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.112',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Vivaldi/4.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Vivaldi/4.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Vivaldi/4.1',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Vivaldi/4.1',
    'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Vivaldi/4.1',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 YaBrowser/21.6.0 Yowser/2.5 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 YaBrowser/21.6.0 Yowser/2.5 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 YaBrowser/21.6.0 Yowser/2.5 Safari/537.36'
)

links = []
with open("mvideo_links.txt", mode='r', encoding='utf-8') as file:
    for line in file: 
        line = line.strip()
        links.append(line)

def getLastPage(soup: BeautifulSoup):
    buttons_container = soup.find('div',{'class':'bottom-controls'})
    lastPageElement = buttons_container.find_all('li', {'class':'ng-star-inserted'})[-1].findChild('a', recursive=True)
    return lastPageElement.get_text()

def getCards(soup: BeautifulSoup):
    return soup.findChildren('mvid-plp-product-card-mobile', recursive=True)

def onStock(card: BeautifulSoup):
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
lastPage = 1
for link in links:
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.set_window_size(600, 1000)

    postfix = '/f/skidka=da/tolko-v-nalichii=da?showCount=72'
    driver.get(link.split('?')[0]+postfix)
    driver.implicitly_wait(5) # seconds
    try:
        btn = WebDriverWait(driver, 10).until(
            lambda wd: wd.find_element(By.CSS_SELECTOR, '.count.ng-star-inserted'))
    except selenium.common.TimeoutException:
        continue
    driver.execute_script("document.body.style.zoom='15%'")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        lastPage = int(getLastPage(soup))
    except (IndexError, AttributeError):
        continue
    print('Last page for %s is %s'%(link.split('?')[0]+postfix, lastPage))

    for i in range(lastPage):
        driver.delete_all_cookies()
        postfix = '/f/skidka=da/tolko-v-nalichii=da?showCount=72?page=%s'%str(i+1)
        driver.get(link.split('?')[0]+postfix, )
        driver.execute_script("document.body.style.zoom='5%'")
        driver.implicitly_wait(5) # seconds
        try:
            btn = WebDriverWait(driver, 10).until(
            lambda wd: wd.find_element(By.CLASS_NAME, 'price__main-value'))
        except selenium.common.TimeoutException:
            continue
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = getCards(soup)
        for card in cards:
            try:
                name, price, discount_price, rating, feedbackCount, url, categories = parseCard(card)
                items.append([name, price, discount_price, rating, feedbackCount, url, categories])
            except:
                pass
        try:
            if not onStock(cards[-1]): break
        except:
            pass
        print("Found %s cards, totally %s items"%(len(cards), len(items)))
    driver.close()

with open('mvideo_items.txt', 'w', encoding='utf-8') as file:
    for e in items:
        file.write('%s\n'%e)

driver.close()

