
from itertools import combinations

#TODO fix this !

def hamming_distance(x, y):
    """Calcule la distance de Hamming entre deux nombres binaires."""
    return bin(x ^ y).count("1")


def find_robust_codes(n, min_hamming_dist=2):
    """
    Génère une liste de nombres entre 0 et 255 maximisant la robustesse.
    
    :param n: Nombre de valeurs nécessaires.
    :param min_hamming_dist: Distance minimale entre les codes (>=2 pour éviter erreurs proches).
    :return: Liste de nombres binaires choisis.
    """
    candidates = list(range(1, 256))  # On exclut 0 pour éviter un signal nul
    selected = [candidates.pop(0)]    # On prend le premier candidat
    
    while len(selected) < n:
        for c in candidates:
            if all(hamming_distance(c, s) >= min_hamming_dist for s in selected):
                selected.append(c)
                candidates.remove(c)
                break
                
    return selected


def get_binary_encoding(stim_class) -> list:
    """
    Génère un encodage robuste pour une hiérarchie de stimuli.
    
    :param stim_class: Structure des classes et sous-classes.
    :return: Liste d'entiers (0-255) optimisés pour la robustesse.
    """
    num_stimuli = sum(sum(c) if isinstance(c, list) else c for c in stim_class)
    codes = find_robust_codes(num_stimuli, min_hamming_dist=2)  # Génère des codes TTL robustes
    
    encoding = {}
    index = 0
    for i, class_def in enumerate(stim_class):
        class_name = f"class_{i+1}"
        if isinstance(class_def, list):  # Sous-classes
            encoding[class_name] = {}
            for j, sub_size in enumerate(class_def):
                encoding[class_name][f"subclass_{j+1}"] = codes[index:index + sub_size]
                index += sub_size
        else:
            encoding[class_name] = codes[index:index + class_def]
            index += class_def
            
    return encoding


