import logging
from urllib.request import Request
import scrapy
import requests
import time
import json

from scrapy.crawler import CrawlerProcess
from seleniumwire import webdriver

BASE_URL = 'https://www.wildberries.ru'
CATALOG_URL = 'https://napi.wildberries.ru/api/menu/getburger?includeBrands=False'
link_1 = 'https://www.wildberries.ru/catalog/'
link_2 = '/detail.aspx?targetUrl=GP'

alert_list = []
denied_list = []
pages = []

option = webdriver.ChromeOptions()
chrome_prefs = {}
option.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
driver = webdriver.Chrome(chrome_options=option)
driver.set_window_position(2000, 2000)

logging.getLogger('scrapy').setLevel(logging.WARNING)
logging.getLogger('seleniumwire.server').setLevel(logging.WARNING)
logging.getLogger('seleniumwire.handler').setLevel(logging.WARNING)
logging.getLogger('scrapy.core.engine').setLevel(logging.WARNING)

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


class WbSpider(scrapy.Spider):
    name = 'test'
    items = 0

    def start_requests(self):
        
        for catalog in expand_catalog(get_request('https://napi.wildberries.ru/api/menu/getburger?includeBrands=False').json()['data']['catalog'][:-4]):
            driver.get(catalog[0] + '1&sort=popular&discount=30')
            time.sleep(8)
            # Access requests via the `requests` attribute
            content_url, count_url = self.get_urls(driver)
            print('content_url is: ', content_url)
            print('count_url is: ', count_url)

            pages = (int)(self.get_products_count(count_url)/100)
            if (pages >= 100):
                pages = 100
            print(pages)

            for i in range(pages):
                url = content_url+'&page=' + str(i+1)

                request = scrapy.Request(
                    url=url, 
                    callback=lambda r: self.parse_request(r, i)
                )

                yield request
        
        driver.close()

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

    def parse_request(self, request: requests.Request, page: int):
        content = self.convert_to_json(request)

        try:
            for e in content['data']['products']:
                product = self.get_product(e)
                self.items += 1
                
            print(str(page), str(self.items), sep=' ')
        except json.decoder.JSONDecodeError:
            print("Cant get " + request.url)

    def get_products_count(self, url: str) -> int:
        count_r = requests.get(url)
        count = json.loads(count_r.text)['data']['total']
        return count

    def convert_to_json(self, response: requests.Response):
        content = json.loads(response.text)
        return content

    def get_product(self, json: str):
        name = json['name']
        brand = json['brand']
        price = (int) (json['priceU'] / 100)
        discount_price = (int) (json['salePriceU'] / 100)
        sale = json['sale']
        link = link_1 + str(json['id']) + link_2
        return [name, brand, price, discount_price, sale, link]


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(WbSpider)
    process.start()
