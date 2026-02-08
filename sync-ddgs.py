import requests
import json
import yaml 

from rssEnergy import parsers, utils


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

    status, response = utils.push_articles(url, feed, data, usr, pwd, proxies)
    utils.push_results(status, response)
