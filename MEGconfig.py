import pytest
import mne
import yaml
import expyriment as expy


HARDWARE = ['response_buttons', 
            'audio', 
            'eyelink',
]

#TODO : se renseigner sur ce qu'ils font à l'ICM : contacter l'ingé qui a surement eu le temps de faire ça ?
#de quelle classe faire hériter ? expyriment/ Psychopy ? autres (mro à configurer) 
# ... non une classe intermédiaire c'est mieux.
class meg_neurospin_config(): 
    ''' 
    Robust hardware configuration setup for the neurospin meg,
    with a great amount of verbosity, to be usefull to the user just before to start the session.
    
    This class has to be used by the meg experimenters. 
    It is an intermediary class of expyriments with the specific need / hardware setup of neurospin and requires a config file (yaml?)
    
    
    TODO cahier des charges à définir avec Fosca
    - It has to reduce the possibility of mistakes while letting access to all possible experiments configurations for the user.
    - Robustness : 0 erreur possible sur les envois et receptions de trigger etc // moins grave sur les checks et fonctinnalités supplémentaire.
    '''  

    def __init__(self, config):
        self.expy = expy
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
     
   
    def quick_fif_checking(self): # voir avec Anne et Fosca ce qu'il faudrait incorporer
        pass
        #load the .fif from the meg stim
        #run a battery of test (based on the user config file)
        
    