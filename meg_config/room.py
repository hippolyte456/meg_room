'''
TODO cahier des charges à définir avec Fosca
- It has to reduce the possibility of mistakes while letting access to all possible experiments configurations for the user.
- Robustness : 0 erreur possible sur les envois et receptions de trigger etc // moins grave sur les checks et fonctinnalités supplémentaire.
'''


CONFIG_PATH = "/home/hippolytedreyfus/Documents/meg_config/meg_config/config/hardware_config.yaml"
USER_CONFIG_PATH = "/home/hippolytedreyfus/Documents/meg_config/meg_config/config/user_config.yaml"


import yaml
from ._stim_pc import StimPC
from ._eyetracker import Eyelink
from ._response_buttons import ResponseButtons

#TODO : se renseigner sur ce qu'ils font à l'ICM : contacter l'ingé qui a surement eu le temps de faire ça ?
class MegRoom(): #Heritage ?
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
        self._load_and_set_attributes(self.hardware_config_path)
        self._load_and_set_attributes(self.user_config_path)
        
        self.stim_pc = StimPC(self.stim_pc)
        self.eyetracker = Eyelink(self.eyetracker)
        self.response_buttons = ResponseButtons(self.response_buttons)
        # test de tout ce qu'il y a tester avant de lancer une expé
        self._pytest_config()
        
           
    def _load_and_set_attributes(self, file_path):
        """Charge un fichier YAML et met à jour les attributs de l'instance."""
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                config_dict = yaml.safe_load(file) 
                if config_dict:
                    self._dict_to_attributes(self, config_dict)  # Conversion en attributs TODO utiliser pydantic !
            except yaml.YAMLError as e:
                print(f"Erreur lors du chargement de {file_path} : {e}")


    def _dict_to_attributes(self, obj, config_dict):
        """Transforme récursivement un dictionnaire en attributs de l'objet donné."""
        for key, value in config_dict.items():
            if isinstance(value, dict):
                # Si la valeur est un dictionnaire, créer un sous-objet pour conserver la hiérarchie
                sub_obj = type(key, (), {})()  # Crée un objet vide avec le nom de la clé
                self._dict_to_attributes(sub_obj, value)  # Remplir récursivement le sous-objet
                setattr(obj, key, sub_obj)  # Attacher l'objet au parent
            else:
                setattr(obj, key, value)  # Attribuer la valeur simple
                
    
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

    
    def show_all(self):
        '''Show all the hardware available in the room'''
        def recursive_print(obj, indent=0):
            for attr, value in obj.__dict__.items():
                if hasattr(value, "__dict__"):
                    print("  " * indent + f"{attr}:")
                    recursive_print(value, indent + 1)
                else:
                    print("  " * indent + f"{attr}: {value}")
        
        print("MEG Room Configuration:")
        recursive_print(self)
