#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author : HippolyteD456

This class contains functions use to counterbalance and randomize some modalities of the experiment.
'''

import random as rd 
from utils.CBandit_parameters import *

class rd_ct:
    def __init__(self, seed=1):
        self.seed = seed
        self.counter = 0
    
    def set_lf_color():
        p = rd.random()
        if p < 0.5:
            left_color = CUE_PURPLE
            right_color = CUE_ORANGE
        else:
            left_color = CUE_ORANGE
            right_color = CUE_PURPLE
        return left_color, right_color
    
    def set_color_order(left_color):
        if left_color == CUE_PURPLE:
            color_order = 'PO'
        else:
            color_order = 'OP'
        return color_order

    def set_cue_order():
        p = rd.random()
        if p < 0.5:
            whichCue = 1
        else:
            whichCue = 0
        return whichCue                
        
    def set_arm_id(subject_id):
        if subject_id % 2 == 0:
            arm_id = 'normal'
        else:
            arm_id = 'flipped'
        return arm_id


    def get_arm_choice(key, arm_id_this_sess): 
        if arm_id_this_sess == 'flipped':
            if key == LEFT_KEY:
                arm_choice = 'B'
            elif key == RIGHT_KEY:
                arm_choice = 'A'
            else:
                arm_choice = 'NA'
                
        elif arm_id_this_sess == 'normal':
            if key == LEFT_KEY:
                arm_choice = 'A'
            elif key == RIGHT_KEY: 
                arm_choice = 'B'
            else:
                arm_choice = 'NA'
        return arm_choice
        
    def get_color_choice(key, color_order_this_sess):            
        if color_order_this_sess == 'PO':
            if key == LEFT_KEY:
                color_choice = 'P'
            elif key == RIGHT_KEY:
                color_choice = 'O'
            else:
                color_choice = 'NA'
        elif color_order_this_sess == 'OP':
            if key == LEFT_KEY:
                color_choice = 'O'
            elif key == RIGHT_KEY:
                color_choice = 'P'
            else:
                color_choice = 'NA'
        return color_choice