import requests
import yaml
import os
import json

from rssEnergy import utils

with open('./config.yaml', encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
    url = cfg['url']
    usr = cfg['usr']
    pwd = cfg['pwd']

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
        response = requests.post(url + feed, json=data, auth=requests.auth.HTTPBasicAuth(usr, pwd))

        # Affichage de la réponse
        status = response.status_code
        response = json.loads(response.content.decode())
        print('->', status, response['message'])
        print('-> Insertion ', response['inserted'])
        print('-> Existing ', response['existing'], '\n')

    else:
        print(args.get('name', feed), ': Disabled!\n')
