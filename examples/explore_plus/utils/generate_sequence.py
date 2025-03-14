#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 11:09:54 2024

These functions generate a sequence of outcomes for an n-option bandit (iid 
across options) from discrete latent levels, with some Gaussian noise and some 
volatility in the latent levels over time. 

They are parameterized into change point generation, latent level sampling, 
outcome generation to allow easy adding of optional experimental constraints. 
(For this, volatility is assumed fixed over a block / sequence; noise level 
 is externally given and can vary across trials and options)

End-to-end generation with the true generative process is in 
gen_outcomes_generative_process() function

There are additional function for: 
    - setting noise levels in a sequence 
    - making and adding forced choices
    - plotting sequences
    - saving results

To do: 
    - add flags for when max num iterations are exceeded in diff places
    - and/or track how long seq generation takes (rough sense for how 
      representative a seq is with given constraints)


@author: apaunov
"""

#TODO --> all this file in seqGen class
# import os
import os.path as op
from glob import glob
import pickle
# import sys
# from time import time
# import itertools
import numpy as np
import numpy.random as npr
# import pandas as pd
import scipy.stats as sp

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import utils.helper_functions as hf


# %% Changepoints

#changepoints (for one-arm)
def gen_cps(vol, horizon=None):
    return npr.choice([0, 1], p=[1-vol, vol], size=horizon)


# To add: sample ncps from geometric dist 
def one_opt_iscp(vol_opt, horizon, ideal_vol=True, ncp_range=None, 
                 min_from_start=None, min_to_end=None, min_dist=None, 
                 max_iter=10000):
    """ generates change point index for one option; inputs:
            vol_opt = the volatility 
            horizon = num trials
            ideal_vol = bool; if True, always return ncp = round(horizon * p)
            ncp_range = range of allowed # of cps (overridden if ideal_vol=True)
            min_from_start = num trials before 1st cp
            min_to_end = min num trials remaining after last cp
            min_dist = minimum distance between cpss
        returns boolean per trial (1 option) for is / is not a changepoint
        
        """ 
    if ideal_vol:
        ncp_range = [round(vol_opt * horizon)] * 2 # lower, upper
        
    # Subfunctions
    def crop_horizon(horizon, min_from_start=None, min_to_end=None):
        real_horizon = horizon
        if min_from_start is not None:
            real_horizon -= min_from_start
        if min_to_end is not None:
            real_horizon -= min_to_end
        
        return real_horizon
    
    def gen_target_ncp(vol_opt, horizon, ncp_range=None, max_iter=max_iter):
        " cropped horizon here (excl init and end trials where no cp allowed)"
        iscp_opt = gen_cps(vol_opt, horizon=horizon)
        # ncp = len(hf.bool2idx(iscp_opt))
        ncp = np.sum(iscp_opt)
        if ncp_range is not None:
            ncp_iter = 0
            while not (ncp_range[0] <= ncp <= ncp_range[1]) and (ncp_iter <= max_iter):
                iscp_opt = gen_cps(vol_opt, horizon=horizon)
                ncp = np.sum(iscp_opt)
                ncp_iter+=1
        
        return iscp_opt
    
    
    cropped_horizon = crop_horizon(horizon, 
                                   min_from_start=min_from_start, 
                                   min_to_end=min_to_end)
    
    iscp_opt = gen_target_ncp(vol_opt, cropped_horizon, ncp_range=ncp_range)
    
    if min_dist is not None:
        dist_iter = 0
        cpidx = hf.bool2idx(iscp_opt)
        if len(cpidx) > 1:
            min_diff = np.min(np.diff(cpidx))
            while (min_diff < min_dist) and (dist_iter < max_iter):
                iscp_opt = gen_target_ncp(vol_opt, cropped_horizon, ncp_range=ncp_range)

                cpidx = hf.bool2idx(iscp_opt)
                
                if len(cpidx) > 1:
                    min_diff = np.min(np.diff(cpidx))
                else:
                    min_diff = min_dist+1
                
                dist_iter+=1
    
    if min_from_start is not None:
        iscp_opt = np.hstack((np.zeros(min_from_start), iscp_opt))
    if min_to_end is not None:
        iscp_opt = np.hstack((iscp_opt, np.zeros(min_to_end)))
        
    return iscp_opt


# %% Latent levels

def sample_latent_level(latent_levels, probs=None):
    return npr.choice(latent_levels, p=probs)


def gen_latent_level(values):
    return npr.choice(values)


def gen_latent_levels_time(values, ncp, current=None, startwith=None):
    """ makes list of latent levels of lenght ncp for a single option
    current and previous are for controlling initial latent level
    (for e.g., to string together sub-sequences)
    current = excluded latent level (because it was the previous one)
    startswith = the latent level to start with
    "current" trumps "startwith"
    """        
    if current is not None: 
        v0 = list(set(values) - set([current]))
        lls = [npr.choice(v0)]
    else:
        if startwith is None:
            lls = [gen_latent_level(values)]
        else:
            lls = [startwith]
    
    for icp in range(ncp-1):
        vals = list(set(values) - set([lls[-1]]))
        lls.append(gen_latent_level(vals))

    return lls


def gen_latent_seq(vol, latent_levels, nopt, horizon, 
                   ideal_vol=True, 
                   ncp_range=None, 
                   cp_min_from_start=None, 
                   cp_min_to_end=None, 
                   cp_min_dist=None, 
                   cp_min_opt_dist=None, 
                   cp_max_iter=10000, 
                   ll_current=None, 
                   ll_startwith=None, 
                   ll_mean_tol=None, 
                   ll_max_iter=1000,
                   output="sequence"):
    
    """ 
    Generates per-trial latent levels over the block horizon (for all options)
    optional arguments: 
        ideal_vol = N cps match exactly vol over this horizon (rounded) (boolean)
        ncp_range = allowed range of N cps (overridden by ideal_vol) (interval)
        cp_min_from_start = min N trials before 1st cp (scalar)
        cp_min_to_end = min N trials from last cp to end of block (scalar)
        cp_min_dist = min distance between cps (scalar)
        cp_min_opt_dist = min N trials between cps on different options (scalar)
        cp_max_iter = N iterations allowed for finding cps that meet constraints
        (TO DO: add warning when reached without success)
        ll_current = the latent_level that can't be the 1st one in seq
        ll_startswith = the latent_level to start the sequence with
        ll_mean_tol = allowed deviation of the mean ll over trials from global
        ll_max_iter = N iteractions allowed for finding lls that meet tolerance
        output = "sequence" or "info"
    
    """
    
    cpargs = {"ideal_vol": ideal_vol, 
              "ncp_range": ncp_range, 
              "min_from_start": cp_min_from_start, 
              "min_to_end": cp_min_to_end, 
              "min_dist": cp_min_dist, 
              "max_iter": cp_max_iter}
    
    vol = hf.repel(vol, nopt, typ="list")
    ll_current = hf.repel(ll_current, nopt, typ="list")
    ll_startwith = hf.repel(ll_startwith, nopt, typ="list")
    
    resample2mean = ll_mean_tol is not None
    
    if resample2mean:
        expected_mean = np.mean(latent_levels)
        ll_mean_tol_crit = expected_mean * ll_mean_tol
    
    def cp_opt_too_close(cpidx, horizon, min_opt_dist=None):
        if (min_opt_dist is None) or len(cpidx) == 1:
            too_close = False
        else:
            peri_cpbool_sofar = []
            curr_cp1d = np.zeros(horizon).astype(bool)
            if len(cpidx[-1] > 0):
                curr_cp1d[cpidx[-1]] = True
                for cp in cpidx[:-1]:
                    peri_cpidx = []
                    for c in cp:
                        starttrial = c - min_opt_dist 
                        if starttrial < 0: starttrial = 0 
                        endtrial = c + min_opt_dist
                        if endtrial > horizon: endtrial = horizon
                        peri_cpidx.append(np.arange(starttrial, endtrial))
                        
                    peri_cpbool_sofar.append(np.zeros(horizon))
                    if len(peri_cpidx) > 0: 
                        peri_cpidx = np.unique(np.hstack(peri_cpidx))
                        peri_cpbool_sofar[-1][peri_cpidx] = 1
                        
                peri_cpbool_sofar = np.vstack(peri_cpbool_sofar)
                if len(peri_cpbool_sofar.shape) > 1:
                    peri_cpbool_sofar = np.sum(peri_cpbool_sofar, axis=0) > 0
                
                too_close = np.any(
                    np.sum(np.vstack((peri_cpbool_sofar, cp1d)), axis=0) > 1)
            else: 
                too_close = False
            
        return too_close

    cpbool = []
    cpidx = []
    vals = []
    dist = []
    ncps = []
    for iopt in range(nopt):
        cp1d = one_opt_iscp(vol[iopt], horizon, **cpargs)
        cpidx.append(hf.bool2idx(cp1d))
        cps_too_close = cp_opt_too_close(cpidx, horizon, 
                                         min_opt_dist=cp_min_opt_dist)
        too_close_iter = 0
        while cps_too_close and too_close_iter <= cp_max_iter:
            cp1d = one_opt_iscp(vol[iopt], horizon, **cpargs)
            cpidx[-1] = hf.bool2idx(cp1d)
            cps_too_close = cp_opt_too_close(cpidx, horizon, 
                                             min_opt_dist=cp_min_opt_dist)
            too_close_iter += 1 
            
        cpbool.append(cp1d)
        dist1d = np.diff(np.hstack((0, cpidx[-1], horizon)))
        ncp = len(dist1d)
        vals1d = gen_latent_levels_time(latent_levels, ncp, 
                                        current=ll_current[iopt], 
                                        startwith=ll_startwith[iopt])
        
        if resample2mean: 
            mean_ll = (vals1d @ dist1d) / horizon
            resample_ll = np.abs(mean_ll  - expected_mean) > ll_mean_tol_crit
            n_ll_iter = 0
            n_cp_iter = 0
            while resample_ll and (n_ll_iter <= ll_max_iter):
                vals1d = gen_latent_levels_time(latent_levels, ncp, 
                                        current=ll_current[iopt], 
                                        startwith=ll_startwith[iopt])
                mean_ll = (vals1d @ dist1d) / horizon
                resample_ll = np.abs(mean_ll  - expected_mean) > ll_mean_tol_crit
                
                resample_cp = resample_ll and \
                    (n_ll_iter == ll_max_iter) and (n_cp_iter <= ll_max_iter)
                    
                n_ll_iter += 1
                if resample_cp:
                    cp1d = one_opt_iscp(vol[iopt], horizon, **cpargs)
                    cpidx.append(hf.bool2idx(cp1d))
                    cps_too_close = cp_opt_too_close(
                        cpidx, horizon, min_opt_dist=cp_min_opt_dist)
                    too_close_iter = 0
                    while cps_too_close and too_close_iter <= cp_max_iter:
                        cp1d = one_opt_iscp(vol[iopt], horizon, **cpargs)
                        cpidx[-1] = hf.bool2idx(cp1d)
                        cps_too_close = cp_opt_too_close(
                            cpidx, horizon, min_opt_dist=cp_min_opt_dist)
                        too_close_iter += 1 

                    cpbool[-1] = cp1d
                    dist1d = np.diff(np.hstack((0, cpidx[-1], horizon)))
                    ncp = len(dist1d)
                    n_cp_iter += 1
                    n_ll_iter = 0
            
        vals.append(vals1d)
        dist.append(dist1d)
        ncps.append(ncp)
        
    seq = []
    for iopt in range(nopt):
        seq.append([])
        for icp in range(ncps[iopt]):
            seq[iopt].append([[vals[iopt][icp]] * dist[iopt][icp]])
        seq[iopt] = np.hstack(seq[iopt])
    seq = np.vstack(seq)
    
    if output == "sequence":
        lat_seq = seq
    elif output == "info":
        lat_seq = {"ll_seq": seq, "lls": vals, 
                   "cp_dist":  dist, "cp_bool": np.vstack(cpbool), 
                   "cp_idx": cpidx, "ncps": np.array(ncps)-1}
    
    return lat_seq


# %% SD sequences

def set_sd_sequence(sd_levels, horizon, nopt=None, ord_type="fixed", 
                    order=None, opts_match=True, out_type="sequence"):
    """ 
    [this function is confusing and too complex without allowing for some
     plausible features like a "safe" and "risky" option]
    
    Sets a sequence of noise levels over a sequence/block which can change 
    arbitrarily across trials and options; inputs: 
        if sd_levels is a number or w len 1, same sd thruout, for all options, 
        nopt must not be None
        if sd_levels is a vector
            * if opts_match (ie, same noise level across options), the entries 
            are taken to be consecutive segments of the same level (nopt can't 
            be None)
            * else, noise levels are taken to be per option (and len sd_levels
            must match nopt, if given)
        if sd_levels is an array, cols must be options, rows are either 
        literal segs or <order> can select from them with an index, 
        or ord_type="random" will shuffle them randomly 
    
    ord_type = "fixed" or "random"; if fixed, if order is None, in the order 
    of the sd_levels row index; else order is an integer index; "random" 
    out_type is string and can be "sequence" or "info" 
    
    """
    
    sd_levels = hf.single2array(sd_levels, typ="array")
    if len(sd_levels.shape) == 1:
        if len(sd_levels) == 1:
            sd_levels = hf.repel(sd_levels, nopt, typ="array")[np.newaxis, :]

        else:
            if opts_match:
                sd_levels = np.hstack([sd_levels[:, np.newaxis]] * nopt)
            else:
                sd_levels = [
                    np.vstack([sd_levels[c] for c in hf.get_combos(len(sd_levels))])]

        if order is not None:
            sd_levels = np.array(sd_levels).squeeze()
            sd_levels = np.vstack([sd_levels[o] for o in order])
    
    nsegs, nopt = np.vstack(sd_levels).shape

    if order is not None:
        if len(order) > nsegs:
            nsegs = len(order)
        sd_levels = np.vstack([sd_levels[iord] for iord in order])
    
    seglen = int(horizon / nsegs)
    iseven = horizon % nsegs == 0
    seglen_long = None
    if not iseven:
        seglen_long = horizon - (seglen * (nsegs-1))
    
    if ord_type == "random":
        if order is None:  # order over rides order_type
            ordidx = npr.choice(np.arange(nsegs), size=nsegs, replace=False)
        else:
            ordidx = np.array(order)
    elif ord_type == "fixed":
        if order is None:
            ordidx = np.arange(nsegs)
        else:
            ordidx = np.array(order)
            
    # sd_levels = np.array(sd_levels).squeeze()
    sd_levels = sd_levels[ordidx]
    if iseven:
        sd_per_trial = [
            np.array([sd_levels[iseg]] * seglen) for iseg in range(nsegs)]
    else:
        sd_per_trial = [
            np.array([sd_levels[iseg]] * seglen) for iseg in range(nsegs-1)]
        sd_per_trial = sd_per_trial + [np.array([sd_levels[-1]] * seglen_long)]
        
    sd_per_trial = np.vstack(sd_per_trial).T

    if out_type == "sequence":
        sdseq = sd_per_trial
    elif out_type == "info":
        sdseq = {"sd_seq": sd_per_trial, 
                 "sd_levels_ord": sd_levels, 
                 "sd_change_idx": [hf.bool2idx(sdopt) for sdopt in np.diff(sd_per_trial, axis=1)],
                 "sd_ord_idx": ordidx, 
                 "sd_seglen": seglen, 
                 "sd_seglen_long": seglen_long, 
                 "sd_nsegs": nsegs
                 }
        
    return sdseq


# %% Outcomes --> now we use the sd levels... 
# to add: option to check if mean outcomes are within some tol and resample 
# if not (after some iters, resample the latent levels) 

def single_outcome(m, sd, bounds=None):
    outcome = np.round(npr.normal(loc=m, scale=sd))
    if bounds is not None: 
       while not (bounds[0] <= outcome <= bounds[1]): 
           outcome = np.round(npr.normal(loc=m, scale=sd))
        
    return int(outcome)
    

def latent2outcome_dist_trial(lat_dist, latent_levels, outcomes, sd, 
                              normalize=True):
    """ Projects latent_level probabilities at a given time to outcome-value 
    probabilities, given the current noise level. Inputs:
        lat_dist = probabilities of each latent level (list/array)
        latent_levels = mean latent outcome level (list/array)
        outcomes = possible observed outcome values (e.g., 1, 2, ..., 100)
        sd = noise level on this trial (scalar)
        normalize = outcome probabilities sum to one (boolean) 
        (because they're often truncated within outcome bounds)
    """
    
    out_dist = np.vstack(
        [sp.norm.pdf(outcomes, ll, scale=sd) for ll in latent_levels])
    out_dist = lat_dist @ out_dist
    if normalize:
        out_dist = out_dist / np.sum(out_dist)
        
    return out_dist


def single_outcome_within_values(m, sd, values, latent_levels):
    """ generates a single outcome within possible outcome values; inputs:
        m = latent_level (scalar)
        sd = noise level (scalar)
        values = possible outcome values (e.g., 1, 2, ..., 100)
        latent_levels = mean latent outcome level
    """
    lat_dist = (latent_levels == m).astype(int)
    value_probs = latent2outcome_dist_trial(lat_dist, latent_levels, values, sd)
    outcome = npr.choice(values, p=value_probs)
    
    return outcome
    
    
def gen_outcome(m, sd, bounds=None, values=None, latent_levels=None):
    """
    bounds are inclusive
    
    if both values and bounds are not None, values are taken within bounds
    if latent levels are not None either values or bounds must be specified
    
    handling bounds
    if only bounds are specified, resamples at the current level (m)
            - this will cause avg for this level to be higher / lower than 
            nominal 
    if latent_levels are specified, always sampled within bounds 
        - but there's non-zero prob of obs far from the mean
        
    """
    sample_in_bounds = latent_levels is not None
    
    if sample_in_bounds:
        if type(latent_levels) == list:
            latent_levels = np.array(latent_levels)
        if bounds is not None:
            if values is not None:
                values = values[hf.bool2idx(values >= bounds[0])]
                values = values[hf.bool2idx(values <= bounds[1])]
            else:
                values = np.arange(bounds[0], bounds[1]+1)
        
        if values is not None:
            outcome = single_outcome_within_values(m, sd, values, latent_levels)
    else:
         outcome = single_outcome(m, sd)
         if bounds is not None: 
            while not (bounds[0] <= outcome <= bounds[1]): 
                outcome = single_outcome(m, sd) 
    
    return outcome


def sample_outcomes(latent_levels_1d, noise_levels_1d, 
                    bounds=None, latent_levels=None, normalize_noise=False):
    """ generates outcomes over trials for a single option; inputs:
            latent_levels_1d = vector of latent level sequence for a block (1 option)
            noise_levels_1d = vector of noise (sd) levels
            bounds = outcome value range (interval)
            latent_levels = possible levels; if not None, outcomes are always
            sampled within bounds
            normalize_noise = ensure outcome deviations from latent levels are
            exactly equal to the given noise level
            
        output: 1d sequence of outcomes
    
    """
       
    out = []
    for ll, sd in zip(latent_levels_1d, noise_levels_1d): 
        out.append(gen_outcome(ll, sd,
                               bounds=bounds, 
                               latent_levels=latent_levels))
    
    out = np.hstack(out)
    
    if normalize_noise:
        noise = out - latent_levels_1d
        sd_levels = np.unique(noise_levels_1d)
 
        for sd_level in sd_levels:
            issd = noise_levels_1d == sd_level
            # print(f"before: {np.std(noise[issd]):0.3f}")
            noise[issd] = (noise[issd] / np.std(noise[issd])) * sd_level
            # print(f"after: {np.std(noise[issd]):0.3f}")
            # something about this is wrong but idk what: it's not exactly at the SD level.. 
        out = latent_levels_1d + noise
        
        if bounds is not None:
            is_outofbounds = ~np.array([bounds[0] < o < bounds[1] for o in out])
            if np.any(is_outofbounds):
                to_replace = [gen_outcome(ll, sd, 
                                          bounds=bounds, 
                                          latent_levels=latent_levels)
                              for ll, sd in zip(latent_levels_1d[is_outofbounds],
                                                noise_levels_1d[is_outofbounds])]
                    
                out[is_outofbounds] = to_replace
                
    return out
    

def gen_outcome_sequence(nopt, horizon, latent_levels, sd_levels, vol, 
                         ideal_vol=True, 
                         ncp_range=None,
                         cp_min_from_start=None, 
                         cp_min_to_end=None, 
                         cp_min_dist=None, 
                         cp_min_opt_dist=None, 
                         cp_max_iter=10000, 
                         ll_current=None, 
                         ll_startwith=None, 
                         ll_opt_diff_tol=None,
                         sd_ord_type="fixed", 
                         sd_order=None, 
                         sd_opts_match=True, 
                         out_bounds=None,
                         out_bound_method="regen",
                         ll_mean_tol=None,
                         out_mean_tol=None, 
                         norm_noise=False, 
                         reg_max_iter=10000,
                         output="sequence"):
    """ Generates a sequence of outcomes. See respective functions for full
    info on argument options. Additional inputs: 
        ll_opt_diff_tol = tolerance for similarity / difference between average 
        latent levels across options over the course of a block (proportion of mean diff)
        out_bound_method = regen (regenerate) and in_bounds (sample within 
        bounds) 
        out_mean_tol = tolerance for deviation of actual outcomes from the 
        expected latent level mean, expressed in sds (prop. deviation; scalar)
    
    Note: the bounds can shift this mean(1:100) != mean([30, 50, 70])
    in a way that depends on the SD and levels closeness to bounds 
    
    the resampling can bias toward selecting sequences with more central
    latent levels oversampled
    
    """
    if output == "info":
        args = locals()
    
    if out_mean_tol is not None:
        if ll_mean_tol is None:
            ll_mean_tol = out_mean_tol

        expected_mean = np.mean(latent_levels)
        out_mean_tol_crit = expected_mean * out_mean_tol
    
    sd_levels = np.array(hf.single2array(sd_levels))
    sd_is_per_trial = False
    if len(sd_levels.shape) == 2:
        if sd_levels.shape[-1] == horizon:
            sd_is_per_trial = True
    
    if sd_is_per_trial:
        noise_level_seq = sd_levels 
    else: 
        noise_level_seq = set_sd_sequence(sd_levels, horizon, 
                                          nopt=nopt, 
                                          ord_type=sd_ord_type, 
                                          order=sd_order, 
                                          opts_match=sd_opts_match, 
                                          out_type=output)
    
    latent_level_seq = gen_latent_seq(vol, latent_levels, nopt, horizon, 
                                      ideal_vol=ideal_vol, 
                                      ncp_range=ncp_range,
                                      cp_min_from_start=cp_min_from_start, 
                                      cp_min_to_end=cp_min_to_end, 
                                      cp_min_dist=cp_min_dist, 
                                      cp_min_opt_dist=cp_min_opt_dist, 
                                      cp_max_iter=cp_max_iter, 
                                      ll_current=ll_current, 
                                      ll_startwith=ll_startwith, 
                                      ll_mean_tol=ll_mean_tol,
                                      ll_max_iter=reg_max_iter,
                                      output=output)
    
    # Make sure the average latent levels across options are not too similar
    # (doesn't matter what to choose) or too different (too obvious what to choose)
    if ll_opt_diff_tol is not None:
        mean_ll_diff = np.mean(np.abs(np.diff(np.vstack(
            [[l1, l2] for l1 in latent_levels for l2 in latent_levels]), 1)))
        
        def check_ll_diffs_opt_pairs(lls):
            "lls is an nopt x horizon array"
            if output == "info":
                lls = lls["ll_seq"]

            ll_diff = []
            for o1 in range(nopt):
                for o2 in range(nopt):
                    if o1 != o2:
                        ll_diff.append(np.abs(lls[o1] - lls[o2]))
            
            return np.mean(np.vstack(ll_diff))
        
        ll_diff = check_ll_diffs_opt_pairs(latent_level_seq)
        
        while ll_diff < ll_opt_diff_tol * mean_ll_diff:
            latent_level_seq = gen_latent_seq(vol, latent_levels, nopt, horizon, 
                                              ideal_vol=ideal_vol, 
                                              ncp_range=ncp_range,
                                              cp_min_from_start=cp_min_from_start, 
                                              cp_min_to_end=cp_min_to_end, 
                                              cp_min_dist=cp_min_dist, 
                                              cp_min_opt_dist=cp_min_opt_dist, 
                                              cp_max_iter=cp_max_iter, 
                                              ll_current=ll_current, 
                                              ll_startwith=ll_startwith, 
                                              ll_mean_tol=ll_mean_tol,
                                              ll_max_iter=reg_max_iter,
                                              output=output)
            
            ll_diff = check_ll_diffs_opt_pairs(latent_level_seq)
    
    if output == "sequence":
        lls = latent_level_seq
        nls = noise_level_seq
    elif output == "info":
        lls = latent_level_seq["ll_seq"]
        if not sd_is_per_trial:
            nls = noise_level_seq["sd_seq"]
        else:
            nls = noise_level_seq
    
    if out_bound_method == "in_bounds":
        latent_levels_resample = latent_levels
    else:  # if it's None or regen
        latent_levels_resample = None
    
    outcomes = []
    for iopt in range(nopt):
        outcomes.append(sample_outcomes(lls[iopt], nls[iopt], 
                                        bounds=out_bounds, 
                                        latent_levels=latent_levels_resample, 
                                        normalize_noise=norm_noise))
        resample = False
        if out_mean_tol is not None:
            resample = np.abs(
                np.mean(outcomes[-1]) - expected_mean) > out_mean_tol_crit
        
        n_out_iter = 0
        while resample and (n_out_iter <= reg_max_iter):
            outcomes[-1] = sample_outcomes(lls[iopt], nls[iopt], 
                                           bounds=out_bounds, 
                                           latent_levels=latent_levels_resample,
                                           normalize_noise=norm_noise)
            resample = False
            if out_mean_tol is not None:
                resample = np.abs(
                    np.mean(outcomes[-1]) - expected_mean) > out_mean_tol_crit
            
            n_out_iter += 1
    
    outcomes = np.stack(outcomes, 1).T
    if output == "info":
        if not sd_is_per_trial:
            out = {**latent_level_seq, **noise_level_seq}
        else:
            out = latent_level_seq
            out["sd_seq"] = noise_level_seq
        
        out["out_seq"] = outcomes
        
        out["args"] = args
        
    else:
        out = outcomes
    
    return out


# %% Generate with the actual generative prrocess (no constraints)
def get_transmat(vol, n_latent_levels, cov="eye"):
    transmat = np.eye(n_latent_levels) * (1 - vol)
    if cov == "eye":
        row = vol / (n_latent_levels - 1)
        transmat[transmat==0] = row
    
    return transmat


def gen_outcomes_generative_process(horizon, latent_levels, sd_levels, 
                                    vol=None, transmat=None, 
                                    prior0_typ="uniform", prior=None, 
                                    out_bounds=None, trans_cov="eye"):
    
    """ This implements the generative process exactly, using the transition
    matrix (ie, the sampled latent levels can be non-iid depending on the
    transmat specification)
    Constraints on sequence generation can be added here (on changepoints, 
    outcome bounding, etc.)
    
    vol and transmat can't both be none. 
    
    prior is the reward levels prior (typically, for now, either uniform for 
    trial 0 or the transmat row at the current reward level) 
    """
    
    nlat = len(hf.single2array(latent_levels))
    # vol and transmat can't both be none
    if vol is None:
        vol = 1-transmat[0]
    
    if transmat is None: 
        transmat = get_transmat(vol, nlat, cov=trans_cov)
    
    if prior is None:
        if prior0_typ == "uniform":
            prior = (1 / nlat) * np.ones(nlat)

    lat = hf.single2array(sample_latent_level(latent_levels, probs=prior))
    out = hf.single2array(single_outcome(lat, sd_levels[0], bounds=out_bounds))
    for it in range(horizon):
        latflag = latent_levels == lat[-1]
        probs = transmat @ latflag
        lat.append(sample_latent_level(latent_levels, probs=probs))
        out.append(single_outcome(lat[-1], sd_levels[it], bounds=out_bounds))
    
    return lat, out


# %% Forced trials
def gen_rand_choice(nopt, probs=None):
    "probs is a vector of length nopt"
    if probs is None:
        return npr.choice(nopt)
    else:
        return npr.choice(nopt, p=probs)
    

def get_forced_idx(horizon, length, period, n_from_start=None, output="idx"):
    "output options: idx, bool, info"

    
    orig_horizon = horizon
    if n_from_start is not None:
        horizon = horizon - n_from_start
    
    nalt = int(horizon / period)  # int rounds down; nalt is # of forced-free periods 
    forced_seg_idx = np.arange(horizon, step=period)[:nalt]
    forced_trial_idx = np.hstack([np.arange(idx, stop=idx+length) for idx in forced_seg_idx])
    
    if n_from_start is not None:
        forced_trial_idx = forced_trial_idx + n_from_start
    
    
    forced_trial_bool = np.zeros(orig_horizon).astype(bool)
    forced_trial_bool[forced_trial_idx] = True
    
    if output == "bool":
        forced_trials = forced_trial_bool
    elif output == "idx":
        forced_trials = forced_trial_idx
    elif output == "info":
        forced_trials = {"forced_bool": forced_trial_bool, 
                         "forced_idx": forced_trial_idx, 
                         "forced_nalt": nalt}
    
    return forced_trials

    
def get_rand_choice_seq(nopt, length):
    return np.array([gen_rand_choice(nopt) for _ in range(length)])
    
    
def gen_forced_seq(nopt, horizon, length, period, n_from_start=None, 
                   max_same_choice=None, output="sequence"):
    "output options are sequence, info"
    if output == "info":
        args = locals()
    
    forced = get_forced_idx(horizon, length, period, n_from_start=n_from_start, 
                            output="info")
    idx = forced["forced_idx"] 
    nseg = forced["forced_nalt"]
    
    choices = []
    for seg in range(nseg):
        choices.append(get_rand_choice_seq(nopt, length))
        if max_same_choice is not None:
            n_per_opt = np.array([np.sum(choices[-1] == opt) 
                                  for opt in range(nopt)])
            
            while np.any(n_per_opt > max_same_choice):
                choices[-1] = get_rand_choice_seq(nopt, length)
                n_per_opt = np.array([np.sum(choices[-1] == opt) 
                                      for opt in range(nopt)])
    
    choices_per_seg = np.vstack(choices)
    choices = np.hstack(choices)
    
    seq = np.nan * np.ones(horizon)
    seq[idx] = choices
    
 
    if output == "sequence":
        forced = seq
    elif output == "info": 
        forced["forced_seq"] = seq
        forced["forced_choices_per_seg"] = choices_per_seg
        forced["forced_choices"] = choices
        
    return forced


def get_obs_seq(seq, choices):
    """ when choices are made (incl. forced choices), keep just the entries in 
    the sequence which were observed 
    
    seq is either 1d array of outcomes on all options on a single time or 
    a 2d mat of outcomes x trials choices is a 0/1d - integer index of seq, w/ 
    length ntrials
    """
    seq = np.array(seq)
    if len(seq.shape) == 1:
        obs = np.nan * np.ones_like(seq)
        c = hf.single2array(choices)
        obs[c] = seq[c] 
    else:
        horizon = seq.shape[1]
        obs = []
        for it in range(horizon): # zip(seq.T, choices.T):
            if not np.isnan(choices[it]):
                c = int(choices[it])
                s = np.nan * np.ones_like(seq[:, it])
                s[c] = seq[c, it]
                obs.append(s)
            else:
                obs.append(seq[:, it])

    return np.vstack(obs).T


#TODO --> in saver class ? 
# %% Plotting and saving 
def make_seq_id_seed(randseed, seq_iter=None):
    if seq_iter is not None:
        seqid = f"seq{randseed}_{seq_iter}"
    else:
        seqid = f"seq{randseed}"
        
    return seqid


def plot_sequence(latent_levels, horizon, out_range, ll_seq=None, 
                  out_seq=None, forced_choices=None,  choices=None, # sd_seq=None, 
                  forced_len=None, forced_period=None, forced_offset=None, 
                  cmap=None, xtick_period=None, ax_fontsize=14, 
                  label_fontsize=16, lw_ll=1, lw_out=0.6, obs_sz=4, 
                  forced_style="x", choice_style="o",
                  fig_height=3, fig_width=10, seqid=None, 
                  savedir=None, ext=".jpg", dpi=300):
    

    if cmap is None:
        cmap = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    fig, ax = plt.subplots()
    fig.set_figheight(fig_height)
    fig.set_figwidth(fig_width)
    
    ylim = [out_range[0]-1, out_range[1]+2]
    ax.set_ylim(ylim)
    ax.set_yticks(latent_levels)
    ax.set_yticklabels(latent_levels, fontsize=ax_fontsize)
    
    ylabel = ""
    if out_seq is not None:
        ylabel = "outcomes"
    else:
        if ll_seq is not None:
            ylabel = "latent levels"
        
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    
    if xtick_period is None:
        xtick_period = 10
    ax.set_xlim([0, horizon])
    x = np.arange(0, horizon, xtick_period)
    ax.set_xticks(x)
    ax.set_xticklabels(x, fontsize=ax_fontsize)
    
    if forced_len is not None:
        forced_ons = np.arange(0, horizon, forced_period)
        for fseg in forced_ons:
            ax.add_patch(Rectangle(
                (fseg, 0), forced_len-1, ylim[1], fc=(0.5, 0.5, 0.5), ec='none', alpha=0.5))
            # ax.axvline(x=48, color=(0, 0, 0), lw=3)
    
    if ll_seq is not None:
        for i, o in enumerate(ll_seq):
            plt.plot(o, c=cmap[i], linewidth=lw_ll)
    
    if out_seq is not None:
        for i, o in enumerate(out_seq):
            plt.plot(o, "--", c=cmap[i], linewidth=lw_out)
            
    if forced_choices is not None:
        obs = np.nan * np.ones_like(out_seq)
        for i in range(horizon):
            if ~np.isnan(forced_choices[i]):
                obs[int(forced_choices[i]), i] = out_seq[int(forced_choices[i]), i]
        for i, o in enumerate(obs):
            # plt.scatter(np.arange(horizon), o, marker="o", c=cmap[i], s=8)
            plt.plot(np.arange(horizon), o, forced_style, c=cmap[i], markersize=obs_sz)
    
    if seqid is not None:
        ax.set_title(seqid, fontsize=label_fontsize)
        
    if savedir is not None:
        previous = len(glob(op.join(savedir, f"{seqid}*{ext}")))
        idx = previous + 1
        savepath = op.join(savedir, f"{seqid}_v{idx}{ext}")
        fig.savefig(savepath, dpi=dpi, bbox_inches = 'tight')
        

def save_sequence(seq_with_info, savename, savedir, forced=None):
    previous = len(glob(op.join(savedir, f"{savename}*.p")))
    idx = previous + 1
    savepath = op.join(savedir, f"{savename}_v{idx}.p")
    
    seq_full = {"seq_info": seq_with_info, 
                "forced": forced}
    if forced is not None:
        if type(forced) == dict:
            forced_seq = forced["forced_seq"]
        else:
            forced_seq = forced
    else:
        forced_seq = np.nan * np.ones(seq_with_info["out_seq"].shape[1])
        
    seq_full["seq"] = get_obs_seq(seq_with_info["out_seq"], forced_seq)
    
    pickle.dump(seq_full, open(savepath, "wb"))

