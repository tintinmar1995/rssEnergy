import yaml
import os
import time

from rssEnergy import driver, parsers, utils

with open('./feeds.yaml', encoding="utf-8") as f:
    feeds = yaml.safe_load(f)

drv = driver.get_driver()

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
                'articles': scrape_articles(driver, args)
            }

            with open(os.path.join('./scanned', feed + '.yaml'), 'w', encoding='utf-8') as f:
                yaml.dump(articles, f)

    else:
        print(args.get('name', feed), ': Disabled !')

