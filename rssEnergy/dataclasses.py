from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import yaml
import datetime

from . import utils, parsers


@dataclass
class Feed:
    id: str
    name: str
    url: str
    enabled: bool = False
    img: Optional[str] = None
    parser: Optional[str] = None
    debug: Optional[str] = None

    @property
    def dump_file(self):
        return utils.path_dump_articles(self.id)

    def to_dict(self) -> dict:
        data = asdict(self)
        data.pop("id")

        # suppression des champs None pour retrouver la structure YAML
        return {k: v for k, v in data.items() if v is not None}

    def sync(self, proxy):
        if not hasattr(parsers, self.parser):
            raise ValueError(
                f"Parser inconnu : {self.parser}"
            )
        return getattr(parsers, self.parser)(proxy)

    def load_articles(self):
        with open(self.dump_file, encoding="utf-8") as f:
            articles = yaml.safe_load(f)
        return articles


@dataclass
class Article:
    guid: str
    title: str
    description: Optional[str]
    category: Optional[str]
    author: Optional[str]
    language: Optional[str]
    pub_date: Optional[str]

    image: Optional[str]
    link: Optional[str]

    source_name: str
    source_url: str
    source_img: Optional[str]


@dataclass
class TrendingTopic:
    label: str
    keywords: list[str]
    articles: list[Article]
    score: float
    source_count: int


def load_feeds(yaml_file: str | Path, only_enabled: bool = False) -> list[Feed]:
    """
    Charge un fichier YAML et retourne une liste de Feed.

    Parameters
    ----------
    yaml_file : str | Path
        Chemin vers le fichier YAML.
    only_enabled : bool
        Si True, ne retourne que les feeds activés.

    Returns
    -------
    list[Feed]
    """
    with open(yaml_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    feeds = []

    for feed_id, feed_config in config.items():

        feed = Feed(
            id=feed_id,
            enabled=feed_config.get("enabled", False),
            name=feed_config.get("name", feed_id),
            url=feed_config["url"],
            img=feed_config.get("img"),
            parser=feed_config.get("parsers"),
            debug=feed_config.get("debug"),
        )

        if not only_enabled or feed.enabled:
            feeds.append(feed)

    return feeds


def load_articles(scanned_dir: str = "scanned") -> list[Article]:
    """
    Charge tous les articles contenus dans les fichiers YAML du dossier scanned.
    """

    articles = []

    for file in Path(scanned_dir).glob("*.yaml"):

        with open(file, "r", encoding="utf-8") as f:
            feed = yaml.safe_load(f)

        source_name = feed.get("name")
        source_url = feed.get("url")
        source_img = feed.get("img")

        for item in feed.get("articles", []):

            articles.append(
                Article(
                    guid=item.get("guid"),
                    title=item.get("title"),
                    description=item.get("description"),
                    category=item.get("category"),
                    author=item.get("author"),
                    language=item.get("language"),
                    pub_date=item.get("pubDate"),
                    image=utils.ensure_url(
                        url=source_url,
                        suspected_uri=item.get("image"),
                    ),
                    link=utils.ensure_url(
                        url=source_url,
                        suspected_uri=item.get("link"),
                    ),
                    source_name=source_name,
                    source_url=source_url,
                    source_img=utils.ensure_url(
                        url=source_url,
                        suspected_uri=source_img,
                    ),
                )
            )

    return articles
