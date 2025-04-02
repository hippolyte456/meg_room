

BASE_PATH = '/neurospin.../neuromag/...'
BIDS_PATH = 'bids' 
RAW_DATA_PATH = 'raw'  
TASK = 'mentalizing' 

#multi session
SESSION = None #check que le code actuel gère ça... ça ne doit pas etre compliqué puisque c'est deja implémenté dans mne_bids
DATATYPE = None

# Direction a setup sur le serveur meg.
CAL_FNAME = BASE_PATH / 'calibration/sss_cal_3176_20240123_2.dat'
CT_FNAME = BASE_PATH / 'calibration/ct_sparse.fif'


#user setup ? ... ou automatiquement fait avec un log de la converion de l'un à l'autre pour que l'utilisateur s'y retrouve 
dict_nip_to_sn = {
'le_240431':'01',
'ld_240454': '02'
}

# ajouter le paramètre 'nom du fihcher au moment de l'enregistrement', pour pouvoir appliqué la regex en fonction de ça.


# l'extraction des events... cf code richard ?