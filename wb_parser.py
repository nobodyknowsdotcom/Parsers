import math
import re
import time
from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException


url = "https://www.wildberries.ru/"

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(service=Service("./src/chromedriver.exe"), options=chrome_options)

action = webdriver.ActionChains(driver)
driver.get(url)

# sumulate categories button click
bttn = driver.find_element_by_class_name('j-menu-burger-btn')
bttn.click()

# get all main categories (consumer electronics, sport gear etc.)
main_categories = driver.find_elements_by_class_name('menu-burger__main-list-link')

time.sleep(1)

for e in main_categories[:25]:
    action.move_to_element(e)
    action.perform()

sub_cats_links = list()
sub_cats = driver.find_elements_by_class_name('j-menu-drop-link')

for e in sub_cats:
    sub_cats_links.append(e.get_attribute('href'))

print("Found sub-categories: " + str(len(sub_cats)))

def check_next_pages_aviablity(driver, link):
    try:
        driver.get(link)
        driver.find_element_by_class_name('goods-count')
        return True
    except NoSuchElementException:
        return False

def parse_product_card(response):
    name = response.find_element_by_class_name('goods-name').text+' '+response.find_element_by_class_name('brand-name').text.split('/')[0]

    try:
        discount = response.find_element_by_class_name('product-card__sale').text
        raw_price = re.findall('[0-9]+', response.find_element_by_class_name('price-old-block').text)
        price = "".join(raw_price)
    except NoSuchElementException:
        discount = 0
        raw_price = re.findall('[0-9]+', response.find_element_by_class_name('lower-price').text)
        price = "".join(raw_price)

    link = response.find_element_by_class_name('product-card__main').get_attribute('href')

    return [name, discount, link, price, category_name, subcategory_name, sub_subcategory_name, page_num, last_page]

# iterate over subcategories (womans/*, shoes/*)
for link in sub_cats_links:
    page_num = 1
    last_page = page_num + 1

    driver.get(link + '?page=%s' % page_num)

    while check_next_pages_aviablity(driver, link + '?page=%s' % page_num) and page_num <= last_page:
        # load page
        driver.get(link + '?page=%s' % page_num)

        # get all categories names
        category_name = driver.find_elements_by_class_name('breadcrumbs__item')[1].find_element_by_tag_name('span').text
        subcategory_name = driver.find_elements_by_class_name('breadcrumbs__item')[2].find_element_by_tag_name('span').text

        try:
            sub_subcategory_name = driver.find_elements_by_class_name('breadcrumbs__item')[3].find_element_by_tag_name('span').text
        except IndexError:
            sub_subcategory_name = ""

        # get number of pages
        try:
            raw_pages_count = driver.find_element_by_class_name('goods-count').find_elements_by_tag_name('span')[1].text
            last_page = math.ceil(int("".join(raw_pages_count.split(" ")))/100)
        except ValueError: 
            break

        product_cards = driver.find_elements_by_class_name('product-card.j-card-item')

        # parse product cards
        for e in product_cards:
            print(parse_product_card(e))

        page_num+=1
    
driver.close