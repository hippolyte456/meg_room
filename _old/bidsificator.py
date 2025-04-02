'''
From the project root of the meg server, 
bidsify the data of a subject to the BIDS folder of the same meg server.
'''

import os
import shutil
import json
import yaml
from datetime import datetime

from mne_bids import write_raw_bids, BIDSPath


class Bidsificator:
    def __init__(self, bids_path, subject_path):
        self.bids_path = bids_path
        self.subject_path = subject_path
        self.bidsify()

    def bidsify(self):
        # Create the subject folder in the BIDS path
        subject_id = os.path.basename(self.subject_path)
        subject_folder = os.path.join(self.bids_path, "sub-" + subject_id)
        os.makedirs(subject_folder, exist_ok=True)

        # Create the dataset_description.json file
        dataset_description = {
            "Name": "MEG experiment",
            "BIDSVersion": "1.4.0",
            "Authors": ["Author 1", "Author 2"],
            "Acknowledgements": "Acknowledgements",
            "HowToAcknowledge": "How to acknowledge",
            "Funding": "Funding",
            "ReferencesAndLinks": "References and links",
            "DatasetDOI": "Dataset DOI"
        }
        with open(os.path.join(subject_folder, "dataset_description.json"), "w") as file:
            json.dump(dataset_description, file, indent=4)




'''
Code from Julie
'''


from __future__ import annotations
import os, re, mne
from pathlib import Path
from mne_bids import BIDSPath, write_raw_bids, write_anat, get_anat_landmarks, write_meg_calibration, write_meg_crosstalk




mne.set_log_level("ERROR")
class Bidsifier:
    def __init__(self):
        BASE_PATH = Path('/home/jb278714/Bureau/Mind_Sentences/')  
        BIDS_PATH = BASE_PATH / 'bids' 
        RAW_DATA_PATH = BASE_PATH / 'raw'  
        TASK = 'mentalizing' 

        CAL_FNAME = BASE_PATH / 'calibration/sss_cal_3176_20240123_2.dat'
        CT_FNAME = BASE_PATH / 'calibration/ct_sparse.fif'

        dict_nip_to_sn = {
        'le_240431':'01',
        'ld_240454': '02'
        }

def convert_to_bids():
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




