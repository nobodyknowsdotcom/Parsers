import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
driver = webdriver.Chrome(service=Service("./chromedriver.exe"), options=options)

with open('./urls.txt', 'r') as f:
    urls = f.readlines()

for url in urls:
    driver.get(url)
    time.sleep(1.5)


