import json
import time
from urllib.request import Request
import requests
from time import sleep

from seleniumwire import webdriver

driver = webdriver.Chrome()
driver.set_window_position(2000, 2000)
driver.get('https://www.wildberries.ru/catalog/zhenshchinam/odezhda/bluzki-i-rubashki?sort=popular&page=1&discount=30')

time.sleep(2)

# Access requests via the `requests` attribute
url = ''
for request in driver.requests:
    if request.response:
        if '/catalog?' in request.url:
            url = request.url
            print(request.url)

driver.close()

r = requests.get(url)
r.encoding = 'utf-8'
deserialized = json.loads(r.text)

for e in deserialized['data']['products']:
    name = e['name']
    brand = e['brand']
    price = (int) (e['priceU'] / 100)
    discount_price = (int) (e['salePriceU'] / 100)
    print(name, brand, price, discount_price, sep=' ')