import yaml
import os
import time
import requests
import json

from rssEnergy import parsers, utils

with open('./config.yaml', encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
    url = cfg['url']
    usr = cfg['usr']
    pwd = cfg['pwd']
    proxy = cfg.get('proxy', None)

with open('./feeds.yaml', encoding="utf-8") as f:
    feeds = yaml.safe_load(f)

os.makedirs('./scanned', exist_ok=True)

for feed, args in feeds.items():
    if args.get('enabled', False):

        if utils.is_file_modified_recently(os.path.join('./scanned', feed + '.yaml')):
            print(args.get('name', feed), ': Skipped!')   

        else:
            print(args.get('name', feed), ': Scanning..')
            articles = {
                'img': args.get('img', None),
                'name' : args['name'],
                'url': args['url'],
                'articles': getattr(parsers, args['parsers'])(proxy)
            }

            with open(os.path.join('./scanned', feed + '.yaml'), 'w', encoding='utf-8') as f:
                yaml.dump(articles, f)

    else:
        print(args.get('name', feed), ': Disabled !')

proxies = None
if proxy is not None:
    proxies = {'http': proxy, 'https': proxy}

with open('./feeds.yaml', encoding="utf-8") as f:
    feeds = yaml.safe_load(f)

os.makedirs('./scanned', exist_ok=True)
for feed, args in feeds.items():
    if args.get('enabled', False):
        print(args.get('name', feed), '...')

        with open(os.path.join('./scanned', feed + '.yaml'), 'r', encoding='utf-8') as f:
            articles = yaml.safe_load(f)

        articles['articles'] = utils.remove_duplicates(articles['articles'], "guid")

        for a in articles['articles']:
            a['pubDate'] = a['pubDate']
            a['source_id'] = feed

        data = {
            "articles": articles['articles'],
            "source_name": articles['name'],
            "source_url": articles['url'],
            "source_image_url": articles['img']
        }

        # Envoi de la requête POST
        response = requests.post(
            url + feed, json=data,
            proxies=proxies,
            auth=requests.auth.HTTPBasicAuth(usr, pwd)
        )

        # Affichage de la réponse
        status = response.status_code
        response = json.loads(response.content.decode())
        print('->', status, response['message'])
        print('-> Insertion ', response['inserted'])
        print('-> Existing ', response['existing'], '\n')

    else:
        print(args.get('name', feed), ': Disabled!\n')

