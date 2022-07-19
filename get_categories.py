import pickle
import requests
import pickle

def expand_catalog(full_catalog, prefix=''):
    result = {}

    for category in full_catalog:
        try:
            if category['childs']:
                try:
                    if prefix == '':
                        result.update(expand_catalog(category['childs'], category['seo']))
                    else:
                        result.update(expand_catalog(category['childs'], prefix + '/' + category['seo']))
                except KeyError:
                    if prefix == '':
                        result.update(expand_catalog(category['childs'], category['name']))
                    else:
                        result.update(expand_catalog(category['childs'], prefix + '/' + category['name']))
            else:
                result[category['query']] = prefix + '/' + category['seo']
        except KeyError:
            try:
                result[category['query']] =  prefix + '/' + category['seo']
            except KeyError:
                try:
                    result[category['query']] =  prefix + '/' + category['name']
                except KeyError:
                    print(category)
    return result

r = requests.get('https://www.wildberries.ru/webapi/menu/main-menu-ru-ru.json')
categories = expand_catalog(r.json())
for (key, val) in categories.items():
    print(key, val)

print(len(categories))

with open('categories.pickle', 'wb') as handle:
    pickle.dump(categories, handle, protocol=pickle.HIGHEST_PROTOCOL)