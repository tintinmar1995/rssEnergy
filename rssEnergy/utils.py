import os
import time
import json
import requests


def push_articles(url, feed, data, usr, pwd, proxies):
    # Envoi de la requête POST
    response = requests.post(
        url + feed, json=data,
        auth=requests.auth.HTTPBasicAuth(usr, pwd),
        proxies=proxies
    )

    # Affichage de la réponse
    status = response.status_code
    response = json.loads(response.content.decode())

    return status, response


def push_results(status, response):
    print('->', status, response['message'])
    print('-> Insertion ', response['inserted'])
    print('-> Existing ', response['existing'], '\n')


def path_dump_articles(feed):
    return os.path.join('./scanned', feed + '.yaml')


def is_file_modified_recently(file_path):
    # Vérifie si le fichier existe
    if not os.path.isfile(file_path):
        return False

    # Obtient le temps de modification du fichier
    modification_time = os.path.getmtime(file_path)
    
    # Obtient le temps actuel
    current_time = time.time()
    
    # Calcule la différence en heures
    hours_since_modification = (current_time - modification_time) / 3600
    
    # Renvoie True si le fichier a été modifié il y a moins de 6 heures
    return hours_since_modification <= 6


def remove_duplicates(dict_list, key):
    seen = set()
    unique_dicts = []

    for d in dict_list:
        if key in d:
            value = d[key]
            if value not in seen:
                seen.add(value)
                unique_dicts.append(d)

    return unique_dicts


def replace_month(s):
    return (
        s
        .lower()
        .replace('january', '01').replace('janvier', '01')
        .replace('february', '02').replace('février', '02')
        .replace('march', '03').replace('mars', '03')
        .replace('april', '04').replace('avril', '04')
        .replace('may', '05').replace('mai', '05')
        .replace('june', '06').replace('juin', '06')
        .replace('july', '07').replace('juillet', '07')
        .replace('august', '08').replace('août', '08')
        .replace('september', '09').replace('septembre', '09')
        .replace('october', '10').replace('octobre', '10')
        .replace('november', '11').replace('novembre', '11')
        .replace('december', '12').replace('décembre', '12')
    )

