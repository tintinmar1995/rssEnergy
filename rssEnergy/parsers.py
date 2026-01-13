import bs4
import requests
import calendar
import datetime
import hashlib
import ddgs

from . import utils


def new_article(**kw):
    out =  {k: kw.get(k, None) for k in [
        'category', 'image', 'link', 'title', 'author', 'description',
        'language', 'copyright', 'pubDate'
    ]}

    out['guid'] = hashlib.sha256(out['link'].encode()).hexdigest()
    return out


def duck(q, tags, proxy):
    engine = ddgs.DDGS(proxy=proxy, verify=False)

    print(q)
    try:
        articles = engine.news(q)
        articles = [
            new_article(
                category=tags,
                image=a['image'],
                link=a['url'],
                title=a['title'],
                author=a['source'],
                source_id=a['source'],
                description='(' + a['source'] + ") " + a['body'],
                language='None',
                copyright=a['source'],
                pubDate=a['date'])
            for a in articles if not a['url'].startswith('https://www.msn.com')
        ]

    except ddgs.exceptions.DDGSException:
        print('No result for query : ', q, '\n')
        articles = list()
    
    return articles


def iea_news(proxy=None):

    proxies = None
    if proxy is not None:
        proxies = {'http': proxy, 'https': proxy}

    response = requests.get("https://www.iea.org/news", proxies=proxies)
    page = bs4.BeautifulSoup(response.text, 'html5lib')
    articles = page.find_all('a', {'class': 'm-news-detailed-listing__link'})
    parsedArticles = list()
    for article in articles:
        try:
            link = article.attrs['href']
            tag = [s.text.replace('\n', '').replace(' ', '') for s in article.find_all('span', {'class': 'a-tag-small'})][0]
            img = article.find('img').attrs['src']
            dt = article.find('div', {'class': 'm-news-detailed-listing__date'}).text.strip()
            title = article.find("h5", {'class': "m-news-detailed-listing__title"}).span.text
            dt = datetime.datetime.strptime(utils.replace_month(dt), "%d %m %Y").strftime("%Y-%m-%d %H:%M:%S")
            parsedArticles.append(new_article(
                category=tag, image=img, pubDate=dt, title=title, link=link
            ))
        except Exception:
            pass

    return parsedArticles


def cre_actualites(proxy=None):

    lang="fr-FR"
    proxies = None
    if proxy is not None:
        proxies = {'http': proxy, 'https': proxy}

    response = requests.get("https://www.cre.fr/actualites/toute-lactualite.html", proxies=proxies)
    page = bs4.BeautifulSoup(response.text, 'html5lib')
    articles = page.find('ul', {'id': "tx-solr-results"}).find_all('li')
    parsedArticles = list()
    for article in articles:
        img = article.find('img').attrs['src']
        link = article.find('h3', {'class': 'card-title'}).a.attrs['href']
        title = article.find('h3', {'class': 'card-title'}).a.text
        desc = title
        tag = "/".join([s.text for s in article.find_all('span', {'class': 'label'})])
        dt = [int(i) for i in article.find('time').text.strip().split('/')]
        dt.reverse()
        dt = datetime.datetime(*dt).strftime("%Y-%m-%d %H:%M:%S")
        parsedArticles.append(new_article(
            image=img, pubDate=dt, title=title,
            link=link, description=desc, language=lang,
            category=tag
        ))     

    return parsedArticles


def rte_actualites(proxy=None):

    months = {
        calendar.month_name[month_idx].upper():
        month_idx for month_idx in range(1,13)
    }

    proxies = None
    if proxy is not None:
        proxies = {'http': proxy, 'https': proxy}
        
    response = requests.get("https://www.rte-france.com/actualites", proxies=proxies)
    page = bs4.BeautifulSoup(response.text, 'html5lib')
    articles = page.find('div', {'class': "result-container"})
    parsedArticles = list()
    for article in articles:
        break 
        img = article.find('img').attrs['src']
        link = article.find('h3', {'class': 'card-title'}).a.attrs['href']
        title = article.find('h3', {'class': 'card-title'}).a.text
        desc = title
        tag = "/".join([s.text for s in article.find_all('span', {'class': 'label'})])
        parsedArticles.append(new_article(
            image=img, pubDate=dt, title=title,
            link=link, description=desc, language=lang,
            category=tag
        ))

    return parsedArticles


def enedis_odte(proxy):

    proxies = None
    if proxy is not None:
        proxies = {'http': proxy, 'https': proxy}

    lang = 'fr_FR'
    months = {
        calendar.month_name[month_idx].lower():
        month_idx for month_idx in range(1,13)
    }

    response = requests.get("https://observatoire.enedis.fr/tous-les-articles", proxies=proxies)
    page = bs4.BeautifulSoup(response.text, 'html5lib')
    articles = page.find('div', {'class': "views-row"})
    parsedArticles = list()
    for article in articles:

        try:

            img = article.find('img').attrs['src']
            link = articles.find('a').attrs['href']
            title = article.find('span', {'class': 'field--name-title'}).text    
            desc = article.find('div', {'class': 'article-card__body__txt'}).text
            tag = article.find('div', {'class': 'field--name-field-page-thematique'}).text

            dt = article.find('p', {'class': "article-card__body__date"}).text.split(' ')
            dt[0] = int(dt[0])
            dt[1] = months[dt[1]]
            dt[2] = int(dt[2])
            dt.reverse()
            dt = datetime.datetime(*dt).strftime("%Y-%m-%d %H:%M:%S")

            parsedArticles.append(new_article(
                image=img, pubDate=dt, title=title, link=link, description=desc, language=lang
            ))
        
        except Exception:
            pass

    return parsedArticles


def sdes(proxy=None):

    proxies = None
    if proxy is not None:
        proxies = {'http': proxy, 'https': proxy}

    lang="fr-FR"
    response = requests.get("https://www.statistiques.developpement-durable.gouv.fr/actualites", proxies=proxies)
    page = bs4.BeautifulSoup(response.text, 'html5lib')
    articles = page.find_all('article', {'role': "article"})
    parsedArticles = list()
    for article in articles:
        try:
            img = article.find('img')
            if img is None:
                # il n'y a pas tout le temps d'image
                img = ''
            else:
                img = img.attrs['src']

            link = article.find('a', {'rel': 'bookmark'}).attrs['href']
            title = article.find('span').text 
            desc = article.find("div", {'class': 'accroche'})
            
            if desc is None:
                # il n'y pas tout le temps de description
                desc = ''
            else:
                desc = desc.find("div", {'class': 'field--item'}).text
            
            tag = article.find("div", {'class': 'field--item'}).text

            dt = article.find("div", {'class': 'date'}).text
            dt = datetime.datetime.strptime(dt, "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
            parsedArticles.append(new_article(
                category=tag, image=img, pubDate=dt, title=title, link=link,
                description=desc, language=lang, author="SDES"
            ))

        except Exception as err:
            pass

    return parsedArticles
