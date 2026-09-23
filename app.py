# app.py

from pathlib import Path
import pandas as pd
import streamlit as st
import yaml


SCANNED_DIR = Path("scanned")


from pathlib import Path

import pandas as pd
import yaml

from rssEnergy import utils


@st.cache_data
def load_articles():

    articles = []

    for file in SCANNED_DIR.glob("*.yaml"):

        with open(file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        source_name = data.get("name", file.stem)
        source_url = data.get("url")
        source_img = data.get("img")

        # Sécurisation de l'URL du logo
        source_img = utils.ensure_url(
            url=source_url,
            suspected_uri=source_img,
        )

        for article in data.get("articles", []):

            article["source"] = source_name
            article["source_url"] = source_url
            article["source_img"] = source_img

            # URL absolue de l'article
            article["link"] = utils.ensure_url(
                url=source_url,
                suspected_uri=article.get("link"),
            )

            # URL absolue de l'image
            article["image"] = utils.ensure_url(
                url=source_url,
                suspected_uri=article.get("image"),
            )

            articles.append(article)

    df = pd.DataFrame(articles)

    if "pubDate" in df.columns:
        df["pubDate"] = pd.to_datetime(
            df["pubDate"],
            errors="coerce"
        )

    return df


st.set_page_config(
    page_title="Veille Energie",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Veille Energie")

df = load_articles()

if len(df) == 0:
    st.warning("Aucun article trouvé.")
    st.stop()

# ======================================================
# Sidebar
# ======================================================

with st.sidebar:

    st.header("Filtres")

    sources = sorted(df["source"].dropna().unique())

    selected_sources = st.multiselect(
        "Sources",
        options=sources,
        default=sources,
    )

    categories = sorted(df["category"].dropna().unique())

    selected_categories = st.multiselect(
        "Catégories",
        options=categories,
        default=categories,
    )

    search = st.text_input(
        "Recherche",
        placeholder="RTE, prix spot, flexibilité..."
    )

# ======================================================
# Filtrage
# ======================================================

filtered = df.copy()

filtered = filtered[
    filtered["source"].isin(selected_sources)
]

if selected_categories:
    filtered = filtered[
        filtered["category"].isin(selected_categories)
    ]

if search:

    mask = (
        filtered["title"]
        .fillna("")
        .str.contains(search, case=False)
    )

    mask |= (
        filtered["description"]
        .fillna("")
        .str.contains(search, case=False)
    )

    filtered = filtered[mask]

filtered = filtered.sort_values(
    "pubDate",
    ascending=False
)

# ======================================================
# Résumé
# ======================================================

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Articles",
        len(filtered)
    )

with col2:
    st.metric(
        "Sources",
        filtered["source"].nunique()
    )

st.divider()

# ======================================================
# Articles
# ======================================================

for idx, article in filtered.iterrows():

    with st.container():

        cols = st.columns([1, 4])

        with cols[0]:

            if article.get("image"):
                st.image(article["image"], use_container_width=True)

        with cols[1]:

            st.subheader(article["title"])

            st.caption(
                f"{article['source']} | "
                f"{article['pubDate'].strftime('%d/%m/%Y')}"
            )

            if pd.notna(article.get("category")):
                st.markdown(
                    f"**Catégorie :** "
                    f"{article['category'].strip()}"
                )

            if pd.notna(article.get("description")):
                st.write(article["description"])

            st.link_button(
                "📖 Ouvrir l'article",
                article["link"]
            )

        st.divider()
