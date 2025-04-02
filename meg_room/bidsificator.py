'''
Code from Julie
'''

import os, re, mne
from pathlib import Path
from mne_bids import BIDSPath, write_raw_bids, write_anat, get_anat_landmarks, write_meg_calibration, write_meg_crosstalk

import sys, importlib


from .config.bids_config import *



#TODO : replace the config by a dynamic path to the config of the user.
module_path = os.getenv("MODULE_DIR", "/default/path/to/module")
module_name = "bids_config"  # Nom du fichier sans `.py`
module_path = Path(module_path)

if module_path.exists():
    sys.path.insert(0, str(module_path))  # Ajoute le chemin au PYTHONPATH
    mon_module = importlib.import_module(module_name)  # Importe le module
    print(f"Module {module_name} importé depuis {module_path}")
else:
    print(f"Erreur : le dossier {module_path} n'existe pas !")
    


class Bidsificator:
    
    def __init__(self,):
        pass
    
    def convert_to_bids():
        mne.set_log_level("ERROR")
        
        for folder in RAW_DATA_PATH.iterdir():
            if folder.is_dir():
                nip = folder.name
                sub = dict_nip_to_sn.get(nip)

                if not sub:
                    print(f"Sujet {nip} non trouvé dans le dictionnaire. Ignoré.")
                    continue

                session_dirs = sorted([d for d in folder.iterdir() if d.is_dir()])

                for session_idx, session_dir in enumerate(session_dirs, start=1):
                    session = f"{session_idx:02d}"

                    write_meg_calibration(
                        CAL_FNAME,
                        BIDSPath(
                            subject=sub,
                            session=session,
                            datatype='meg',
                            root=BIDS_PATH
                        )
                    )
                    write_meg_crosstalk(
                        CT_FNAME,
                        BIDSPath(
                            subject=sub,
                            session=session,
                            datatype='meg',
                            root=BIDS_PATH
                        )
                    )

                    for file in session_dir.iterdir():
                        if file.suffix == '.fif' and 'run_' in file.name:
                            match = re.search(r"run_(\d+)\.fif", file.name)
                            if not match:
                                print(f"Aucun numéro de run trouvé pour le fichier {file.name}")
                                continue

                            run = int(match.group(1))

                            bids_path = BIDSPath(
                                subject=sub,
                                session=session,
                                run=run,
                                task=TASK,
                                datatype='meg',
                                root=BIDS_PATH
                            )

                            raw = mne.io.read_raw_fif(file, allow_maxshield=True)
                            write_raw_bids(raw, bids_path=bids_path, overwrite=True)

                    empty_room_file = session_dir / 'empty_room.fif'
                    if empty_room_file.exists():
                        empty_raw = mne.io.read_raw_fif(empty_room_file, allow_maxshield=True)

                        meas_date = empty_raw.info['meas_date']
                        if meas_date is None:
                            print(f"Aucune date trouvée pour le fichier {empty_room_file}")
                            continue

                        emptyroom_date = meas_date.strftime('%Y%m%d')

                        empty_bids_path = BIDSPath(
                            subject=sub,
                            session=session,
                            task='emptyroom',
                            datatype='meg',
                            root=BIDS_PATH
                        )

                        write_raw_bids(empty_raw, bids_path=empty_bids_path, overwrite=True)

                anat_file = folder / 'anat' / 'T1.nii.gz'
                if anat_file.exists():
                    anat_bids_path = BIDSPath(
                        subject=sub,
                        root=BIDS_PATH,
                        session=None
                    )
                    trans_file = folder / 'trans.fif'
                    landmarks = None
                    if trans_file.exists():
                        landmarks = get_anat_landmarks(anat_file, info=raw.info, trans=trans_file)
                    write_anat(
                        image=anat_file,
                        bids_path=anat_bids_path,
                        landmarks=landmarks,
                        overwrite=True
                    )

                beh_file = folder / f'sub-{sub}_responses.csv'
                if beh_file.exists():
                    beh_target = BIDS_PATH / f"sub-{sub}/beh" / f"sub-{sub}_task-{TASK}_beh.tsv"
                    beh_target.parent.mkdir(parents=True, exist_ok=True)
                    beh_file.rename(beh_target)
                else:
                    print(f"Aucun fichier comportemental trouvé pour le sujet {sub}.")


        print(f"\n\nConversion terminée. Les fichiers sont dans {BIDS_PATH}\n")




if __name__ == '__main__':
    bidsifier = Bidsificator()
    bidsifier.convert_to_bids()