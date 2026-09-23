from pathlib import Path
import logging
import yaml

from rssEnergy import parsers, utils, feed


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

CONFIG_DIR = Path("config")
CREDENTIALS_FILE = CONFIG_DIR / "credentials.yaml"
RSS_FEEDS_FILE = CONFIG_DIR / "rss-feeds.yaml"
SCANNED_DIR = Path("scanned")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Scan RSS feeds
# -----------------------------------------------------------------------------

def scan_feeds(feeds: dict, proxy: str | None) -> None:
    """
    Récupère les articles des flux RSS et les stocke
    localement sous forme YAML.
    """

    SCANNED_DIR.mkdir(exist_ok=True)

    for feed_id, config in feeds.items():

        feed_name = config.get("name", feed_id)

        if not config.get("enabled", False):
            logger.info("%s : désactivé", feed_name)
            continue

        scan_file = SCANNED_DIR / f"{feed_id}.yaml"

        if utils.is_file_modified_recently(scan_file):
            logger.info("%s : scan récent, ignoré", feed_name)
            continue

        try:
            utils.validate_feed(feed_id, config)

            parser_name = config["parser"]

            if not hasattr(parsers, parser_name):
                raise ValueError(
                    f"Parser inconnu : {parser_name}"
                )

            logger.info("%s : scan en cours", feed_name)

            parser = getattr(parsers, parser_name)

            articles = {
                "img": config.get("img"),
                "name": config["name"],
                "url": config["url"],
                "articles": parser(proxy)
            }

            logger.info(
                "%s : %s article(s) trouvé(s)",
                feed_name,
                len(articles["articles"])
            )

            with open(
                utils.path_dump_articles(feed_id),
                "w",
                encoding="utf-8"
            ) as f:
                yaml.safe_dump(
                    articles,
                    f,
                    allow_unicode=True,
                    sort_keys=False
                )

        except Exception:
            logger.exception(
                "Échec du scan du feed '%s'",
                feed_name
            )


# -----------------------------------------------------------------------------
# Push articles
# -----------------------------------------------------------------------------

def push_feeds(
    feeds: dict,
    url: str,
    usr: str,
    pwd: str,
    proxies: dict | None
) -> None:
    """
    Envoie les articles collectés vers l'API cible.
    """

    for feed_id, config in feeds.items():

        feed_name = config.get("name", feed_id)

        if not config.get("enabled", False):
            logger.info("%s : désactivé", feed_name)
            continue

        logger.info("%s : publication", feed_name)

        dump_file = utils.path_dump_articles(feed_id)

        if not Path(dump_file).exists():
            logger.warning(
                "%s : aucun fichier scanné trouvé",
                feed_name
            )
            continue

        with open(dump_file, encoding="utf-8") as f:
            articles = yaml.safe_load(f)

        # Suppression des doublons avant envoi
        unique_articles = utils.remove_duplicates(
            articles["articles"],
            "guid"
        )

        # Ajout de métadonnées communes
        for article in unique_articles:
            article["source_id"] = feed_id

        payload = {
            "articles": unique_articles,
            "source_name": articles["name"],
            "source_url": articles["url"],
            "source_image_url": articles["img"]
        }

        try:
            status, response = utils.push_articles(
                url,
                feed_id,
                payload,
                usr,
                pwd,
                proxies
            )

            utils.push_results(status, response)

        except Exception:
            logger.exception(
                "Échec de publication pour '%s'",
                feed_name
            )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:

    args = utils.parse_args()

    credentials = utils.load_yaml(CREDENTIALS_FILE)
    feeds = {f.id: f.to_dict() for f in feed.load_feeds(RSS_FEEDS_FILE)}

    url = credentials["url"]
    usr = credentials["usr"]
    pwd = credentials["pwd"]
    proxy = credentials.get("proxy")
    proxies = utils.build_proxies(proxy)

    scan_feeds(feeds, proxy)

    if not args.offline:
        push_feeds(feeds, url, usr, pwd, proxies)
    else:
        logger.info('(Mode offline) Insertion ignorée')


if __name__ == "__main__":
    main()
