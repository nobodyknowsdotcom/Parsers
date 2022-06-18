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

    def start_requests(self):

        for catalog in expand_catalog(get_request('https://napi.wildberries.ru/api/menu/getburger?includeBrands=False').json()['data']['catalog'][:-4]):
            r = get_request(catalog[0] + '1')
            soup = BeautifulSoup(r.content)
            try:
                products_count = ''.join(filter(lambda i: i.isdigit(),soup.find('span', {'class':'goods-count'}).findChildren('span', recursive=False)[2].text))
            except AttributeError:
                denied_list.append(catalog[0] + '1')
                continue

            pages_count = int(int((products_count)) / 100)
            if (pages_count >= 999):
                print('Original pages count: %s, trimmed to %s due to unavailability' % (pages_count, 999))
                pages_count = 999
            print("Pages: ", pages_count)

            for page_id in range(1, pages_count + 1):
                request = scrapy.Request(
                    url=catalog[0] + str(page_id) + '&sort=popular&discount=20', 
                    callback=lambda r: self.parse_page(r, catalog[1]))
                yield request

    def parse_page(self, response, category_title):
        for product_card in response.css('div.product-card__wrapper'):
            name = product_card.css('span.goods-name::text').extract_first().strip()
            product_link = BASE_URL + product_card.css('a::attr(href)').extract_first()
            price = product_card.css('.lower-price::text').extract_first().strip()
            old_price = product_card.css('.price-old-block del::text').extract_first()

            if not old_price:
                old_price = price
                
            sale = product_card.css('span.product-card__sale::text').extract_first()
            if not sale:
                sale = '-0%'
            
            print(name, price)
        pages.append('something')
        print(category_title, response.url.split('?')[1].split('&')[0], "pages crawled:", len(pages))


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(WbSpider)
    process.start()
