import requests
import json
import ddgs
import yaml 

from rssEnergy import parsers


with open('./config/search-queries.yaml', encoding="utf-8") as f:
    queries = yaml.safe_load(f)
    queries = {k['q']: k['tag'] for k in queries}


with open('./config/credentials.yaml', encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
    url = cfg['url']
    usr = cfg['usr']
    pwd = cfg['pwd']
    proxy = cfg.get('proxy', None)


proxies = None
if proxy is not None:
    proxies = {'http': proxy, 'https': proxy}


feed = "ddgs"
for q in queries:

    data = {
        "articles": parsers.duck(q, queries[q], proxy),
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
