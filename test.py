import time
import requests
from bs4 import BeautifulSoup

page = requests.get('https://www.wildberries.ru/catalog/zhenshchinam/odezhda/bluzki-i-rubashki?sort=popular&page=2', headers=)
time.sleep(5)
soup = BeautifulSoup(page.text, 'lxml')

for product_card in soup.find_all('div', {'class':'product-card__wrapper'}):
    name = product_card.find('span', {'class' : 'goods-name'}).get_text()
    
    print(name)