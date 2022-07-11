import pickle
from urllib.request import Request
from bs4 import BeautifulSoup
import scrapy
import requests
import time
import json

from scrapy.crawler import CrawlerProcess
from seleniumwire import webdriver
from urllib3 import HTTPResponse

class wineparser(scrapy.Spider):
    name = 'wine'
    
    with open('urls.txt', 'r') as f:
        urls = f.readlines()   

    def start_requests(self):
        for url in self.urls:
            # TODO: вставить метод для парсинга HTML ответа
            
            request = scrapy.Request(
                url=url, 
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0',
                    'Connection': 'keep-alive',
                    'Host': 'winestyle.ru',
                    'Referer': 'https://winestyle.ru/',
                },
                callback=lambda response: self.parse_html(response, url)
            )
            yield request
    
    def parse_html(self, request, url: str):
        soup = BeautifulSoup(request.text, 'lxml')
        with open('response.txt', 'w') as f:
            f.write(request.text)
        exit()

        name = soup.select_one('h1').text.strip()
        title_seconds = soup.select_one('.meta span.text').text.strip()
        preview_pictures = soup.find('a', class_='img-container').get('href')
        detail_picture = soup.find('a', class_='img-container').get('href')
        desc = soup.find('div', class_='desc').find('div', class_='description-block collapse-content')
        notes_desc = soup.select_one('.articles-container.articles-col.collapsible-block.notes.opened-half').select('.description-block')
        if notes_desc != []:
            notes_color = notes_desc[0].find("p").text
            notes_vkus = notes_desc[1].find("p").text
            notes_aromat = notes_desc[2].find("p").text
            notes_gastr = notes_desc[3].find("p").text
        else:
            notes_color = ''
            notes_vkus = ''
            notes_aromat = ''
            notes_gastr = ''
        techs = {}
        select = soup.select('ul.list-description li')

        print(name)
        
        new_rows = []
        for row in select:
            cols = row.text.strip().split(':')
            if (len(row) != 0):
                if (len(row) != 1):
                    tech_name = row.find('span', class_="name").text.strip(':')
                    tech_value = row
                    tech_val = tech_value.span.decompose()
                    tech_val2 = tech_value.text.strip()
                    arr = [tech_name, tech_val2]
                    # print(val, value.text.strip(','))
                    new_rows.append(arr)

        for new_row in new_rows:
            techs[new_row[0]] = new_row[1].strip()

        item = {
            'name': name,
            'name_tr': title_seconds,
            'preview_pictures': preview_pictures,
            'detail_picture': detail_picture,
            'desc': str(desc),
            'notes_color': str(notes_color),
            'notes_vkus': str(notes_vkus),
            'notes_aromat': str(notes_aromat),
            'notes_gastr': str(notes_gastr),
            'techs': techs,
            'url': url,
        }

        print(item)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(wineparser)
    process.start()