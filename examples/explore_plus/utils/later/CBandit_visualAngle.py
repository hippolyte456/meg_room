#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 22:47:56 2021

@author: apaunov
"""

import os
import numpy as np
from math import atan2, degrees

def define_visual_angle(size_in_deg, disp_height, disp_dist, disp_res):
    # define the width of the display
    prop_dist_center = 0.6 # distance of the stim from center, as prop of radius
    
    #ie total width is the diameter of the 2 circles + their distance
    stim_width_num_radii = (2+prop_dist_center) * 2
    
    #get the number of pixels in the given degrees
    deg_per_pix = degrees(atan2(.5*disp_height, disp_dist)) / (.5*disp_res)
    size_in_pix = size_in_deg / deg_per_pix
    
    # Get the radius of the outer circle (frame)
    outer_radius = size_in_pix / stim_width_num_radii
    
    # Get the radius of the inner cirlce
    prop_inner_radius = 0.8 # as proportion of the frame radius
    inner_radius = outer_radius * prop_inner_radius
    
    # Get position
    dist_center = outer_radius * prop_dist_center
    stim_position = dist_center + outer_radius
    
    # Get the radius of the fixation cross
    prop_fix_inner_radius = 0.03 # as proportion of total width
    prop_fix_middle_radius = 0.06
    prop_fix_outer_radius = 0.09
    
    fix_inner_radius = size_in_pix * prop_fix_inner_radius
    fix_middle_radius = size_in_pix * prop_fix_middle_radius
    fix_outer_radius = size_in_pix * prop_fix_outer_radius
    
    prop_fix_line_width = 0.02
    fix_line_width = size_in_pix * prop_fix_line_width
    
    if size_in_deg < 3:
        font_size = 18
    elif size_in_deg >= 3 and size_in_deg < 4:
        font_size = 22
    elif size_in_deg >= 4 and size_in_deg < 5:
        font_size = 26
    
    return {'stim_frame_rad': outer_radius, 
            'stim_rad': inner_radius, 
            'position': stim_position, 
            'fix_center': fix_inner_radius, 
            'fix_middle': fix_middle_radius,
            'fix_outer': fix_outer_radius, 
            'fix_line': fix_line_width,
            'total_size_pix': size_in_pix,
            'font_size': font_size}