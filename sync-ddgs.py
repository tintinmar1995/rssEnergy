import requests
import json
import ddgs
import yaml 

from rssEnergy import parsers

queries = [
    # 'electricite hydrogene',
    'electricite rte france',
    'électricité site:lesechos.fr'
]

with open('./config.yaml', encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
    url = cfg['url']
    usr = cfg['usr']
    pwd = cfg['pwd']
    proxy = cfg.get('proxy', 'None')

engine = ddgs.DDGS(proxy=proxy, verify=False)
feed = "ddgs"

proxies = None
if proxy is not None:
    proxies = {'http': proxy, 'https': proxy}

for q in queries:
    articles = engine.news(q)
    articles = [
        parsers.new_article(
            category=None,
            image=a['image'],
            link=a['url'],
            title=a['title'],
            author=a['source'],
            source_id=a['source'],
            description=a['body'],
            language='None',
            copyright=a['date'],
            pubDate=a['date'])
        for a in articles
    ]

    data = {
        "articles": articles,
        "source_name": "ddgs",
        "source_url": "https://duckduckgo.com",
        "source_image_url": ""
    }

    # Envoi de la requête POST
    response = requests.post(
        url + feed, json=data,
        auth=requests.auth.HTTPBasicAuth(usr, pwd),
        proxies=proxies
    )

    # Affichage de la réponse
    status = response.status_code
    response = json.loads(response.content.decode())
    print('->', status, response['message'])
    print('-> Insertion ', response['inserted'])
    print('-> Existing ', response['existing'], '\n')
