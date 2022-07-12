import json
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
driver = webdriver.Chrome(service=Service("./chromedriver.exe"), options=options)

data = []
with open('./urls.txt', 'r') as f:
    urls = f.readlines()

def parse_soup(soup: BeautifulSoup, url: str):
    name = soup.select_one('h1').text.strip()
    title_seconds = soup.select_one('.meta span.text').text.strip()
    preview_pictures = soup.find('a', class_='img-container').get('href')
    detail_picture = soup.find('a', class_='img-container').get('href')
    desc = soup.find('div', class_='desc').find('p').get_text()
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
        'url': url.strip(),
    }
    return item

def dump_to_json(filename, data, **kwargs,):
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 1)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, **kwargs)

for url in urls:
    try:
        driver.get(url)
        time.sleep(2)
    except:
        time.sleep(5)
        continue
    try:
        item = parse_soup(BeautifulSoup(driver.page_source, 'lxml'), url)
    except AttributeError:
        continue
    data.append(item)
    print(item, len(data), sep='\n')

dump_to_json('winestyle.json', data)
driver.close()



