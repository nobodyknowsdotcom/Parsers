import os
import numpy as np
import pandas as pd
import scrapy
import requests

from bs4 import BeautifulSoup
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
from requests import ConnectTimeout

items = []

def parse_card(card: BeautifulSoup):
        id = card['id'].split('item_')[1]
        try:
            size = []
            for e in card.find_all('span', {'class':'aSize'}):
                size.append(e.get_text().strip())
        except:
            size = 'no size'
        try:
            price = card.find('span', {'class':'fullprice'}).get_text().strip()
            discount_price = price
            discount = 0
        except:
            try:
                price = card.find('span', {'class':'oldprice'}).get_text().strip()
                discount_price = card.find('div', {'class':'retail-newprice'}).get_text().strip()
                discount = card.find('span', {'class':'element'}).get_text().strip()
            except:
                price = 0
                discount_price = 0
                discount = 0
        return [id, size, price, discount_price, discount]

class WbSpider(scrapy.Spider):
    name = 'yoox_demo'

    def start_requests(self): 
        # womens
        url = 'https://www.yoox.com/uk/women/shoponline/#/dept=women&gender=D&page=1&season=X'
        page = requests.get(url,
            headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'})
        soup = BeautifulSoup(page.text, 'lxml')
        for e in soup.find('div', {'id': 'teleyooxCategories'}).find_all('a', {'data-tracking-label':'ctgr - choose micro'})[:5]:
            raw_url = ('https://www.yoox.com'+e['href']).split('page=1')
            link = raw_url[0].split('#/')[0]+'/'+str(1)+'#/'+raw_url[0].split('#/')[1]+'page='+str(1)+raw_url[1]
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_page(r),
                    errback=self.errback_httpbin,
                    dont_filter=True)
                yield request
            except:
                pass
        # mens
        url = 'https://www.yoox.com/uk/men/shoponline#/dept=men&gender=U&page=1&season=X'
        page = requests.get(url,
            headers={'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'})
        soup = BeautifulSoup(page.text, 'lxml')
        for e in soup.find('div', {'id': 'teleyooxCategories'}).find_all('a', {'data-tracking-label':'ctgr - choose micro'})[:5]:
            raw_url = ('https://www.yoox.com'+e['href']).split('page=1')
            link = raw_url[0].split('#/')[0]+'/'+str(1)+'#/'+raw_url[0].split('#/')[1]+'page='+str(1)+raw_url[1]
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_page(r),
                    errback=self.errback_httpbin,
                    dont_filter=True)
                yield request
            except:
                pass
        # designart
        url = 'https://www.yoox.com/uk/design+art/shoponline#/dept=designart&page=1&season=X'
        page = requests.get(url,
            headers={'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'})
        soup = BeautifulSoup(page.text, 'lxml')
        for e in soup.find('div', {'id': 'teleyooxCategories'}).find_all('a', {'data-tracking-label':'ctgr - choose micro'})[:5]:
            raw_url = ('https://www.yoox.com'+e['href']).split('page=1')
            link = raw_url[0].split('#/')[0]+'/'+str(1)+'#/'+raw_url[0].split('#/')[1]+'page='+str(1)+raw_url[1]
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_page(r),
                    errback=self.errback_httpbin,
                    dont_filter=True)
                yield request
            except:
                pass
        # kids
        url = 'https://www.yoox.com/uk/girl/main%20collection/baby/shoponline#/dept=collgirl_baby&gender=D&page=1&season=X'
        page = requests.get(url,
            headers={'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'})
        soup = BeautifulSoup(page.text, 'lxml')
        for e in soup.find('div', {'id': 'teleyooxCategories'}).find_all('a', {'data-tracking-label':'ctgr - choose micro'})[:5]:
            raw_url = ('https://www.yoox.com'+e['href']).split('page=1')
            link = raw_url[0].split('#/')[0]+'/'+str(1)+'#/'+raw_url[0].split('#/')[1]+'page='+str(1)+raw_url[1]
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_page(r),
                    errback=self.errback_httpbin,
                    dont_filter=True)
                yield request
            except:
                pass
        url = 'https://www.yoox.com/uk/boy/main%20collection/baby/shoponline#/dept=collboy_baby&gender=U&page=1&season=X'
        page = requests.get(url,
            headers={'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'})
        soup = BeautifulSoup(page.text, 'lxml')
        for e in soup.find('div', {'id': 'teleyooxCategories'}).find_all('a', {'data-tracking-label':'ctgr - choose micro'})[:5]:
            raw_url = ('https://www.yoox.com'+e['href']).split('page=1')
            link = raw_url[0].split('#/')[0]+'/'+str(1)+'#/'+raw_url[0].split('#/')[1]+'page='+str(1)+raw_url[1]
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_page(r),
                    errback=self.errback_httpbin,
                    dont_filter=True)
                yield request
            except:
                pass
        url = 'https://www.yoox.com/uk/boy/main%20collection/kids/shoponline#/dept=collboy_kid&gender=U&page=1&season=X'
        page = requests.get(url,
            headers={'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'})
        soup = BeautifulSoup(page.text, 'lxml')
        for e in soup.find('div', {'id': 'teleyooxCategories'}).find_all('a', {'data-tracking-label':'ctgr - choose micro'})[:5]:
            raw_url = ('https://www.yoox.com'+e['href']).split('page=1')
            link = raw_url[0].split('#/')[0]+'/'+str(1)+'#/'+raw_url[0].split('#/')[1]+'page='+str(1)+raw_url[1]
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_page(r),
                    errback=self.errback_httpbin,
                    dont_filter=True)
                yield request
            except:
                pass
        url = 'https://www.yoox.com/uk/girl/main%20collection/kids/shoponline#/dept=collgirl_kid&gender=D&page=1&season=X'
        page = requests.get(url,
            headers={'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'})
        soup = BeautifulSoup(page.text, 'lxml')
        for e in soup.find('div', {'id': 'teleyooxCategories'}).find_all('a', {'data-tracking-label':'ctgr - choose micro'})[:5]:
            raw_url = ('https://www.yoox.com'+e['href']).split('page=1')
            link = raw_url[0].split('#/')[0]+'/'+str(1)+'#/'+raw_url[0].split('#/')[1]+'page='+str(1)+raw_url[1]
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_page(r),
                    errback=self.errback_httpbin,
                    dont_filter=True)
                yield request
            except:
                pass
        url = 'https://www.yoox.com/uk/boy/main%20collection/junior/shoponline#/dept=collboy_junior&gender=U&page=1&season=X'
        page = requests.get(url,
            headers={'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'})
        soup = BeautifulSoup(page.text, 'lxml')
        for e in soup.find('div', {'id': 'teleyooxCategories'}).find_all('a', {'data-tracking-label':'ctgr - choose micro'})[:5]:
            raw_url = ('https://www.yoox.com'+e['href']).split('page=1')
            link = raw_url[0].split('#/')[0]+'/'+str(1)+'#/'+raw_url[0].split('#/')[1]+'page='+str(1)+raw_url[1]
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_page(r),
                    errback=self.errback_httpbin,
                    dont_filter=True)
                yield request
            except:
                pass
        url = 'https://www.yoox.com/uk/girl/main%20collection/junior/shoponline#/dept=collgirl_junior&gender=D&page=1&season=X'
        page = requests.get(url,
            headers={'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'})
        soup = BeautifulSoup(page.text, 'lxml')
        for e in soup.find('div', {'id': 'teleyooxCategories'}).find_all('a', {'data-tracking-label':'ctgr - choose micro'})[:5]:
            raw_url = ('https://www.yoox.com'+e['href']).split('page=1')
            link = raw_url[0].split('#/')[0]+'/'+str(1)+'#/'+raw_url[0].split('#/')[1]+'page='+str(1)+raw_url[1]
            try:
                request = scrapy.Request(
                    url = link, 
                    callback=lambda r: self.parse_page(r),
                    errback=self.errback_httpbin,
                    dont_filter=True)
                yield request
            except:
                pass

        combined_csv = pd.DataFrame(items, columns = ['id', 'size', 'price', 'discount_price', 'discount'])
        combined_csv.to_csv('proxy_demo.csv', index=False)
        combined_csv = pd.read_csv('proxy_demo.csv')
        os.remove('proxy_demo.csv')
        old = pd.read_csv("descriptions.csv")
        old.drop(['size', 'price', 'discount_price', 'discount'], axis=1, inplace=True)
        merged = combined_csv.merge(old, left_on="id", right_on="id", how="inner").drop_duplicates()
        merged['discount_price'].replace('0', np.nan, inplace=True)
        merged['details'].replace('0', np.nan, inplace=True)
        merged.dropna(subset=['discount_price'], inplace=True)
        merged.to_csv('yoox_demo.csv', index=False)
    
    def parse_page(self, response):
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            cards = soup.find_all('div', {'class':'itemContainer'})
            for card in cards:
                data = parse_card(card)
                items.append(data)
            print('\nItems:', len(items))
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
