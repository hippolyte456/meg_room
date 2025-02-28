#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 18:01:59 2021

Parameters for the curious bandit task. 

@author: apaunov
"""


from expyriment import misc, io
import random


# =============================================================================
# CONTROL STIMULUS SIZE
# =============================================================================
size_in_deg = 2.5
IS_BIG = False
MULT = 1.5

# =============================================================================
# DIRECTORIES #TODO 
# =============================================================================
ROOT_DIR = '~/Documents/explore_plus/'
DATA_DIR = '~/Documents/explore_plus/Data/'
SEQ_DIR = '~/Documents/explore_plus/Data/TaskSequences/'
TASK_DIR = '~/Documents/explore_plus/BehavioralTask/'
# =============================================================================
# BLOCKS INFO
# =============================================================================
N_TRIALS = 96 
N_BLOCKS = 8
LOW_SD = 10
HIGH_SD = 15

# =============================================================================
# MEG port
# =============================================================================


# =============================================================================
# TIMING
# =============================================================================
CUE_DUR = 2 
ISI = 2
FRAME_OFF_DUR = 0.75
FRAME_ON_DUR = ISI - FRAME_OFF_DUR
OUT_DUR = 1
meanITI = 2
eITI = 0


def generate_values(n,m,e):
    '''
    Generate n values (of ITI) following a uniform distribution with mean m, in a range [m-e, m+e]
    with the constraint that the sum of the values will always be n*m
    '''
    wanted_total_sum = n * m
    values = [random.uniform(m-e, m+e) for _ in range(n-1)] 
    total_sum = sum(values) 
    last_value = wanted_total_sum - total_sum
    if last_value < m-e or last_value > m+e:
        return generate_values(n,m,e)  # Retry if last value is out of bounds
    values.append(last_value) 
    return values 

ITI = generate_values(N_TRIALS, meanITI, eITI)


# Questions timing in sec   
Q_DUR = 3 # single question max duration
Q_PAD = 0.5 # time between value guess response and conf rating
Q_GAP = 1 # time before and after a set of qs (before, displays "Questions")
N_Q = 4 # number of questions in a set
Q_PERIOD_DUR = (Q_DUR  + Q_PAD) * N_Q + (Q_GAP*2) # ie 16 sec total
TOT_TIME_Q = 16 - 2*Q_GAP  #TODO


FIX_DUR = 2.5
    
# =============================================================================
# VARIATION OF THE TASK
# =============================================================================

LEVELS = [20, 40, 60, 80]          
VALUES = ['20','40','60','80']


# =============================================================================
# KEYS
# =============================================================================


Left = 'port1_4'
LeftMiddle = 'port1_8'
RightMiddle = 'port2_8'
Right = 'port1_1'
LEFT_KEY = Left
RIGHT_KEY = Right
KEYS_CHOICE = [LEFT_KEY, RIGHT_KEY]
KEYS_VAL = [Left, LeftMiddle, RightMiddle, Right]
KEYS_CONF = [Left, LeftMiddle, RightMiddle, Right]


# =============================================================================
# SIZES
# =============================================================================

abc = 0.4
stim_sizes = {'stim_frame_rad': 75*abc, 
        'stim_rad': 60*abc, 
        'position': 120*abc, 
        'fix_center': 11*abc, 
        'fix_middle': 23*abc,
        'fix_outer': 35* abc, 
        'fix_line': 8*abc,
        'total_size_pix': 387*abc,
        'font_size': 30} #be careful with variation of a parameter without variation of the others !

FIX_0 = stim_sizes['fix_center']
FIX_REST = FIX_0

FIX_LOW = stim_sizes['fix_middle']
FIX_HIGH = stim_sizes['fix_outer']

FIX_LINE = stim_sizes['fix_line']

CUE_0 = stim_sizes['stim_rad']
CUE_1 = stim_sizes['stim_frame_rad']

POS_LEFT = -stim_sizes['position']
POS_RIGHT = stim_sizes['position']

POS_RATE_PROMPT = stim_sizes['position']
POS_RATE_OPTIONS = -stim_sizes['position']
POS_RATE_OPTIONS_VERT = -stim_sizes['position']

POS_RATE_OPTIONS_ENDS = [-stim_sizes['position'] - stim_sizes['stim_rad']*8,
                            stim_sizes['position'] + stim_sizes['stim_rad']*8]

RATE_SIZE = stim_sizes['stim_rad']*1.5
RATE_SIZE_FRAME = stim_sizes['stim_rad']*1.7
RATE_LINE_FRAME = stim_sizes['fix_line']*1.5
FONT_SIZE = stim_sizes['font_size']
    


# =============================================================================
# COLORS
# =============================================================================

# Background
BLACK = (0, 0, 0)
GRAY = (119, 136, 153)
DARK_GRAY = (96, 96, 96) # DELL SCREEN LUMINANCE = 26
WHITE = (255, 255, 255)
YELLOW = (255,255,0)

# DELL SCREEN
CUE_PURPLE = (126, 30, 126)
CUE_ORANGE = (150, 38, 6)

# Fixation cross colors
FIX_COLOR = GRAY
MISS_FIX_COLOR = misc.constants.C_RED

# =============================================================================
# FONTS
# =============================================================================
mult = 1


# =============================================================================
# SEQUENCE GENERATION
# =============================================================================    
NOPT = 2
HORIZON = 96
LATENT_LEVELS = LEVELS
SD_LEVELS = [LOW_SD, HIGH_SD] #CAUTION : redifinition of sd_levels in the class

NbQForced = 2
NbQFree = 4
Min_Qspacing = 9
VOL = 1/24

# Options parameters
IDEAL_VOL = True # returns exactly num changepoints over the sequence as specified by volatility
NCP_RANGE = (3, 5) # range of allowed num changepoints (overridden if ideal_vol is True)
CP_MIN_FROM_START = 10 # min number of trials before changepoint
CP_MIN_TO_END = 6 # min number of trials from last changepoint to end of sequence
CP_MIN_DIST = 10 # min number of trials between chanagepoints
CP_MIN_OPT_DIST = 6 # minimum trials between changepoints on different options
OUT_BOUNDS = (1, 100) # bound observations in some range (see method argument)
LL_MEAN_TOL = 0.01 # tolerance for average latent levels deviation from expected mean reward
OUT_MEAN_TOL = 0.005 # tolerance for observations average deviation from " " "
LL_OPT_DIFF_TOL = 0.2 # tolerance for average diff between latent_levels over a block 
# (too similar=doesn't matter what you choose; too different=too obvious what to choose)
NORM_NOISE = True # normalize noise to match the SD level
# Forced choices
FORCED_LEN = 4  # number of forced choices per forced segment
FORCED_PERIOD = 12  # new forced segment starts every N trials
MAX_SAME_CHOICE = 3  # how many forced choices can be the same within a segment



