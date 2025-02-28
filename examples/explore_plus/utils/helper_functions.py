#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 11:10:56 2024

@author: apaunov
"""

import os
import os.path as op
import sys
from time import time
import itertools
import numpy as np
import numpy.random as npr
import pandas as pd
import scipy.stats as sp
import matplotlib.pyplot as plt




# %% Functions

def bool2idx(boolarray):
    """ Convert a boolean to index (argwhere wrapper) """
    ndim = len(np.squeeze(boolarray).shape)
    if ndim > 0: 
        if ndim == 1:
            idx = np.argwhere(boolarray).flatten()
        else:
            idx = [np.argwhere(boolarray[:, opt]).flatten()
                   for opt in range(boolarray.shape[1])]
    else:
        idx = []
    return idx


def idx2bool(idx, nd):
    """ Convert an index to a boolean mask 
    index can contain nan; 
    NB: if max(idx) > nd-1, these values are ignored! """
    bool_array = []
    for v in range(nd):
        bool_array.append(idx == v)

    return np.vstack(bool_array)


def is_single(num):
    """ Checks if input is single and returns boolean. 
    single means anything you can't take the len of, 0d; either py base 
    scalar or numpy scalar. If it's a py base char string, it has a len 
    but it's made into a list 
    """
    
    issingle = False
    try:
        len(num)
    except Exception:
        issingle = True
        
    if not issingle: 
        if type(num) == str:
            issingle = True
    
    return issingle


def single2array(num, typ="list"): 
    """ Converts a scalar to array format (if it isn't already); inputs:
        num = scalar or None 
        typ = string for output type: array (numpy) or list 
    returns array
        
        """
    
    isnone = False
    if is_single(num):
        isnone = num is None
        num = [num]
    
    if type(num) == list:
        # ie, if it was single to begin with and converted to list above
        if typ == "array":
            if isnone:
                num = np.array([np.nan])
            else:
                num = np.array(num)
            
    return num


def repel(num, n, typ="array"):
    """repeat element. Inputs:
        num = element: either scalar or list 
        n = number of repetitions
        typ = output type (list or array)
    returns repeated element
    """
    num = single2array(num, typ=typ)
    if len(num) > 1:
        nums = num
    else: 
        if typ == "list":
            if type(num) is not list: num = list(num)
            nums = num * n
        elif typ == "array":
            nums = np.ones(n) * num
        
    return nums


def get_combos(n, nopt=None, output=int):
    """Gets possible combinations of choices; inputs: 
        n = number of trials (scalar)
        nopt = number of options (scalar)
        output = data type (boolean or integer)
    returns ordered set of all possible choice sequences
    """
    if nopt is None:
        nopt = 2
    if nopt > 2:
        output = int
    
    opts = np.arange(nopt).astype(int)
    combos = np.asarray(
        list((itertools.product(opts, repeat=n)))).astype(output)
    combos = np.flipud(combos)
    nterms = np.sum(combos, axis=1)
    isort = np.argsort(nterms)
    combos = combos[isort]
    
    return combos


def map2legacyIO(): # TO EDIT
    """ 
    To map naming convention from explore idealObserver to explore_plus IO
    
    
    """
    which_variables = ['MAP_reward',
                           'expected_reward',
                           'expected_uncertainty',
                           'unexpected_uncertainty',
                           'prediction_error',
                           'unsigned_prediction_error',
                           'prediction_error_MAP',
                           'unsigned_prediction_error_MAP',
                           'feedback_surprise',
                           'signed_feedback_surprise',
                           'expected_discrete_reward',
                           'expected_outcome_uncertainty',
                           'estimation_confidence']

    vars_requiring_reward_prob = ['prior_reward_probability',
                                  'posterior_reward_probability',
                                  'feedback_surprise',
                                  'signed_feedback_surprise',
                                  'expected_discrete_reward',
                                  'expected_outcome_uncertainty']
