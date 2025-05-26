# RSS Energy

RSS-Energy est un outil en cours de développement. Il permet de :

- Scraper les pages internet d'acteurs de l'énergie afin de collecter les liens vers les articles ;
- Constituer, gérer, afficher une base de données locale (fichiers yaml) ;
- Envoyer l'annuaire d'articles sur le web (e.g. pour constituer une flux RSS).

Every source in one channel :
- https://mmasson.fr/toolbox/rss-energy.php

Choose the channel you want : 
- https://mmasson.fr/toolbox/rss-energy.php?source_id=iea
- https://mmasson.fr/toolbox/rss-energy.php?source_id=rte-actualite

## Install 

- Python 3.13.3
- Selenium `pip install selenium`
- See requirements.txt

:warning Eviter la WSL (problème lier au GUI à résoudre sinon). Préférer Windows ou une distribution Linux plus classique, avec Firefox d'installé.

## A développer 

- CLI
- Catégorisation des articles
