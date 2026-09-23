from rssEnergy.utils import remove_duplicates
from rssEnergy.dataclasses import load_articles

from rssEnergy.topic import detect_trending_topics

from pathlib import Path 

SCANNED_DIR = Path("scanned")

articles = load_articles(SCANNED_DIR)

unique_articles = remove_duplicates(
    articles,
    "guid"
)

topics = detect_trending_topics(
    unique_articles,
    minimum_articles=2,
    similarity_threshold=0.35,
)

for topic in topics:
    print(
    f"\n{topic.label} "
    f"| score={topic.score} "
    f"| articles={len(topic.articles)} "
    f"| sources={topic.source_count} \n"
    )
    
    for article in topic.articles:
        print(
        f" - [{article.source_name}] "
        f"{article.title}"
        )