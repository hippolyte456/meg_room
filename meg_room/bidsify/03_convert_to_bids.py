# -*- coding: utf-8 -*-
'''
Code from Diane
'''

###############################################################################
############################ Conversion to BIDS ###############################
###############################################################################

import mne
import os.path as op
import numpy as np

from mne_bids import (
    write_raw_bids,
    write_meg_calibration,
    write_meg_crosstalk,
    write_anat,
    BIDSPath,
    print_dir_tree,
)
from mne_bids.stats import count_events


data_path = r'\\fouet.intra.cea.fr\neurospin\meg\meg_tmp\Deltaphase_shift_Valentine_2021\data'


subject_number = '08'
subject_path = op.join(data_path, '08_fd110104')
#deriv_path = op.join(data_path, 'BIDS') #old path
deriv_path = r'\\fouet.intra.cea.fr\neurospin\meg\meg_tmp\Deltaphase_shift_Valentine_2021\BIDS'
fs_subjects_dir = op.join(deriv_path, 'freesurfer')  #freesurfer subjects dir
t1_fname = op.join(subject_path, 'irm', f'sub-{subject_number}_ses-01_T1.nii') 

output_path = deriv_path

#new events
event_id = {
    'start_expe': 48,
    'start_cue_ON': 2,
    'start_cue_OFF': 16,
    'start_cue_JIT': 32,
    'visual_cue': 8,
    'target_ON_1': 10,
    'target_ON_2': 18,
    'target_OFF_1': 24,
    'target_OFF_2': 26,
    'target_JIT_1': 34,
    'target_JIT_2': 40,
    'red_button': 16384,
    'green_button': 8192,
    'correct': 4,
    'incorrect': 9,
    'irrelevant_bp': 400,
    'premature_bp': 300,
    'no_bp': 200,
    'BAD_ACQ_SKIP': 999}



raw_fname_template = op.join(subject_path, 'meg', 'run0{}_raw.fif')
events_fname_template = op.join(subject_path, 'meg', 'run0{}_raw-eve.fif')
rs_fname = op.join(subject_path, 'meg', 'resting_state_raw.fif')
er_fname = op.join(subject_path, 'meg', 'empty_room_raw.fif')


#loop over runs and convert them to bids + create event file if not yet created
for run in range(1, 2):  # 9 runs so write 10
    raw_fname = raw_fname_template.format(run)
    events_fname = events_fname_template.format(run)

    raw = mne.io.read_raw(raw_fname, allow_maxshield=True)
    raw.info['line_freq'] = 50
    
    if op.exists(events_fname):
        events = mne.read_events(events_fname)
    else:
        events = mne.find_events(raw, stim_channel='STI101', shortest_event=0.00001, min_duration=0.003, consecutive=True)
        mne.write_events(events_fname, events, overwrite=True)

    # select only the sensors we need   
    ##### supposed to be True everywhere, here it is for sub-05                  
    #raw.pick_types(ias=True, meg=True, eeg=False, stim=True, eog=False, ecg=False, bio=False, misc=False, syst=True) 
    
    ##### only for sub-05
    #channels_to_drop = ['STI001', 'STI002', 'STI003', 'STI004', 'STI005', 'STI006', 'STI007', 'STI008',
                       # 'STI009', 'STI010', 'STI011', 'STI012', 'STI013', 'STI014', 'STI015', 'STI016',
                       # 'SYS101'] #, 'BIO004', 'BIO005', 'BIO006', 'BIO007', 'BIO008', 'BIO009', 'BIO010',
        #                'BIO011', 'BIO012']
    #raw.drop_channels(channels_to_drop)

    task = 'audio'
    bids_path = BIDSPath(
        subject=subject_number, 
        session='01', 
        task=task, 
        run='0'+str(run), 
        datatype='meg', 
        root=output_path
    )

    write_raw_bids(
        raw=raw,
        bids_path=bids_path,
        events=events_fname,
        event_id=event_id,
        overwrite=True,
    )


'''
#only if there is a run10
raw = mne.io.read_raw(run10, allow_maxshield=True)
raw.info['line_freq'] = 50

if op.exists('run10_raw-eve.fif'):
    events = mne.read_events('run10_raw-eve.fif')
else:
    events = mne.find_events(raw, stim_channel='STI101', shortest_event=0.00001, min_duration=0.003, consecutive=True)
    mne.write_events('run10_raw-eve.fif', events, overwrite=True)
    

#change subject name for each participant
task = 'audio' 
bids_path = BIDSPath(
    subject='pilot1', 
    session='01', 
    task=task, 
    run=10, 
    datatype='meg', 
    root=output_path
)

write_raw_bids(
    raw=raw,
    bids_path=bids_path,
    events=un10_raw-eve.fif,
    event_id=event_id,
    overwrite=True,
)
'''

#load the empty room (er) data
raw_er = mne.io.read_raw(er_fname, allow_maxshield=True)
raw_er.info['line_freq'] = 50

##### supposed to be True everywhere, here it is for sub-05
raw_er.pick_types(ias=True, meg=True, eeg=False, stim=True, eog=False, ecg=False, bio=False, misc=False, syst=True)

##### only for sub-05
#channels_to_drop = ['STI001', 'STI002', 'STI003', 'STI004', 'STI005', 'STI006', 'STI007', 'STI008',
#                    'STI009', 'STI010', 'STI011', 'STI012', 'STI013', 'STI014', 'STI015', 'STI016',
#                    'SYS101'] #, 'BIO004', 'BIO005', 'BIO006', 'BIO007', 'BIO008', 'BIO009', 'BIO010',
                   # 'BIO011', 'BIO012']
#raw_er.drop_channels(channels_to_drop)
  
bids_er_path = BIDSPath(
        subject=subject_number,
        session='01',
        task='emptyroom',
        datatype='meg',
        root=output_path,
        )

write_raw_bids(
        raw=raw_er,
        bids_path=bids_er_path,
        overwrite=True,
        )


raw_rs = mne.io.read_raw(rs_fname, allow_maxshield=True)
raw_rs.info['line_freq'] = 50

##### supposed to be True everywhere, here it is for sub-05
raw_rs.pick_types(ias=True, meg=True, eeg=False, stim=True, eog=False, ecg=False, bio=False, misc=False, syst=True)
#raw_rs.drop_channels(channels_to_drop)

task = 'rest'
bids_path = BIDSPath(
     subject=subject_number, 
     session='01', 
     task=task, 
     datatype='meg', 
     root=output_path
 )

write_raw_bids(
     raw=raw_rs,
     bids_path=bids_path,
     overwrite=True,
 )


#calibration files - make sure it is the correct path + file names
cal_fname = op.join(data_path, 'sss_config_ns', 'sss_cal_3176_20240123_2.dat')
ct_fname = op.join(data_path, 'sss_config_ns', 'ct_sparse.fif')
    
write_meg_calibration(cal_fname, bids_path)
write_meg_crosstalk(ct_fname, bids_path)


# Get the sidecar ``.json`` file --> check information written
sidecar_json_bids_path = bids_path.copy().update(suffix='meg', extension='.json')
sidecar_json_content = sidecar_json_bids_path.fpath.read_text(encoding='utf-8-sig')
print(sidecar_json_content)


#write T1 mri
#create the BIDSPath object
t1w_bids_path = BIDSPath(subject=subject_number, session='01', root=output_path, suffix="T1w")

t1w_bids_path = write_anat(
    image=t1_fname,  
    bids_path=t1w_bids_path,
    landmarks=None,
    deface=False,
    verbose=None,
    overwrite=True
)






###############################################################################
######################## Check the data (optional) ############################
###############################################################################

#check the structure of the BIDS folder
print_dir_tree(output_path)


#overview of events from the whole dataset
counts = count_events(output_path)
counts










