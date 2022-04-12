import math
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup as bs
import csv

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--no-sandbox')
options.add_argument("--test-type")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--start-maximized")
options.add_argument("user-agent=Chrome/80.0.3987.132")
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", options=options)
action = webdriver.ActionChains(driver)

file = open('links.txt')
links = file.read().split('\n')
file.close

REQUEST_INTERVAL = 1
denied_list = []
items = []
errors = 0

def get_name(page):
    return page.find('h1', attrs={'class': ['gl-heading', 'gl-heading--regular']}).findChild("span" , recursive=False).get_text()

def get_links():
    driver.get('https://www.adidas.co.uk/search?start=0')
    time.sleep(5)
    driver.find_element_by_class_name('gl-modal__close').click()
    items_count = int(re.sub("[^0-9]", "", driver.find_element_by_class_name('count___1ZIhY').text))
    pages_count = math.ceil(items_count/48)
    print("items found: %d, pages found: %d" % (items_count, pages_count))

    elements = []
    denied_list = []
    for page_num in range(pages_count):
        try:
            driver.get("https://www.adidas.co.uk/search?start="+str(page_num*48))
            time.sleep(2.1)
            soup = bs(driver.page_source)
            cards = soup.find_all('div', {'class': 'plp-container-with-masking'})
            for e in cards:
                elements.append(e.findChild("a" , recursive=True)['href'])
            if (len(cards) == 0):
                denied_list.append("https://www.adidas.co.uk/search?start="+str(page_num*48))
                continue
            print('page %s: ok!' %page_num)
            print(len(elements))
        except:
            denied_list.append("https://www.adidas.co.uk/search?start="+str(page_num*48))

    for link in denied_list:
        try:
            driver.get(link)
            time.sleep(3)
            soup = bs(driver.page_source)
            cards = soup.find_all('div', {'class': 'plp-container-with-masking'})
            for e in cards:
                elements.append(e.findChild("a" , recursive=True)['href'])
            print('%s: ok!' %link)
            print(len(elements))
        except:
            pass

    with open('links.txt', 'w', encoding='utf-8') as f:
        for item in elements:
            f.write(str(item)+"\n")
    print('links.txt succesfully saved in script directory!')

def parse_page(driver, url, sleep_interval):
    driver.get(url)
    time.sleep(sleep_interval)
    soup = bs(driver.page_source)

    url = driver.current_url
    name = get_name(soup)
    old_price = re.sub("[^0-9]", "", soup.find('div', {'class':['gl-price', 'gl-price--horizontal']}).findChild('div', recursive=False).get_text())
    try:
        discount_price = re.sub("[^0-9]", "", soup.find('div', {'class':['gl-price', 'gl-price--horizontal']}).findChildren('div', recursive=False)[1].get_text())
    except (AttributeError, IndexError):
        discount_price = old_price
    category = soup.find_all('span', {'class':'path-item___2_uct'})[0].get_text()
    subcategory = soup.find_all('span', {'class':'path-item___2_uct'})[1].get_text()
    time.sleep(sleep_interval/4)
    try:
        description = soup.find('div', attrs={'class': 'text-content___1EWJO'}).findChild("p" , recursive=False).get_text()
    except (AttributeError, IndexError):
        description = ''
    images = []
    try:
        for e in soup.find('div', {'class':'views-scroll-container___2ZUHK'}).find_all('div', {'class':'view___CgbJj'}):
            images.append(e.findChild('img', recursive=True)['src'])
        images = list(set(images))
    except (AttributeError, IndexError, TypeError):
        images = soup.find('div', {'class':'content___26aLt'}).findChild('img', recursive=False)['src']
    aviable_sizes = []
    try:
        for e in soup.find('div', {'class':'size-selector___2htsB'}).findChildren('span', recursive=True):
            aviable_sizes.append(e.get_text())
    except (AttributeError, IndexError):
        pass
    about_model = []
    try:
        for e in soup.find('div', {'class':'bullets___NV9iB'}).findChildren('li', recursive=True):
            about_model.append(e.get_text())
    except:
        time.sleep(sleep_interval/2)
        for e in soup.find('div', {'class':'bullets___NV9iB'}).findChildren('li', recursive=True):
            about_model.append(e.get_text())
    shiping = ['Free delivery for members', 'Free delivery to our adidas Store']

    return [category, subcategory, name, url, old_price, discount_price, aviable_sizes, images, description, about_model, shiping]

time.sleep(5)

for link in links[:10]:
    try:
        category, subcategory, name, url, old_price, discount_price, aviable_sizes, image, description, about_model, shiping = parse_page(driver, url=link, sleep_interval=REQUEST_INTERVAL)
        if len(aviable_sizes) == 0 or len(description)==0 or aviable_sizes[0] == 'AAA':
            denied_list.append(link)
            errors +=1
            continue
        print('\033c', category, subcategory, name, url, old_price, discount_price, aviable_sizes, image, description, about_model, shiping,
        'Items parsed: ' + str(len(items)+1),sep='\n',)
        items.append([category, subcategory, name, url, old_price, discount_price, aviable_sizes, image, description, about_model, shiping])
    except:
        print("Invalid link!")
        denied_list.append(link)

print('Checking denied list (%s elements)'%len(denied_list))
for e in denied_list:
    try:
        category, subcategory, name, url, old_price, discount_price, aviable_sizes, image, description, about_model, shiping = parse_page(driver, url=link, sleep_interval=REQUEST_INTERVAL*1.5)
        if len(aviable_sizes)==0 or len(description)==0:
            continue
        print('\033c', category, subcategory, name, url, old_price, discount_price, aviable_sizes, image, description, about_model, shiping,
        'Items parsed: ' + str(len(items)+1),sep='\n')
        items.append([category, subcategory, name, url, old_price, discount_price, aviable_sizes, image, description, about_model, shiping])
    except:
        continue

with open('items_demo.csv', 'w', encoding='utf_8') as f:
    write = csv.writer(f)
    write.writerow(['category', 'subcategory', 'name', 'url', 'old_price', 'discount_price', 'aviable_sizes', 'image', 'description', 'about_model', 'shipping'])
    write.writerows(items)

driver.close()