import json
import time
import requests
from time import sleep

from seleniumwire import webdriver

link_1 = 'https://www.wildberries.ru/catalog/'
link_2 = '/detail.aspx?targetUrl=GP'

def get_urls(driver: webdriver.Chrome):
    content_url = ''
    count_url = ''

    for request in driver.requests:
        if request.response:
            if '/v4/filters?appType=1&couponsGeo=' in request.url:
                count_url = request.url
                print('count url is\n' + request.url)
            if '/catalog?appType=1&couponsGeo=' in request.url:
                print('main url is\n' + request.url)
                content_url = request.url
    
    return [content_url, count_url]

def get_products_count(url: str) -> int:
    count_r = requests.get(url)
    count_r.encoding = 'utf-8'
    count = json.loads(count_r.text)['data']['total']
    return count

def get_content(url: str):
    r = requests.get(url)
    r.encoding = 'utf-8'
    content = json.loads(r.text)
    return content

def get_product(json: str):
    name = json['name']
    brand = json['brand']
    price = (int) (json['priceU'] / 100)
    discount_price = (int) (json['salePriceU'] / 100)
    sale = json['sale']
    link = link_1 + str(json['id']) + link_2
    return [name, brand, price, discount_price, sale, link]

driver = webdriver.Chrome()
driver.set_window_position(2000, 2000)
driver.get('https://www.wildberries.ru/catalog/zhenshchinam/odezhda/bluzki-i-rubashki?sort=popular&discount=30')


# Access requests via the `requests` attribute
time.sleep(8)
content_url, count_url = get_urls(driver)
    
driver.close()

pages = (int)(get_products_count(count_url)/100)
if (pages >= 999):
    pages = 999
print(pages)

for i in range(pages):
    url = content_url+'&page=' + str(i+1)
    try:
        content = get_content(url)
    except json.decoder.JSONDecodeError:
        print("Cant get " + url)
    for e in content['data']['products']:
        product = get_product(e)
        print(i, *product, sep=' ')