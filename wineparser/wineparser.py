from cgitb import html

import csv
import json
import xlsxwriter

from html.parser import HTMLParser

# from selenium import webdriver
# from selenium_stealth import stealth

import requests
import time
import random

# from fake_useragent import UserAgent
# ua = UserAgent()
# from fake_useragent import FakeUserAgentError

from bs4 import BeautifulSoup

# options = webdriver.ChromeOptions()
# options.add_argument("start-maximized")

# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# driver = webdriver.Chrome(options=options, executable_path=r"/Users/moisey/chromedriver")

# stealth(
#     driver,
#     languages=["ru-RU", "ru"],
#     vendor="Apple",
#     platform="MacOS",
#     webgl_vendor="Apple",
#     renderer="Apple M1",
#     fix_hairline=True,
# )

PAGES_COUNT = 10
# json_list_name = []
# for json_name in range(100):
#     json_list_name.append('/Bravo/ws_bravo_' + str(json_name) + '.json')

# print(OUT_FILENAME)
# l = list(range(5, 101))
# for i in l:
#     OUT_FILENAME = 'ws_bravo_0' + str(i) + '.json'

user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
]

def dump_to_json(filename, data, **kwargs):
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 1)
    
    with open(filename, 'w') as f:
        json.dump(data, f, **kwargs)

def dump_to_xlsx(filename, data):
    if not len(data):
        return None
    
    with xlsxwriter.Workbook(filename) as workbook:
        ws = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})

        headers = ['Название товара', 'Название с перевода', 'Фото списка', 'Фото детальная', 'Описание позиций', 'Ссылка', 'ДЗЦвет', 'ДЗВкус', 'ДЗАромат', 'ДЗ Гастр ст']
        headers.extend(data[0]['techs'].keys())

        for col, h in enumerate(headers):
            ws.write_string(0, col, h, cell_format=bold)

        for row, item in enumerate(data, start=1):
            ws.write_string(row, 0, item['name'])
            ws.write_string(row, 1, item['name_tr'])
            ws.write_string(row, 2, item['preview_pictures'])
            ws.write_string(row, 3, item['detail_picture'])
            ws.write_string(row, 4, item['desc'])
            ws.write_string(row, 5, item['url'])
            ws.write_string(row, 6, item['notes_color'])
            ws.write_string(row, 7, item['notes_vkus'])
            ws.write_string(row, 8, item['notes_aromat'])
            ws.write_string(row, 9, item['notes_gastr'])
            for prop_name, prop_value in item['techs'].items():
                col = headers.index(prop_name)
                print(prop_name)
                try:
                    ws.write_string(row, col, prop_value)
                except Exception as ex:
                    print(row, col, prop_value, ex)

def get_free_proxies_http():
    url = "https://free-proxy-list.net/"
    # посылаем HTTP запрос и создаем soup объект
    free_proxy_lists = BeautifulSoup(requests.get(url).content, "html.parser")
    proxies_http = []
    tr = free_proxy_lists.select_one(".table.table-striped.table-bordered").select("tbody tr")
    for row in tr:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            hx = tds[6].text.strip()
            hm = tds[7].text.strip()
            hm_secs = hm.find(' secs')
            host = f"{ip}:{port}"
            if (hm_secs >= 1):
                if (hx == 'no'):
                    proxies_http.append(host)
            if (hm == '1 min ago'):
                if (hx == 'no'):
                    proxies_http.append(host)
        except IndexError:
            continue
    return proxies_http

def get_free_proxies_https():
    url = "https://free-proxy-list.net/"
    # посылаем HTTP запрос и создаем soup объект
    free_proxy_lists = BeautifulSoup(requests.get(url).content, "html.parser")
    proxies_https = []
    tr = free_proxy_lists.select_one(".table.table-striped.table-bordered").select("tbody tr")
    for row in tr:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            hx = tds[6].text.strip()
            hm = tds[7].text.strip()
            hm_secs = hm.find(' secs')
            host = f"{ip}:{port}"
            if (hm_secs >= 1):
                if (hx == 'yes'):
                    proxies_https.append(host)
            if (hm == '1 min ago'):
                if (hx == 'yes'):
                    proxies_https.append(host)
        except IndexError:
            continue
    return proxies_https

def get_session_https(get_free_proxies_https):
    # создаем сессию для отправки HTTP запроса
    session_https = requests.Session()
    # выбираем случайным образом один из адресов
    proxy_https = random.choice(get_free_proxies_https())
    session_https.proxies = {"https": proxy_https}
    return session_https

def get_session_http(get_free_proxies_http):
    # создаем сессию для отправки HTTP запроса
    session_http = requests.Session()
    # выбираем случайным образом один из адресов
    proxy_http = random.choice(get_free_proxies_http())
    session_http.proxies = {"http": proxy_http}
    return session_http

def get_soup(url):
    user_agent = random.choice(user_agent_list)

    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Host': 'winestyle.ru',
        'Referer': 'https://winestyle.ru/',
        # 'Sec-Fetch-Dest': 'document',
        # 'Sec-Fetch-Mode': 'navigate',
        # 'Sec-Fetch-Site': 'same-origin',
        'User-Agent': user_agent
    }

    # ses_http = get_session_http(get_free_proxies_http)

    # ses_https = get_session_https(get_free_proxies_https)

    # set_proxies_http = ses_http.get("http://icanhazip.com", timeout=2).text.strip()

    # set_proxies_https = ses_https.get("http://icanhazip.com", timeout=3).text.strip()

    # print(ses_http, set_proxies_http)

    # print(ses_https, set_proxies_https)

    # , proxies=set_proxies
    
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, features='html.parser')
        else:
            soup = None
        return soup
    # except FakeUserAgentError:
    #     pass
    except Exception as ex:
        return get_soup(url)

OUT_FILENAME = './Bravo/ws_bravo_44.json'

def crawl_products():
    """
    Собирает со страниц с 1 по pages_count включительно ссылки на товары.
    """
    urls = [
        "https://ekb.winestyle.ru/products/Arran-10-years-gift-box-with-two-glasses.html",
        "https://winestyle.ru/products/Machrie-Moor-Cask-Strength-56-2-in-tube.html",
        "https://winestyle.ru/products/Robert-Burns-Blend-In-Tube.html",
        "https://winestyle.ru/products/Ailsa-Bay-Sweet-Smoke.html",
        "https://winestyle.ru/products/Glenfarclas-105-in-tube.html",
        "https://winestyle.ru/products/Glenfarclas-10-years-in-tube.html",
        "https://winestyle.ru/products/Glenfarclas-12-years-in-tube.html",
        "https://winestyle.ru/products/Glenfarclas-15-years-in-tube-700.html",
        "https://winestyle.ru/products/Glenfarclas-185-th-Anniversary-in-tube.html",
        "https://winestyle.ru/products/Glenfarclas-25-years-in-tube.html",
        "https://winestyle.ru/products/Glenfarclas-Heritage-In-Tube.html",
        "https://winestyle.ru/products/Glenfarclas-1954-Family-Casks-46-7-wooden-box.html",
        "https://winestyle.ru/products/Glenfarclas-1955-Family-Casks-45-4-in-wooden-box.html",
        "https://winestyle.ru/products/Glenfarclas-1956-Family-Casks-48-3.html",
        "https://winestyle.ru/products/Glenfarclas-1958-Family-Casks-40-2-in-gift-box.html",
        "https://winestyle.ru/products/Glenfarclas-1961-Family-Casks-44-2.html",
        "https://winestyle.ru/products/Glenfarclas-1963-Family-Casks-47-4-gift-box.html",
        "https://winestyle.ru/products/Glenfarclas-1968-Family-Casks-41-7-in-wooden-box.html",
        "https://winestyle.ru/products/Glenfarclas-1969-Family-Casks-56-1.html",
        "https://winestyle.ru/products/Glenfarclas-1973-Family-Casks-41-6.html",
        "https://winestyle.ru/products/Glenfarclas-1974-Family-Casks-55-1.html",
        "https://winestyle.ru/products/Glenfarclas-1975-Family-Casks-44-5.html",
        "https://winestyle.ru/products/Glenfarclas-1976-Family-Casks-45-9.html",
        "https://winestyle.ru/products/Langs-Full-Smoky.html",
        "https://winestyle.ru/products/Tomatin-12-Years-Old-gift-box.html",
        "https://winestyle.ru/products/Tomatin-12-Year-Old-gift-box.html",
        "https://winestyle.ru/products/Tomatin-14-Years-Old-gift-box.html",
        "https://winestyle.ru/products/Tomatin-30-Years-Old-wooden-box.html",
        "https://winestyle.ru/products/Tomatin-Limited-Edition-French-Collection-Cognac-Casks-2008-gift-box.html",
        "https://winestyle.ru/products/Tomatin-Legacy.html",
        "https://winestyle.ru/products/Tomatin-Legacy-gift-box.html",
        "https://winestyle.ru/products/The-Antiquary-12-years-old-gift-box.html",
        "https://winestyle.ru/products/The-Antiquary-21-years-old-gift-box.html",
        "https://winestyle.ru/products/The-Antiquary-gift-box.html",
        "https://winestyle.ru/products/Edradour-21-Years-Old-Barolo-Cask-Finish-1999-in-tube.html",
        "https://winestyle.ru/products/Edradour-19-Years-Old-Bordeaux-Cask-Finish-1999-in-tube.html",
        "https://winestyle.ru/products/Kilchoman-Machir-Bay-gift-box-with-2-glasses.html",
        "https://winestyle.ru/products/Kilchoman-Machir-Bay-gift-box.html",
        "https://winestyle.ru/products/Kilchoman-Madeira-Cask-Matured-50-gift-box.html",
        "https://winestyle.ru/products/Teeling-Irish-Whiskey-50.html",
        "https://winestyle.ru/products/Teeling-Irish-Whiskey-gift-set-with-2-glasses.html",
        "https://winestyle.ru/products/Teeling-Irish-Whiskey-5000.html",
        "https://winestyle.ru/products/Teeling-Irish-Whiskey-Single-Grain-gift-tube.html",
        "https://winestyle.ru/products/Teeling-Irish-Whiskey-Single-Grain.html",
        "https://winestyle.ru/products/Teeling-Blackpitts-Peated-Single-Malt-in-tube.html",
        "https://winestyle.ru/products/Teeling-Single-Malt-Irish-Whiskey-in-tube.html",
        "https://winestyle.ru/products/Teeling-30-Year-Old-Single-Malt-Irish-Whiskey.html",
        "https://winestyle.ru/products/Teeling-Single-Malt-32-Year-Old-wooden-box.html",
        "https://winestyle.ru/products/Teeling-Single-Malt-Irish-Whiskey-in-tube.html",
        "https://winestyle.ru/products/Teeling-Renaissance-Series-3-Single-Malt-Irish-Whiskey-18-Years-Old-gift-box.html",
        "https://winestyle.ru/products/Teeling-Single-Pot-Still-gift-box.html",
        "https://winestyle.ru/products/Teeling-Spirit-of-Dublin.html",
        "https://winestyle.ru/products/Teeling-Amber-Ale-gift-box.html",
        "https://winestyle.ru/products/Teeling-Stout-Cask-Irish-Whiskey-gift-box.html",
        "https://winestyle.ru/products/Heaven-Hill-Old-Style-Bourbon.html",
        "https://winestyle.ru/products/Evan-Williams-Bottled-in-Bond.html",
        "https://winestyle.ru/products/Evan-Williams-Extra-Aged.html",
        "https://winestyle.ru/products/Evan-Williams-Single-Barrel-Vintage-2013.html",
        "https://winestyle.ru/products/Rittenhouse-Rye-Bottled-in-Bond.html",
        "https://winestyle.ru/products/Four-Roses-50.html",
        "https://winestyle.ru/products/Four-Roses.html",
        "https://winestyle.ru/products/Four-Roses-700.html",
        "https://winestyle.ru/products/Four-Roses-1000.html",
        "https://winestyle.ru/products/Four-Roses-Single-Barrel-50.html",
        "https://winestyle.ru/products/Four-Roses-Single-Barrel.html",
        "https://winestyle.ru/products/Four-Roses-Small-Batch.html",
        "https://winestyle.ru/products/Tenjaku-500.html",
        "https://winestyle.ru/products/Tenjaku-gift-box.html",
        "https://winestyle.ru/products/Tenjaku-Pure-Malt-500.html",
        "https://winestyle.ru/products/Tenjaku-Pure-Malt-gift-box.html",
        "https://winestyle.ru/products/Kavalan-Concertmaster-Sherry-Cask-Finish-gift-box.html",
        "https://winestyle.ru/products/Kavalan-King-Car-gift-box.html",
        "https://winestyle.ru/products/Kavalan-Solist-Brandy-Single-Cask-57-1-gift-box.html",
        "https://winestyle.ru/products/Kavalan-Solist-Amontillado-Sherry-Cask-55-6-wooden-box.html",
        "https://winestyle.ru/products/Kavalan-Solist-Amontillado-Sherry-Cask-56-3-wooden-box-with-glass.html",
        "https://winestyle.ru/products/Black-Velvet-700.html",
        "https://winestyle.ru/products/Black-Velvet-1000.html",
        "https://winestyle.ru/products/Armorik-Classic-gift-set-with-2-glasses.html",
        "https://winestyle.ru/products/Armorik-Classic-gift-box.html",
        "https://winestyle.ru/products/Armorik-Dervenn-gift-box.html",
        "https://winestyle.ru/products/Armorik-Double-Maturation-gift-box.html",
        "https://winestyle.ru/products/Armorik-Sherry-Cask-gift-box.html",
        "https://winestyle.ru/products/M-H-Classic-gift-box.html",
        "https://winestyle.ru/products/M-H-Elements-Peated-gift-box.html",
        "https://winestyle.ru/products/M-H-Elements-Red-Wine-gift-box.html",
        "https://winestyle.ru/products/M-H-Elements-Sherry-gift-box.html",
        "https://winestyle.ru/products/Mithuna-by-Paul-John-gift-box.html",
        "https://winestyle.ru/products/Paul-John-Nirvana.html",
        "https://winestyle.ru/products/Paul-John-Nirvana-gift-box.html",
        "https://winestyle.ru/products/Paul-John-Bold-50.html",
        "https://winestyle.ru/products/Paul-John-Bold-in-tube.html",
        "https://winestyle.ru/products/Paul-John-Brilliance-50.html",
        "https://winestyle.ru/products/Paul-John-Brilliance-in-tube.html",
        "https://winestyle.ru/products/Paul-John-Edited-50.html",
        "https://winestyle.ru/products/Paul-John-Edited-in-tube.html",
        "https://winestyle.ru/products/Paul-John-Oloroso-Select-Cask-gift-box.html",
        "https://winestyle.ru/products/Paul-John-Peated-Select-Cask.html",
        "https://winestyle.ru/products/Paul-John-Pedro-Ximenez-Select-Cask-gift-box.html",
        "https://winestyle.ru/products/Cotswolds-Founders-Choice-gift-box.html",
        "https://winestyle.ru/products/Cotswolds-Peated-Cask-gift-box.html",
        "https://winestyle.ru/products/Cotswolds-Peated-Cask-60-4-gift-box.html",
        "https://winestyle.ru/products/Penderyn-Celt-gift-box.html",
        "https://winestyle.ru/products/Penderyn-Legend-gift-box.html",
        "https://winestyle.ru/products/Penderyn-Myth-gift-box.html",
        "https://winestyle.ru/products/Penderyn-Madeira-Finish-gift-box.html",
        "https://winestyle.ru/products/Penderyn-Peated-gift-box.html",
        "https://winestyle.ru/products/Penderyn-Portwood-gift-box.html",
        "https://winestyle.ru/products/Penderyn-Rich-Oak-gift-box.html",
        "https://winestyle.ru/products/Puni-Gold-gift-box.html",
        "https://winestyle.ru/products/Puni-Sole-gift-box.html",
        "https://winestyle.ru/products/Puni-Vina-gift-box.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1914-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1915-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1924-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1925-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1929-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1930-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1934-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1939-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1941-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1944-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1946-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1952-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1960-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1961-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1962-Bas-Armagnac-700.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1964-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1965-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1966-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1967-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1970-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1971-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1972-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1973-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1974-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1975-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1976-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1978-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1978-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1980-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1981-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1982-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1983-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1984-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1985-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1986-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1987-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1988-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1990-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1991-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1992-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1993-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1994-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1997-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1998-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-1999-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-2000-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-2002-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-Napoleon-10-ans-Bas-Armagnac-gift-box.html",
        "https://winestyle.ru/products/Baron-G-Legrand-VS-Bas-Armagnac.html",
        "https://winestyle.ru/products/Baron-G-Legrand-VSOP-Bas-Armagnac.html",
        "https://winestyle.ru/products/Lheraud-Cognac-Charles-X.html",
        "https://winestyle.ru/products/Lheraud-Cognac-Cuvee-10.html",
        "https://winestyle.ru/products/Lheraud-Cognac-Cuvee-20-5000.html",
        "https://winestyle.ru/products/Lheraud-Cognac-Extra-gift-box.html",
        "https://winestyle.ru/products/Lheraud-Cognac-Vieux-Millenaire-wooden-box.html",
        "https://winestyle.ru/products/Lheraud-Oublie-XO.html",
        "https://winestyle.ru/products/Lheraud-Cognac-1963-Petite-Champagne.html",
        "https://winestyle.ru/products/Lheraud-Cognac-1972-Petite-Champagne.html",
        "https://winestyle.ru/products/Lheraud-Cognac-1973-Grande-Champagne.html",
        "https://winestyle.ru/products/Lheraud-Cognac-1982-Fins-Bois-700.html",
        "https://winestyle.ru/products/Lheraud-Cognac-1982-Petite-Champagne.html",
        "https://winestyle.ru/products/Lheraud-Cognac-1987-Grande-Champagne-AOC-wooden-box.html",
        "https://winestyle.ru/products/Lheraud-Cognac-1988-Petite-Champagne.html",
        "https://winestyle.ru/products/Lheraud-Cognac-1989-Petite-Champagne.html",
        "https://winestyle.ru/products/Lheraud-Pineau-des-Charentes-Collection-Perle-Rose.html",
        "https://winestyle.ru/products/Lheraud-Pineau-Charentais-Signature-Ugni-Blanc.html",
        "https://winestyle.ru/products/Lheraud-Pineau-Vieux-15-years.html",
        "https://winestyle.ru/products/A-E-Dor-Albane-Grande-Champagne-gift-box.html",
        "https://winestyle.ru/products/A-E-Dor-Sigar.html",
        "https://winestyle.ru/products/A-E-Dor-Embleme.html",
        "https://winestyle.ru/products/A-E-Dor-Extra-wooden-box.html",
        "https://winestyle.ru/products/A-E-Dor-Extra-Cristal-gift-bag.html",
        "https://winestyle.ru/products/A-E-Dor-Gold.html",
        "https://winestyle.ru/products/A-E-Dor-Napoleon.html",
        "https://winestyle.ru/products/A-E-Dor-10-wooden-box.html",
        "https://winestyle.ru/products/A-E-Dor-6-wooden-box.html",
        "https://winestyle.ru/products/A-E-Dor-8-wooden-box.html",
        "https://winestyle.ru/products/A-E-Dor-VSOP-Rare-Fine-Champagne-wooden-box.html",
        "https://winestyle.ru/products/A-E-Dor-6.html",
        "https://winestyle.ru/products/A-E-Dor-4-Season-s-gift-box.html",
        "https://winestyle.ru/products/A-E-Dor-VSOP-Rare-Fine-Champagne-wooden-box.html",
        "https://winestyle.ru/products/A-E-Dor-XO-40-350.html",
        "https://winestyle.ru/products/Albert-Jarraud-XO-New-Design-gift-box.html",
        "https://winestyle.ru/products/Carolans-Irish-Cream-500.html",
        "https://winestyle.ru/products/Carolans-Irish-Cream-700.html",
        "https://winestyle.ru/products/Carolans-Irish-Cream-1000.html",
        "https://winestyle.ru/products/Irish-Mist-Honey.html",
        "https://winestyle.ru/products/Irish-Mist-Honey-1000.html",
        "https://winestyle.ru/products/Christian-Drouin-Bouche-Brut-de-Normandie.html",
        "https://winestyle.ru/products/Blanche-de-Normandie.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-15-ans-gift-box.html",
        "https://winestyle.ru/products/Christian-Drouin-Hine-Angels-17-Years-Old.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-VSOP-42-Gift-box.html",
        "https://winestyle.ru/products/Christian-Drouin-Calvados-Pays-d-Auge-XO-gift-box.html",
        "https://winestyle.ru/products/Christian-Drouin-Calvados-Selection.html",
        "https://winestyle.ru/products/Christian-Drouin-Calvados-Selection-gift-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-1961-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-1962-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-1971-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1972-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1976-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1977-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1981-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1982-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1986-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1987-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1991-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1992-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1996-wooden-box.html",
        "https://winestyle.ru/products/Coeur-de-Lion-Calvados-Pays-d-Auge-1997-wooden-box.html",
        "https://winestyle.ru/products/Christian-Drouin-Pommeau-de-Normandie-gift-box.html",
        "https://winestyle.ru/products/Bocchino-Gran-Moscato.html",
        "https://winestyle.ru/products/Bocchino-Sigillo-Nero.html",
        "https://winestyle.ru/products/Bocchino-Cantina-Privata-18-anni-wooden-box.html",
        "https://winestyle.ru/products/Bocchino-Cantina-Privata-8-anni-wooden-box.html",
        "https://winestyle.ru/products/Bocchino-Cantina-Privata-8-anni-gift-box-with-2-glasses.html",
        "https://winestyle.ru/products/Rochel-Bay-Classic.html",
        "https://winestyle.ru/products/Rochel-Bay-Traditional.html",
        "https://winestyle.ru/products/Brecon-Botanicals-Gin.html",
        "https://winestyle.ru/products/Edinburgh-Gin-Bramble-Honey.html",
        "https://winestyle.ru/products/Edinburgh-Gin-Cannonball-Navy-Strength.html",
        "https://winestyle.ru/products/Edinburgh-Gin-Classic.html",
        "https://winestyle.ru/products/Edinburgh-Gin-Rhubarb-Ginger-Gin.html",
        "https://winestyle.ru/products/Edinburgh-Gin-Seaside.html",
        "https://winestyle.ru/products/Cotswolds-Dry-Gin.html",
        "https://winestyle.ru/products/Christian-Drouin-Le-Gin.html",
        "https://winestyle.ru/products/Christian-Drouin-Le-Gin-Carmina.html",
        "https://winestyle.ru/products/Le-Gin-de-Christian-Drouin-Calvados-Cask-Finish.html",
        "https://winestyle.ru/products/Kavalan-gift-box.html",
        "https://winestyle.ru/products/La-Fee-Absinthe-Bohemian.html",
        "https://winestyle.ru/products/Reyka-Small-Batch-Vodka-50.html",
        "https://winestyle.ru/products/Reyka-Small-Batch-Vodka.html",
        "https://winestyle.ru/products/Reyka-Small-Batch-Vodka-1000.html",
        "https://winestyle.ru/products/Danzka-Citrus.html",
        "https://winestyle.ru/products/Danzka-Cranraz.html",
        "https://winestyle.ru/products/Danzka-Currant.html",
        "https://winestyle.ru/products/Danzka-Fifty.html",
        "https://winestyle.ru/products/Danzka-Grapefruit-700.html",
        "https://winestyle.ru/products/Danzka-500.html",
        "https://winestyle.ru/products/Danzka-750.html",
        "https://winestyle.ru/products/Danzka.html",
        "https://winestyle.ru/products/Danzka-1750.html",
        "https://winestyle.ru/products/Blavod-Black-500.html",
        "https://winestyle.ru/products/Blavod-Black-1000.html",
        "https://winestyle.ru/products/ORA-Blue-50.html",
        "https://winestyle.ru/products/ORA-Blue-gift-box.html",
        "https://winestyle.ru/products/ORA-Blue.html",
        "https://winestyle.ru/products/Penderyn-Five.html",
        "https://winestyle.ru/products/Aecovi-Jerez-Alexandro-Fino.html",
        "https://winestyle.ru/products/Aecovi-Jerez-Alexandro-Oloroso.html",
        "https://winestyle.ru/products/Aecovi-Jerez-Alexandro-Sanlucar-Manzanilla.html",
        "https://winestyle.ru/products/Aecovi-Jerez-Alexandro-Medium.html",
        "https://winestyle.ru/products/Aecovi-Jerez-Alexandro-Cream.html",
        "https://winestyle.ru/products/Aecovi-Jerez-Alexandro-Moscatel.html",
        "https://winestyle.ru/products/Aecovi-Jerez-Alexandro-Pedro-Ximenez.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-30-Years-Old-Tawny-Port.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Rose-Port.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Lote-601-Ruby-Port-500.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Lote-601-Ruby-Port.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Vintage-2004-Port.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Vintage-2005-Port.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Vintage-2009-Port.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Vintage-Port-2012.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Vintage-2014-Port.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Vintage-2015-Port.html",
        "https://winestyle.ru/products/Quinta-De-La-Rosa-Vintage-Port-2019.html",
        "https://winestyle.ru/products/Delamotte-Brut-Blanc-de-Blancs-gift-box-375.html",
        "https://winestyle.ru/products/Delamotte-Brut-Blanc-de-Blancs-gift-box.html",
        "https://winestyle.ru/products/Delamotte-Brut-Blanc-de-Blancs-gift-box-1500.html",
        "https://winestyle.ru/products/Delamotte-Brut-Blanc-de-Blancs-2014-gift-box.html",
        "https://winestyle.ru/products/Delamotte-Brut-Champagne-AOC.html",
        "https://winestyle.ru/products/Delamotte-Brut-Champagne-AOC-gift-box-750.html",
        "https://winestyle.ru/products/Delamotte-Brut-Champagne-AOC-gift-box.html",
        "https://winestyle.ru/products/Brut-Rose-750.html",
        "https://winestyle.ru/products/Zantho-Gruner-Veltliner-2020.html",
        "https://winestyle.ru/products/Zantho-Rose-Brut-gift-box.html",
        "https://winestyle.ru/products/Zardetto-Private-Cuvee-Brut.html",
        "https://winestyle.ru/products/Zardetto-Prosecco-DOC-Brut.html",
        "https://winestyle.ru/products/Zardetto-Cartizze-Valdobbiadene-Superiore-di-Cartizze-DOCG-Dry-2019.html",
        "https://winestyle.ru/products/Zardetto-Long-Charmat-Conegliano-Valdobbiadene-DOCG-Prosecco-Superiore-Brut.html",
        "https://winestyle.ru/products/Zardetto-Prosecco-DOC-Extra-Dry.html",
        "https://winestyle.ru/products/Zardetto-Prosecco-DOC-Rose-Extra-Dry.html",
        "https://winestyle.ru/products/Zardetto-Vivus-Frizzante.html",
        "https://winestyle.ru/products/Chateau-Reynon-Sauvignon-Blanc-Bordeaux-AOC-2018.html",
        "https://winestyle.ru/products/Les-Arums-de-Lagrange-2016.html",
        "https://winestyle.ru/products/Chateau-La-Croix-de-Roche-Bordeaux-Superieur-AOC-2016.html",
        "https://winestyle.ru/products/Chateau-La-Grande-Metairie-Bordeaux-AOC-2016.html",
        "https://winestyle.ru/products/Petite-Laurence-Bordeaux-Superieur-AOC-2015.html",
        "https://winestyle.ru/products/Chateau-Carbonnieux-Blanc-Pessac-Leognan-AOC-Grand-Cru-Classe-de-Graves-2011.html",
        "https://winestyle.ru/products/Chateau-Cantemerle-Haut-Medoc-AOC-5-me-Grand-Cru-2015.html",
        "https://winestyle.ru/products/Chateau-du-Breuil-Haut-Medoc-AOC-2014.html",
        "https://winestyle.ru/products/Chateau-Branas-Grand-Poujeaux-Moulis-en-Medoc-AOC-2011.html",
        "https://winestyle.ru/products/Les-Pagodes-de-Cos-AOC-Saint-Estephe-2013.html",
        "https://winestyle.ru/products/Les-Pelerins-de-Lafon-Rochet-St-Estephe-AOC-2014.html",
        "https://winestyle.ru/products/Les-Fiefs-de-Lagrange-Saint-Julien-AOC-2015.html",
        "https://winestyle.ru/products/Chateau-Rieussec-Sauternes-AOC-1-er-Grand-Cru-Classe-2006.html",
        "https://winestyle.ru/products/Patrice-Moreux-Corty-Artisan-Caillottes-Pouilly-Fume-AOC-2020.html",
        "https://winestyle.ru/products/Patrice-Moreux-Corty-Artisan-Intro-Pouilly-Fume-AOC-2020.html",
        "https://winestyle.ru/products/Patrice-Moreux-Corty-Artisan-Silex-Pouilly-Fume-AOC-2020.html",
        "https://winestyle.ru/products/Patrice-Moreux-Corty-Artisan-Intro-Sancerre-AOC-2020.html",
        "https://winestyle.ru/products/Patrice-Moreux-Corty-Artisan-Les-Monts-Damnes-Sancerre-AOC-2019.html",
        "https://winestyle.ru/products/Eugenio-Collavini-Blanc-Fumat-Sauvignon-Collio-DOC-2020.html",
        "https://winestyle.ru/products/Eugenio-Collavini-Broy-Collio-DOC-2016.html",
        "https://winestyle.ru/products/Eugenio-Collavini-Broy-Collio-DOC-2017.html",
        "https://winestyle.ru/products/Eugenio-Collavini-dei-Sassi-Cavi-Chardonnay-Collio-DOC-2020.html",
        "https://winestyle.ru/products/Eugenio-Collavini-T-Friulano-Collio-DOC-2020.html",
        "https://winestyle.ru/products/Eugenio-Collavini-Turian-Ribolla-Gialla-Colli-Orientali-del-Friuli-DOC-2019.html",
        "https://winestyle.ru/products/Eugenio-Collavini-Forresco-Colli-Orientali-del-Friuli-DOC-2012.html",
        "https://winestyle.ru/products/Eugenio-Collavini-Merlot-dal-Pic-Collio-DOC-2016-750.html",
        "https://winestyle.ru/products/Eugenio-Collavini-Turian-Schioppettino-Colli-Orientali-del-Friuli-DOC-2015.html",
        "https://winestyle.ru/products/Tagaro-Cinquenoci-Primitivo-Puglia-IGT-2020.html",
        "https://winestyle.ru/products/Tagaro-Mancinello-Nero-di-Troia-Puglia-IGT-2020.html",
        "https://winestyle.ru/products/Tagaro-Muso-Rosso-Primitivo-di-Manduria-DOC-2019.html",
        "https://winestyle.ru/products/Tagaro-Pie-del-Monaco-Primitivo-Puglia-IGT-2018.html",
        "https://winestyle.ru/products/Tagaro-Pie-del-Monaco-Primitivo-Limited-Edition-Puglia-IGT-2013.html",
        "https://winestyle.ru/products/Tagaro-Seicaselle-Negroamaro-Puglia-IGT-2020.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Soave-DOC-Classico-2020.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Le-Preare-Garganega-Verona-IGT-2020.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Le-Preare-Pinot-Grigio-delle-Venezie-DOC-2020.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Le-Preare-Soave-DOC-2020.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Bardolino-Chiaretto-DOC-Classico-2019.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Le-Preare-Bardolino-Chiaretto-DOC-2020.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Amarone-della-Valpolicella-DOCG-Classico-2018.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Bardolino-DOC-Classico-2019.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Valpolicella-Ripasso-DOC-Classico-Superiore-2019.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Le-Preare-Amarone-della-Valpolicella-DOCG-2018.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Le-Preare-Appassimento-Rosso-Veneto-IGT-2020.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Corvina-Verona-IGT-2019.html",
        "https://winestyle.ru/products/Cantina-di-Negrar-Le-Preare-Valpolicella-Ripasso-Superiore-DOC-2019.html",
        "https://winestyle.ru/products/Zantho-Gruner-Veltliner-2020-250.html",
        "https://winestyle.ru/products/Zantho-Gruner-Veltliner-2020.html",
        "https://winestyle.ru/products/Zantho-Muskat-Ottonel-2020.html",
        "https://winestyle.ru/products/Zantho-Sauvignon-Blanc-2020.html",
        "https://winestyle.ru/products/Zantho-Welschriesling-2020.html",
        "https://winestyle.ru/products/Zantho-Pink-2020.html",
        "https://winestyle.ru/products/Zantho-Blaufrankisch-2020.html",
        "https://winestyle.ru/products/Zantho-Cuvee-1487-2018.html",
        "https://winestyle.ru/products/Zantho-Merlot-Reserve-2019.html",
        "https://winestyle.ru/products/Zantho-Pinot-Noir-Reserve-2018.html",
        "https://winestyle.ru/products/Zantho-St-Laurent-2019.html",
        "https://winestyle.ru/products/Zantho-St-Laurent-Reserve-2017.html",
        "https://winestyle.ru/products/Zantho-Zweigelt-2019-250.html",
        "https://winestyle.ru/products/Zantho-Zweigelt-2020.html",
        "https://winestyle.ru/products/Zantho-Zweigelt-Reserve-2019.html",
        "https://winestyle.ru/products/Zantho-Beerenauslese-2017.html",
        "https://winestyle.ru/products/Zantho-Eiswein-2018.html",
        "https://winestyle.ru/products/Zantho-Trockenbeerenauslese-2018.html",
        "https://winestyle.ru/products/Dominio-del-Plata-Crios-Chardonnay-2020.html",
        "https://winestyle.ru/products/Dominio-del-Plata-Crios-Torrontes-2020.html",
        "https://winestyle.ru/products/Dominio-del-Plata-Crios-Rose-of-Malbec-2020.html",
        "https://winestyle.ru/products/Dominio-del-Plata-BenMarco-Expresivo-2018.html",
        "https://winestyle.ru/products/Dominio-del-Plata-BenMarco-Malbec-2019.html",
        "https://winestyle.ru/products/Dominio-del-Plata-Crios-Cabernet-Sauvignon-2019.html",
        "https://winestyle.ru/products/Dominio-del-Plata-Crios-Malbec-2019.html",
        "https://winestyle.ru/products/Dominio-del-Plata-Susana-Balbo-Brioso-2018.html",
        "https://winestyle.ru/products/Dominio-del-Plata-Susana-Balbo-Cabernet-Sauvignon-2017.html",
        "https://winestyle.ru/products/Dominio-del-Plata-Susana-Balbo-Cabernet-Sauvignon-2018.html",
        "https://winestyle.ru/products/Dominio-del-Plata-Susana-Balbo-Malbec-2018.html",
        "https://winestyle.ru/products/Konrad-Riesling-2017.html",
        "https://winestyle.ru/products/Konrad-Sauvignon-Blanc-2020.html",
        "https://winestyle.ru/products/Konrad-Pinot-Noir-2020.html"
    ]

    # fmt = 'https://parsemachine.com/sandbox/catalog/?page={page}'

    # for page_n in range(1, 1 + pages_count):
    #     print('page: {}'.format(page_n))

    #     page_url = fmt.format(page=page_n)
    #     soup = get_soup(page_url)
    #     if soup is None:
    #         break

    #     for tag in soup.select('.product-card .title'):
    #         href = tag.attrs['href']
    #         url = 'https://parsemachine.com{}'.format(href)
    #         urls.append(url)

    return urls



def parse_products(urls):
    """
    :param urls:            список URL на карточки товаров.
    :return:                массив спарсенных данных по каждому из товаров.
    """
    data = []

    for url in urls:
        # driver.get(url)
        # print('\tproduct: {}'.format(url))

        soup = get_soup(url)
        if soup is None:
            break

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

        # name = driver.find_element("h1")
        # price = driver.find_element("h1")
        print(name)
        # title_seconds = driver.select_one('.meta span.text').text.strip()
        # preview_pictures = driver.find('a', class_='img-container').get('href')
        # detail_picture = driver.find('a', class_='img-container').get('href')
        # desc = driver.find('div', class_='desc').find('div', class_='description-block collapse-content')
        # notes_desc = driver.select_one('.articles-container.articles-col.collapsible-block.notes.opened-half').select('.description-block')
        # if notes_desc != []:
        #     notes_color = notes_desc[0].find("p").text
        #     notes_vkus = notes_desc[1].find("p").text
        #     notes_aromat = notes_desc[2].find("p").text
        #     notes_gastr = notes_desc[3].find("p").text
        # else:
        #     notes_color = ''
        #     notes_vkus = ''
        #     notes_aromat = ''
        #     notes_gastr = ''
        # techs = {}
        # select = soup.select('ul.list-description li')
        
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
        data.append(item)
        
        # driver.quit()

    return data


def main():
    # urls = crawl_products(PAGES_COUNT)
    urls = crawl_products()
    data = parse_products(urls)
    dump_to_json(OUT_FILENAME, data)
    # dump_to_xlsx(OUT_XLSX_FILENAME, data)
    # send_document(OUT_FILENAME, TELEGRAM_TOKEN, CHAT_ID)
    # send_document(OUT_XLSX_FILENAME, TELEGRAM_TOKEN, CHAT_ID)


if __name__ == '__main__':
    main()