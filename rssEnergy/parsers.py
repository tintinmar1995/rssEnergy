from selenium.webdriver.common.by import By
import locale
import calendar
import datetime
import hashlib

def new_article(**kw):
    out = {k: kw.get(k, None) for k in [
        'category', 'image', 'link', 'title', 'author', 'description',
        'language', 'copyright', 'pubDate'
    ]}
    out['guid'] = hashlib.sha256(out['link'].encode()).hexdigest()
    return out

def parse_date(date_str, lang):
    locale.setlocale(locale.LC_ALL, lang)
    months = {calendar.month_name[month_idx].lower(): month_idx for month_idx in range(1, 13)}
    dt_parts = date_str.split(' ')
    dt_parts[0] = int(dt_parts[0])
    dt_parts[1] = months[dt_parts[1]]
    dt_parts[2] = int(dt_parts[2])
    dt_parts.reverse()
    return datetime.datetime(*dt_parts).strftime("%Y-%m-%d %H:%M:%S")

def scrape_articles(driver, url, container_class, article_class, lang, title_class, date_class, img_class, link_class, desc_class=None):
    driver.get(url)
    articlesContainer = driver.find_element(By.CLASS_NAME, container_class)
    articles = articlesContainer.find_elements(By.CLASS_NAME, article_class)

    parsedArticles = []
    for article in articles:
        img = article.find_element(By.TAG_NAME, img_class).get_property("src")
        title = article.find_element(By.CLASS_NAME, title_class).text
        dt = article.find_element(By.CLASS_NAME, date_class).text
        link = article.find_element(By.TAG_NAME, link_class).get_property('href')
        
        pubDate = parse_date(dt, lang)
        
        article_data = {
            'image': img,
            'pubDate': pubDate,
            'title': title,
            'link': link
        }
        
        if desc_class:
            desc = article.find_element(By.CLASS_NAME, desc_class).text
            article_data['description'] = desc
        
        parsedArticles.append(new_article(**article_data))

    driver.quit()
    return parsedArticles

def iea_news(driver):
    return scrape_articles(driver, "https://www.iea.org/news", 'o-layout__main', 'article', 'en_UK',
                           "m-news-detailed-listing__title", "m-news-detailed-listing__date", "img", "m-news-detailed-listing__link")

def rte_actualites(driver):
    return scrape_articles(driver, "https://www.rte-france.com/actualites", "result-container", "a", 'fr_FR',
                           "read-more-title", "file-date", "img")

def enedis_odte(driver, lang='fr_FR'):
    return scrape_articles(driver, "https://observatoire.enedis.fr/tous-les-articles", 
                           "views-infinite-scroll-content-wrapper", "views-row", lang,
                           "article-card__body__title", "article-card__body__date", "img", "a", "article-card__body__txt")
