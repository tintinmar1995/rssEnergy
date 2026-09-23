import math
import re
import unicodedata

import numpy as np

from datetime import datetime, timezone
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

from .dataclasses import Article, TrendingTopic


FRENCH_STOP_WORDS = {
    "a", "afin", "ai", "ainsi", "alors", "apres", "au", "aucun",
    "aucune", "aussi", "autre", "aux", "avec", "avoir", "ce", "ces",
    "cet", "cette", "comme", "comment", "dans", "de", "des", "du",
    "elle", "en", "encore", "est", "et", "etre", "fait", "font",
    "il", "ils", "je", "la", "le", "les", "leur", "leurs", "lui",
    "mais", "mes", "moi", "moins", "mon", "ne", "nos", "notre",
    "nous", "on", "ont", "ou", "par", "pas", "plus", "pour",
    "pourquoi", "quand", "que", "quel", "quelle", "quelles", "quels",
    "qui", "sa", "sans", "se", "ses", "si", "son", "sont", "sur",
    "ta", "tes", "toi", "ton", "tous", "tout", "toute", "toutes",
    "tres", "tu", "un", "une", "vos", "votre", "vous",
    "actualite", "actualites", "article", "articles"
}


def normalize_text(value: object) -> str:
    """
    Nettoie une valeur textuelle.

    Gère notamment :
    - None ;
    - pd.NA et np.nan ;
    - les chaînes vides ;
    - les accents ;
    - les caractères spéciaux.
    """
    if value is None:
        return ""

    try:
        import pandas as pd

        if pd.isna(value):
            return ""
    except (ImportError, TypeError, ValueError):
        pass

    text = str(value).strip().lower()

    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^a-z0-9À-ÿ\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def article_to_text(article: Article) -> str:
    """
    Construit le texte analysé.

    Le titre est répété afin de lui donner davantage de poids
    que la description.
    """
    title = normalize_text(article.title)
    description = normalize_text(article.description)

    return f"{title} {title} {description}".strip()


def ensure_utc(value: datetime) -> datetime:
    """
    Convertit une date en date UTC.

    Une date sans fuseau horaire est considérée comme UTC.
    """
    value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def get_cluster_keywords(
    matrix,
    feature_names: np.ndarray,
    article_indexes: list[int],
    number: int = 5,
) -> list[str]:
    """
    Extrait les mots ou expressions ayant le poids TF-IDF moyen
    le plus élevé dans un groupe.
    """
    cluster_matrix = matrix[article_indexes]
    average_scores = np.asarray(cluster_matrix.mean(axis=0)).ravel()

    sorted_indexes = average_scores.argsort()[::-1]

    return [
        feature_names[index]
        for index in sorted_indexes
        if average_scores[index] > 0
    ][:number]


def compute_trending_score(
    articles: list[Article],
    now: datetime,
    freshness_hours: float = 48.0,
) -> float:
    """
    Calcule un score combinant :

    - le nombre d'articles ;
    - le nombre de sources distinctes ;
    - la récence des articles.

    La récence décroît exponentiellement.
    """
    source_count = len({article.source_name for article in articles})

    freshness_scores = []

    for article in articles:
        published_at = ensure_utc(article.pub_date)

        article_age_hours = max(
            0.0,
            (now - published_at).total_seconds() / 3600,
        )

        freshness = math.exp(
            -article_age_hours / freshness_hours
        )

        freshness_scores.append(freshness)

    average_freshness = (
        sum(freshness_scores) / len(freshness_scores)
        if freshness_scores
        else 0.0
    )

    volume_score = math.log1p(len(articles))
    diversity_score = math.log1p(source_count)

    return round(
        volume_score
        * diversity_score
        * average_freshness,
        4,
    )


def detect_trending_topics(
    articles: list[Article],
    minimum_articles: int = 2,
    similarity_threshold: float = 0.35,
    maximum_topics: int = 10,
) -> list[TrendingTopic]:
    """
    Détecte les sujets du moment à partir des titres et descriptions.

    Parameters
    ----------
    articles
        Articles à analyser.

    minimum_articles
        Nombre minimum d'articles nécessaires pour créer un sujet.

    similarity_threshold
        Similarité minimale approximative entre deux articles.

        Une valeur élevée crée des groupes plus stricts.
        Une valeur faible crée des groupes plus larges.

    maximum_topics
        Nombre maximal de sujets retournés.
    """
    valid_articles = [
        article
        for article in articles
        if article_to_text(article)
    ]

    if len(valid_articles) < minimum_articles:
        return []

    texts = [
        article_to_text(article)
        for article in valid_articles
    ]

    vectorizer = TfidfVectorizer(
        stop_words=list(FRENCH_STOP_WORDS),
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.90,
        max_features=10_000,
        sublinear_tf=True,
    )

    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return []

    # Avec une distance cosinus :
    # distance = 1 - similarité.
    epsilon = 1.0 - similarity_threshold

    clustering = DBSCAN(
        eps=epsilon,
        min_samples=minimum_articles,
        metric="cosine",
    )

    labels = clustering.fit_predict(matrix)
    feature_names = vectorizer.get_feature_names_out()

    now = datetime.now(timezone.utc)
    topics = []

    for cluster_id in sorted(set(labels)):
        # -1 représente les articles considérés comme isolés.
        if cluster_id == -1:
            continue

        article_indexes = [
            index
            for index, label in enumerate(labels)
            if label == cluster_id
        ]

        cluster_articles = [
            valid_articles[index]
            for index in article_indexes
        ]

        keywords = get_cluster_keywords(
            matrix=matrix,
            feature_names=feature_names,
            article_indexes=article_indexes,
            number=5,
        )

        if not keywords:
            continue

        source_count = len({
            article.source_name
            for article in cluster_articles
        })

        topics.append(
            TrendingTopic(
                label=" · ".join(keywords[:3]),
                keywords=keywords,
                articles=sorted(
                    cluster_articles,
                    key=lambda article: ensure_utc(
                        article.pub_date
                    ),
                    reverse=True,
                ),
                score=compute_trending_score(
                    articles=cluster_articles,
                    now=now,
                ),
                source_count=source_count,
            )
        )

    return sorted(
        topics,
        key=lambda topic: topic.score,
        reverse=True,
    )[:maximum_topics]