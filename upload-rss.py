import requests
import yaml
import os

with open('./config.yaml', encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
    url = cfg['url']
    usr = cfg['usr']
    pwd = cfg['pwd']

with open('./feeds.yaml', encoding="utf-8") as f:
    feeds = yaml.safe_load(f)

for feed, args in feeds.items():
    if args.get('enabled', False):
        
        with open(os.path.join('./scanned', feed + '.yaml'), 'r', encoding='utf-8') as f:
            articles = yaml.safe_load(f)

        for a in articles['articles']:
            a['pubDate'] = a['pubDate'].strftime("%Y-%m-%d %H:%M:%S")
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
        print("Statut de la réponse:", response.status_code)
        print("Contenu de la réponse:", response.content)

    else:
        print(args.get('name', feed), ': Disabled !')
