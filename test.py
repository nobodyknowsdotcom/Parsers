import pickle
import json
import time
import requests
from time import sleep

from urllib.parse import urlparse
from urllib.parse import parse_qs

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

def expand_catalog(full_catalog):
    result = {}

    for category in full_catalog:

        try:
            if category['childs']:
                result.update(expand_catalog(category['childs']))
            else:
                result[category['query']] = category['seo']
        except KeyError:
            try:
                result[category['query']] =  category['seo']
            except KeyError:
                pass
    return result

def get_querry(url: str):
    parsed_url = urlparse(content_url)
    kind = parse_qs(parsed_url.query)['kind']
    subject = parse_qs(parsed_url.query)['subject']
    ext = ''
    try:
        ext = parse_qs(parsed_url.query)['ext']
    except KeyError:
        pass

    if ('=' in ext):
        category_query = 'kind='+''.join(kind)+'&subject='+''.join(subject)+'&ext='+str(ext)
    else:
        category_query = 'kind='+''.join(kind)+'&subject='+''.join(subject)
    return(category_query)

driver = webdriver.Chrome()
driver.set_window_position(2000, 2000)
driver.get('https://www.wildberries.ru/catalog/zhenshchinam/odezhda/bluzki-i-rubashki?sort=popular&discount=30')

r = requests.get('https://www.wildberries.ru/webapi/menu/main-menu-ru-ru.json')

# Access requests via the `requests` attribute
time.sleep(8)
content_url, count_url = get_urls(driver)
with open('categories_dictionary.pkl', 'rb') as f:
    category_dict = pickle.load(f)
category_query = get_querry(content_url)

try:
    category = category_dict[category_query]
    print(len(category_dict))
except:
    pass

driver.close()
exit()

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