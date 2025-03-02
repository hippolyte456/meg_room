'''
TODO cahier des charges à définir avec Fosca
- It has to reduce the possibility of mistakes while letting access to all possible experiments configurations for the user.
- Robustness : 0 erreur possible sur les envois et receptions de trigger etc // moins grave sur les checks et fonctinnalités supplémentaire.
'''


CONFIG_PATH = "/home/hippolytedreyfus/Documents/MEGconfig/meg-config/config/hardware_config.yaml"
USER_CONFIG_PATH = "/home/hippolytedreyfus/Documents/MEGconfig/meg-config/config/user_config.yaml"


import pytest
import mne
import yaml
import expyriment as expy
from parallel_ports import MEG_ports


#TODO : se renseigner sur ce qu'ils font à l'ICM : contacter l'ingé qui a surement eu le temps de faire ça ?
class meg_neurospin_config(): #Heritage ?
    ''' 
    Robust hardware configuration setup for the neurospin meg,
    with a great amount of verbosity, to be usefull to the user just before to start the session.
    
    This class has to be used by the meg experimenters. 
    It is an intermediary class of expyriments with the specific need / hardware setup of neurospin and requires a config file (yaml?)
    '''  

    def __init__(self, hardware_path, user_path):
        self.hardware_config_path = hardware_path
        self.user_config_path = user_path
        # récupérer les configs ports parallèles et autres hardwares qui peut changer.
        self._load_config(self.hardware_config_path)
        self._load_config(self.user_config_path)
        
        self.parports = MEG_ports() #pareil pour eyelink, etc...
        # test de tout ce qu'il y a tester avant de lancer une expé
        self._pytest_config()
        
           
    def _load_config(self,file_path):
        """Charge un fichier YAML et retourne son contenu sous forme de dictionnaire."""
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                return yaml.safe_load(file)  # Utiliser `safe_load` pour éviter l'exécution de code arbitraire
            except yaml.YAMLError as e:
                print(f"Erreur lors du chargement de {file_path} : {e}")
                return None
    
    
    def _pytest_config(self):
        '''run all tests'''
        pass
        #HARDWARE
        # test port parallèles 
        # test des boutons réponses 
        # test de la bonne connexion et synchro de tous les equipements
        # SOFTWARE
        # data quality assessement
        # check de l'environnement python
