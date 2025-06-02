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

def scrape_articles(driver, config):
    driver.get(config['source']['url'])
    articlesContainer = driver.find_element(By.CLASS_NAME, config['source']['container_class'])
    articles = articlesContainer.find_elements(By.CLASS_NAME, config['source']['article_class'])

    parsedArticles = []
    for article in articles:
        img = article.find_element(By.TAG_NAME, config['source']['img_class']).get_property("src")
        title = article.find_element(By.CLASS_NAME, config['source']['title_class']).text
        dt = article.find_element(By.CLASS_NAME, config['source']['date_class']).text
        link = article.find_element(By.TAG_NAME, config['source']['link_class']).get_property('href')
        
        pubDate = parse_date(dt, config['source']['lang'])
        
        parsedArticles.append(new_article(
            image=img,
            pubDate=pubDate,
            title=title,
            link=link
        ))

    driver.quit()
    return parsedArticles
