import scrapy
import requests
import time

from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess

BASE_URL = 'https://www.wildberries.ru'
CATALOG_URL = 'https://napi.wildberries.ru/api/menu/getburger?includeBrands=False'

alert_list = []
denied_list = []
pages = []

def expand_catalog(full_catalog, prefix=''):
    result = []
    for category in full_catalog:
        new_prefix = prefix + '/' + category['name'] if prefix else category['name']

        if category['childNodes']:
            result.extend(expand_catalog(category['childNodes'], new_prefix))
        else:
            if category['pageUrl'].startswith('/api/'):
                category_url = BASE_URL + category['pageUrl'][4:] + '?page='
                result.append((category_url, new_prefix))
            else:
                alert_list.append(category['pageUrl'])
    return result

def get_request(url):
    while True:
        request = requests.get(url)
        if request.status_code == 200:
            return request
        elif request.status_code in (401, 404):
            denied_list.append(url)
            return None
        else:
            time.sleep(2)

cats = expand_catalog(get_request('https://napi.wildberries.ru/api/menu/getburger?includeBrands=False').json()['data']['catalog'][:-4])[1003]
print(cats)