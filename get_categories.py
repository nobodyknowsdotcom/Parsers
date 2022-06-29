import pickle
import json
import time
import requests
import pickle

def expand_catalog(full_catalog):
    result = {}

    for category in full_catalog:

        try:
            if category['childs']:
                result.update(expand_catalog(category['childs']))
            else:
                result[category['query']] = category['seo']
        except KeyError:
            try:
                result[category['query']] =  category['seo']
            except KeyError:
                try:
                    result[category['query']] =  category['name']
                except KeyError:
                    print(category)
    return result

r = requests.get('https://www.wildberries.ru/webapi/menu/main-menu-ru-ru.json')
categories = expand_catalog(r.json())
print(len(categories))

with open('categories.pickle', 'wb') as handle:
    pickle.dump(categories, handle, protocol=pickle.HIGHEST_PROTOCOL)