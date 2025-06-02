from selenium.webdriver.common.by import By

import locale
import calendar
import datetime
import hashlib

def new_article(**kw):
    out =  {k: kw.get(k, None) for k in [
        'category', 'image', 'link', 'title', 'author', 'description',
        'language', 'copyright', 'pubDate'
    ]}

    out['guid'] = hashlib.sha256(out['link'].encode()).hexdigest()
    return out
 
def iea_news(driver):

    driver.get("https://www.iea.org/news")

    articlesContainer = driver.find_element(By.CLASS_NAME, 'o-layout__main')
    articles = articlesContainer.find_elements(By.TAG_NAME, "article")

    parsedArticles = list()
    for article in articles:
        
        tag = article.find_element(By.CLASS_NAME, "a-tag-small").text
        try:
            img = article.find_element(By.TAG_NAME, "img").get_property("src")
        except:
            img = None
        title = article.find_element(By.CLASS_NAME, "m-news-detailed-listing__title").text
        dt = article.find_element(By.CLASS_NAME, "m-news-detailed-listing__date").text
        
        link = article.find_element(By.CLASS_NAME, "m-news-detailed-listing__link").get_property('href')

        locale.setlocale(locale.LC_ALL, 'en_UK')
        dt = datetime.datetime.strptime(dt, "%d %B %Y").strftime("%Y-%m-%d %H:%M:%S")

        parsedArticles.append(new_article(
            category=tag, image=img, pubDate=dt, title=title, link=link
        ))

    return parsedArticles


def cre_actualites(driver, lang="fr-FR"):

    driver.get("https://www.cre.fr/actualites/toute-lactualite.html")
    driver.find_element(By.CLASS_NAME, "orejime-Notice-saveButton").click()

    articlesContainer = driver.find_element(By.ID, "tx-solr-results")
    articles = articlesContainer.find_elements(By.TAG_NAME, "li")

    parsedArticles = list()
    for article in articles:

        img = article.find_element(By.TAG_NAME, "img").get_property("src")
        title = article.find_element(By.CLASS_NAME, "card-title")
        link = title.find_element(By.TAG_NAME, "a").get_property('href')
        title = title.text
        desc = title
        tag = article.find_element(By.CLASS_NAME, "card-labels").text.replace(' ', '/')

        try:
            dt = article.find_element(By.TAG_NAME, "time").text.split('/')
            dt.reverse()
            dt = datetime.datetime(*[
                int(i) for i in dt if len(i) > 0
            ]).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            dt = None

        parsedArticles.append(new_article(
            image=img, pubDate=dt, title=title,
            link=link, description=desc, language=lang,
            category=tag
        ))     

    return parsedArticles


def rte_actualites(driver):

    locale.setlocale(locale.LC_ALL, 'fr_FR')
    months = {
        calendar.month_name[month_idx].upper():
        month_idx for month_idx in range(1,13)
    }

    driver.get("https://www.rte-france.com/actualites")

    articlesContainer = driver.find_element(By.CLASS_NAME, "result-container")
    articles = articlesContainer.find_elements(By.TAG_NAME, "a")

    parsedArticles = list()
    for article in articles:
        img = article.find_element(By.TAG_NAME, "img")
        title = article.find_element(By.CLASS_NAME, "read-more-title")

        dt = article.find_element(By.CLASS_NAME, "file-date").text.split(' ')
        dt[0] = int(dt[0])
        dt[1] = months[dt[1]]
        dt[2] = int(dt[2])
        dt.reverse()
        dt = datetime.datetime(*dt).strftime("%Y-%m-%d %H:%M:%S")

        parsedArticles.append(new_article(
            image=img.get_property("src"), pubDate=dt,
            title=title.text, link=article.get_property('href')
        ))

    return parsedArticles


def enedis_odte(driver, lang = 'fr_FR'):

    locale.setlocale(locale.LC_ALL, lang)
    months = {
        calendar.month_name[month_idx].lower():
        month_idx for month_idx in range(1,13)
    }

    driver.get("https://observatoire.enedis.fr/tous-les-articles")

    articlesContainer = driver.find_element(By.CLASS_NAME, "views-infinite-scroll-content-wrapper")
    articles = articlesContainer.find_elements(By.CLASS_NAME, "views-row")

    parsedArticles = list()
    for article in articles:

        img = article.find_element(By.TAG_NAME, "img")
        link = article.find_element(By.TAG_NAME, "a")
        title = article.find_element(By.CLASS_NAME, "article-card__body__title").text

        dt = article.find_element(By.CLASS_NAME, "article-card__body__date").text.split(' ')
        dt[0] = int(dt[0])
        dt[1] = months[dt[1]]
        dt[2] = int(dt[2])
        dt.reverse()
        dt = datetime.datetime(*dt).strftime("%Y-%m-%d %H:%M:%S")

        desc = article.find_element(By.CLASS_NAME, "article-card__body__txt").text

        parsedArticles.append(new_article(
            image=img.get_property("src"), pubDate=dt,
            title=title, link=link.get_property('href'),
            description=desc, language=lang
        ))

    return parsedArticles
