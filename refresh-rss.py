import yaml
import os

from rssEnergy import driver, parsers

with open('./feeds.yaml', encoding="utf-8") as f:
    feeds = yaml.safe_load(f)

drv = driver.get_driver()

os.makedirs('./scanned', exist_ok=True)

for feed, args in feeds.items():
    if args.get('enabled', True):
        print(args.get('name', feed), ': Scanning..')
        articles = {
            'img': args['img'],
            'name' : args['name'],
            'url': args['url'],
            'articles': getattr(parsers, args['parsers'])(drv)
        }

        with open(os.path.join('./scanned', feed + '.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(articles, f)

    else:
        print(args.get('name', feed), ': Disabled !')

