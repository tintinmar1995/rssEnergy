import requests
import json
import ddgs
import yaml 

from rssEnergy import parsers


queries = {
    'stations de transfert énergie par pompage': 'EnR',
    'orano framatome rosatome CNNC CGN SPIC Huaneng' : 'Nucléaire',
    'epr Flamanville': 'Nucléaire, EPR',
    'electricite hydrogene': 'H2, EnR',
    'electricite rte france': 'RTE',
    'electricite lesechos.fr': None,
    "agence internationale énergie -atomique -aiea": None,
    'data center france': "Nouveaux usages",
    'stockage électrique batterie': 'Stockage',
    'prix spot négatif énergie': 'EPEX-Spot',
    'EPEX Spot': 'EPEX-Spot',
    'marché de gros electricite': 'EPEX-Spot',
    "prix de l'électricité": 'EPEX-Spot',
    'production photovoltaïque éolien': 'PV, Eole, EnR',
    'production énergie solaire': 'PV, Eole, EnR',
    'production énergie éolienne': 'PV, Eole, EnR',
    'agrivoltaisme france': 'PV, EnR'
}

with open('./config.yaml', encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
    url = cfg['url']
    usr = cfg['usr']
    pwd = cfg['pwd']
    proxy = cfg.get('proxy', None)

feed = "ddgs"

proxies = None
if proxy is not None:
    proxies = {'http': proxy, 'https': proxy}

for q in queries:

    data = {
        # TODO: Also search news with Google News
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
