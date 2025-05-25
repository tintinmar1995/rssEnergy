from selenium.webdriver.common.by import By

import locale
import calendar
import datetime

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
        
        locale.setlocale(locale.LC_ALL, 'en_UK')
        dt = datetime.datetime.strptime(dt, "%d %B %Y")

        parsedArticles.append({
            "tag": tag, "img": img, "datetime": dt, "title": title
        })

    driver.quit()

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
        dt = datetime.datetime(*dt)

        parsedArticles.append({
            "img": img.get_property("src"),
            "datetime": dt,
            "title": title.text
        })

    driver.quit()

    return parsedArticles
