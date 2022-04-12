import os
import numpy as np
from pandas import read_csv
import pandas as pd
import scrapy
import requests

from bs4 import BeautifulSoup
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
from requests import ConnectTimeout

links = []
items = []

def get_link(card):
    try:
        link = 'https://www.yoox.com'+card.find('a')['href']
    except:
        link = ''
    return link

class WbSpider(scrapy.Spider):
    name = 'get_descriptions'
    
    def start_requests(self):
        links = read_csv("descriptions.csv")['link'].tolist()
        for link in links:
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_card(r),
                    dont_filter=True)
                yield request
            except:
                print('Item out of stock!')

        df = pd.DataFrame (items, columns = ['id', 'description', 'composition'])
        df.to_csv('descriptions.csv', index=False)
        old = pd.read_csv("descriptions.csv")
        old.drop(['description', 'composition'], axis=1, inplace=True)
        merged['discount_price'].replace('0', np.nan, inplace=True)
        merged['details'].replace('0', np.nan, inplace=True)
        merged.dropna(subset=['discount_price'], inplace=True)
        merged = old.merge(pd.read_csv("descriptions.csv"), left_on="id", right_on="id", how="outer")
        os.remove('descriptions.csv')
        merged.to_csv('descriptions.csv', index=False, encoding='utf-8')
        
    def parse_page(self, response):
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            cards = soup.find_all('div', {'class':'itemContainer'})
            for card in cards:
                link = get_link(card)
                if (link != ''):
                    links.append([link])
            print('\nLinks:', len(links))
        except:
            print('An exception occured!')

    def parse_card(self, response):
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            description = soup.find('div', {'class':'Details_block2__y_uOf'}).find('span', {'class':['MuiBody1-body1','MuiBody1-wide']}).get_text()
            composition = soup.find('div', {'class':'Details_block1__Ru66n'}).find('span', {'class':['MuiBody1-body1','MuiBody1-wide']}).get_text()
            prod_code = soup.find('div', {'class':'Details_code10__1V6sY'}).find('span', {'class':['MuiBody1-body2','MuiBody2-wide']}).get_text().split('Product code: ')[1]
            items.append([prod_code, description, composition])
        except:
            print('An exception occured!')
    
    def get_pages_count(self, url):
        splitted_url = url.split('page=')
        request = requests.get(splitted_url[0]+'0'+splitted_url[1],
            headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'})
        soup = BeautifulSoup(request.content, 'html.parser')
        try:
            return soup.find('ul', {'id':'js-expanded-pagination-lite'}).findChildren('li', recursive=True)[-1].get_text()
        except:
            return 1

    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        
        if failure.check(TimeoutError):
            response = failure.value.response
            self.logger.error('TimeoutError on %s', response.url)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
        
        elif failure.check(ConnectTimeout):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
