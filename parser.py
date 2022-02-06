import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from lxml import html


url = "https://www.dns-shop.ru/catalog/17a892f816404e77/noutbuki/?order=2"

driver = webdriver.Chrome(service=Service("./src/chromedriver.exe"), options=webdriver.ChromeOptions())
driver.get(url)
content = driver.page_source

tree = html.fromstring(content)

refs = list()
names = list()
prices = list()

last_page = tree.xpath('//li[@class="pagination-widget__page"]/@data-page-number')[-1]
last_page = int(last_page)

page_num = 1

while page_num <= last_page:

    if (page_num==1):
        url = "https://www.dns-shop.ru/catalog/17a892f816404e77/noutbuki/?order=2"
    else:
        url = "https://www.dns-shop.ru/catalog/17a892f816404e77/noutbuki/?order=2&p=%s" % page_num

    driver.get(url)

    time.sleep(3)

    name = driver.find_elements_by_class_name('catalog-product__name')
    price = driver.find_elements_by_class_name('product-buy__price')
    link = driver.find_elements_by_class_name('catalog-product__name')

    print('\nСтраница: %s из %s' % (page_num, last_page))

    for i in name:
        names.append(i.text)
    print("Names length: %s" % len(names))

    for i in price:
        i = i.text.split(" ")
        res = i[0]+i[1]
        prices.append("".join(res))
    print("Prices length: %s" % len(prices))

    for i in link:
        refs.append(i.get_attribute("href"))
    print("Links length: %s" % len(refs))

    page_num += 1

driver.close()


dict = {'Price': prices, 'Name': names, 'Link': refs}
df = pd.DataFrame(data=dict)
df.to_excel("output.xlsx")