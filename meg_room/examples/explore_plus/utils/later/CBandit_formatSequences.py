#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 16:28:38 2021

@author: apaunov
"""
import scipy.io as spio
import os.path as op
import numpy as np
import pandas as pd

# Set paths
rootdir = '/Users/apaunov/iCloud/neurospin/CBanditTask_tobii/sequences'
input_dir = op.join(rootdir, 'fromDalin')
output_dir = op.join(rootdir, 'formatted')

# set constants
n_seq = 11
seq_id = np.arange(n_seq) + 1
n_trials = 96
n_arms = 2

# Control execution
CONVERT_TO_CSV = True
ADD_FMRI_INFO = True
ADD_ITI = False

# Convert from .mat files to csvs (all sequences)
if CONVERT_TO_CSV:
    for seq_num in seq_id:
        seq_input_path = op.join(input_dir, 'RR%d.mat' % seq_num)
        seq_mat = spio.loadmat(seq_input_path)
        rewards = seq_mat['task']['rr'][0][0]
        sds = seq_mat['task']['rs'][0][0]
        sds = sds[:,0] # for some reason the sds for seq_ids=6 have a bunch of extra columns
        mean_rewards = seq_mat['task']['rm'][0][0]
        iscp = np.zeros((n_arms, n_trials))
        iscp[:,1:] = (np.diff(mean_rewards, 1) != 0).astype(int)
        obs = seq_mat['task']['Obs'][0][0]
        forced = np.nan * np.ones(n_trials)
        forced[~np.isnan(obs[0,:])] = 0
        forced[~np.isnan(obs[1,:])] = 1
        
        seq_df = pd.DataFrame({'A': rewards[0,:],
                              'B': rewards[1,:],
                              'SD': sds,
                              'forced': forced,
                              'A_mean': mean_rewards[0,:], 
                              'B_mean': mean_rewards[1,:],
                              'A_cp': iscp[0,:],
                              'B_cp': iscp[1,:]})
        
        seq_output_path = op.join(output_dir, 'RR%02d.csv' % seq_num)
        seq_df.to_csv(seq_output_path, index=None)

# Add fMRI info (question positions, ITIs) for the subset of sequences used
if ADD_FMRI_INFO:
    # Sequences info
    n_grp = 2 # number of sets x 4
    
    # Which sequences to use
    # previous versions: 
    # seq_grp_ids = [[1, 2, 3, 4], [5, 7, 8, 9]]
    # seq_grp_ids = [[1, 2, 3, 4], [5, 7, 8, 11]]
    seq_grp_ids = [[1, 2, 3, 4], [5, 7, 8, 10]]
    
    # ITIs info (hardcoded)
    iti_range = (2, 5) # in seconds
    iti_avg = np.mean(iti_range)
    iti_norm = iti_avg * n_trials
    
    # Question positions (pre-defined, same across 2 sets of sequences)
    q_pos_path = op.join(rootdir, 'question_positions.csv')
    q_pos = pd.read_csv(q_pos_path)
    seq_count = 0
    for grp in range(n_grp):
        grp_num = grp + 1
        
        for seq_idx, seq_num in enumerate(seq_grp_ids[grp]):
            seq_count = seq_count + 1
            # Set random seed for reproducibility (for ITIs)
            np.random.seed(seq_num)
            
            seq_idx2num = seq_idx + 1
            
            # Load formatted sequences
            seq_csv_path = op.join(output_dir, 'RR%02d.csv' % seq_num)
            sequence = pd.read_csv(seq_csv_path)
            
            # Add ITIs
            if ADD_ITI: 
                ITI = np.random.uniform(iti_range[0], iti_range[1], n_trials)
                ITI_scale = (iti_norm - np.sum(ITI)) / n_trials
                ITI = ITI + ITI_scale
                
                sequence['ITI'] = ITI
            
            # Add question positions
            sequence['isQ'] = q_pos['sequence%d' % seq_count]
            
            # Name sequence and save
            seq_fname = 'sequence_%d_%d.csv' % (grp_num, seq_idx2num)
            seq_save_path = op.join(rootdir, seq_fname)
            sequence.to_csv(seq_save_path)
            
            
            
    