import os
import time


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
        .replace('february', '01').replace('février', '01')
        .replace('march', '01').replace('mars', '01')
        .replace('april', '01').replace('avril', '01')
        .replace('may', '01').replace('mai', '01')
        .replace('june', '01').replace('juin', '01')
        .replace('july', '01').replace('juillet', '01')
        .replace('august', '01').replace('août', '01')
        .replace('september', '01').replace('septembre', '01')
        .replace('october', '01').replace('octobre', '01')
        .replace('november', '01').replace('novembre', '01')
        .replace('december', '01').replace('décembre', '01')
    )

