from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class Feed:
    id: str
    enabled: bool
    name: str
    url: str
    img: Optional[str] = None
    parser: Optional[str] = None
    debug: Optional[str] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data.pop("id")

        # suppression des champs None pour retrouver la structure YAML
        return {k: v for k, v in data.items() if v is not None}


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
    