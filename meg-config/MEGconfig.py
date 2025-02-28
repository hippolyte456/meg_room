'''
TODO cahier des charges à définir avec Fosca
- It has to reduce the possibility of mistakes while letting access to all possible experiments configurations for the user.
- Robustness : 0 erreur possible sur les envois et receptions de trigger etc // moins grave sur les checks et fonctinnalités supplémentaire.
'''

import pytest
import mne
import yaml
import expyriment as expy



#TODO : se renseigner sur ce qu'ils font à l'ICM : contacter l'ingé qui a surement eu le temps de faire ça ?
class meg_neurospin_config(): #Heritage ?
    ''' 
    Robust hardware configuration setup for the neurospin meg,
    with a great amount of verbosity, to be usefull to the user just before to start the session.
    
    This class has to be used by the meg experimenters. 
    It is an intermediary class of expyriments with the specific need / hardware setup of neurospin and requires a config file (yaml?)
    '''  

    def __init__(self, config):
        self.expy = expy # deal with the best way to do it ? what is necessary or not in term of expy integration ?
        self.cfg = config
        # récupérer les configs ports parallèles et autres hardwares qui peut changer.
        self._load_config()
        # test de tout ce qu'il y a tester avant de lancer une expé
        self._pytest_config()
           
    
    def _load_config(self):
        pass
    
    
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
