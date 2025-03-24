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


