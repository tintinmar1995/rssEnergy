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
