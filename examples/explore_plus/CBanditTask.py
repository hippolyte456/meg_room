#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 18 15:54:22 2021
    


*****************
NB: BEFORE RUNNING!!! 
* USE ACTUAL SEQUENCES
* TURN OFF DEV MODE, ETC
*****************

* ADD RECORDING OF 
    - wrong presses on forced trials
    - anticipatory presses 

@author: apaunov, hippolyteD456
"""


import yaml

import time 
import os
import numpy as np
import pandas as pd
import pickle

import expyriment as expy  #control, design, misc, stimuli, io
from utils.CBandit_parameters import *
from utils.rand_counter import *
from utils.ratings import rating_block, MEG_rating_block
import utils.generate_sequence as gs 

from utils.seq_gen import SeqGen
from utils.saver import Saver
from utils.rand_counter import rd_ct
from utils.feedback import Feedback as FB
from utils.parallel_ports import MEG_ports


# =============================================================================
# INITIALISATION
# =============================================================================
expy.control.defaults.window_mode = False

exp = expy.design.Experiment(name="Curious Bandit Task",
                        background_colour=DARK_GRAY,
                        foreground_colour=BLACK)
exp.add_data_variable_names(["BlockID, TrialID, Key, RT, reward, " + 
                              "keyQ1_val, rtQ1_val, keyQ1_conf, rtQ1_conf, " + 
                              "keyQ2_val, rtQ2_val, keyQ2_conf, rtQ2_conf, " + 
                              "trial_start, outcome_start, outcome_dur, " + 
                              "trial_end, trial_dur, SOA, exp_time_elapsed, " ]) 
expy.control.initialize(exp)
trigger = exp.keyboard  # USED FOR BOTH LAPTOP AND KEYBOARD
expy.control.start(skip_ready_screen=True)
saver = Saver(exp)


response_meg = MEG_ports(exp, receive_port1, receive_port2, receive_port3)
MEGport = response_meg.port2


# =============================================================================
# TASK DESIGN: SET UP STIMULI
# =============================================================================

#order of COLORS, QUESTIONS, ARMS
left_color, right_color = rd_ct.set_lf_color()
color_order_this_sess = rd_ct.set_color_order(left_color) 
whichCue = rd_ct.set_cue_order()
arm_id_this_sess = rd_ct.set_arm_id(0)


# NORMAL TRIALS (and initial / final)
fix_center = expy.stimuli.Circle(FIX_0, colour=FIX_COLOR, position=(meg_pos,0))
fix_low = expy.stimuli.Circle(FIX_LOW, colour=FIX_COLOR, position=(meg_pos,0),line_width=FIX_LINE)
fix_high = expy.stimuli.Circle(FIX_HIGH, colour=FIX_COLOR, position=(meg_pos,0),line_width=FIX_LINE)
fix_switch = expy.stimuli.Circle(FIX_HIGH, colour=YELLOW, position=(meg_pos,0),line_width=FIX_LINE)   
fix_center_miss = expy.stimuli.Circle(FIX_0, colour=MISS_FIX_COLOR, position=(meg_pos,0))
fix_low_miss = expy.stimuli.Circle(FIX_LOW, colour=MISS_FIX_COLOR, position=(meg_pos,0),line_width=FIX_LINE)
fix_high_miss = expy.stimuli.Circle(FIX_HIGH, colour=MISS_FIX_COLOR, position=(meg_pos,0),line_width=FIX_LINE)
fix_center.preload()
fix_low.preload()
fix_high.preload()
fix_switch.preload()
fix_center_miss.preload()
fix_low_miss.preload()
fix_high_miss.preload()
# CUES 
cueLeft_frame = expy.stimuli.Circle(CUE_1, colour=left_color, position=(POS_LEFT+meg_pos,0),line_width=4)
cueLeft_mask = expy.stimuli.Circle(CUE_1, colour=DARK_GRAY, position=(POS_LEFT+meg_pos,0),line_width=6)
cueLeft = expy.stimuli.Circle(CUE_0, colour=left_color, position=(POS_LEFT+meg_pos,0))
cueLeft_frame.preload()
cueLeft.preload()
cueLeft_mask.preload()
cueRight_frame = expy.stimuli.Circle(CUE_1, colour=right_color, position=(POS_RIGHT+meg_pos,0),line_width=4)
cueRight_mask = expy.stimuli.Circle(CUE_1, colour=DARK_GRAY, position=(POS_RIGHT+meg_pos,0),line_width=6)
cueRight = expy.stimuli.Circle(CUE_0, colour=right_color, position=(POS_RIGHT+meg_pos,0))
cueRight_frame.preload()
cueRight.preload()
cueRight_mask.preload()
# QUESTIONS
qsTitle = expy.stimuli.TextLine("Questions", position=(meg_pos,0), text_size=FONT_SIZE,text_font=EXP_FONT)


# =======================================================================================
# TASK DESIGN: LOAD OR GENERATE SEQUENCE
# =======================================================================================
seqgen = SeqGen(subID= saver.subject_idx, sessionID=saver.session_idx, blockID=saver.block_idx)
try:   
    block_inputs = seqgen.get_block_input() #GET
    print('block_inputs loaded')
except:
    block_inputs = seqgen.gen_block_input() #GENERATE
    print('BE CAREFUL block_inputs generated, not visually checked')
fb = FB(exp, block_inputs,csv_dir = saver.save_path)
block = expy.design.Block(name=saver.block_name)
seqgen.check_sequence(block_inputs)


# =======================================================================================
# TASK DESIGN: PRE-GENERATE CUE SEQUENCE (LOW/HIGH SD, FREE/FORCED) WITH COUNTERBALANCING
# =======================================================================================
for trial_num in range(N_TRIALS):   
    canvass = expy.stimuli.BlankScreen()
    
    # FIXATION 
    if block_inputs['SD'][trial_num] == LOW_SD:
        fix_low.plot(canvass)
        fix_center.plot(canvass)
        
    elif block_inputs['SD'][trial_num] == HIGH_SD:
        fix_high.plot(canvass)
        fix_low.plot(canvass)
        fix_center.plot(canvass)
    
    # CUES
    if np.isnan(block_inputs['forced'][trial_num]):
        cueLeft_frame.plot(canvass)
        cueLeft.plot(canvass)
        cueRight_frame.plot(canvass)
        cueRight.plot(canvass)
        
    elif block_inputs['forced'][trial_num] == 0: # 0 is left arm *chosen*
        cueLeft_frame.plot(canvass)
        cueLeft.plot(canvass)
        cueRight.plot(canvass)
        
    elif block_inputs['forced'][trial_num] == 1: 
        cueLeft.plot(canvass)
        cueRight_frame.plot(canvass)
        cueRight.plot(canvass)
        
    trial = expy.design.Trial()
    trial.add_stimulus(canvass)
    block.add_trial(trial)

exp.add_block(block)


# =============================================================================
# RUN EXPERIMENT
# =============================================================================

#TODO check this line for MEG initiliazation___________________
expy.stimuli.TextLine("Waiting for trigger...").present()
if IS_FMRI:
    exp.keyboard.read_out_buffered_keys() 
    key, rt = trigger.wait_char(SCAN_TRIGGER)

elif IS_MEG:
    trigger.wait_char(SCAN_TRIGGER)
    print('sending on parallel port the starting')
    MEGport.send(data = 255)
    exp.clock.wait(durationTriggers) #TODO check if necessary
    MEGport.send(data = 0)
    
elif IS_BEHAV:
    trigger.wait_char(SCAN_TRIGGER)

t_trigger = exp.clock.time #TODO understand that 
exp.clock.reset_stopwatch() #reset timer for trial timing
exp_start_time = exp.clock.stopwatch_time # get the start time for checking total session duration
#_______________________________________________________________  


# Initial fixation
if seqgen.sd == LOW_SD:
    expy.stimuli.TextLine("Pour cette séquence, vous vendez à des professionnels.", position = (meg_pos,40), text_size= 40).present()
if seqgen.sd == HIGH_SD:
    expy.stimuli.TextLine("Pour cette séquence, vous vendez à des amateurs.", position = (meg_pos,40),text_size= 40).present()
    
fix_center.present(clear=False)
exp.clock.wait(FIX_DUR * 1000)
expy.stimuli.BlankScreen().present()


#run les 96 trials #TODO faire des fonctions pour chaque partie conditionnelle de la boucle ! ou un decorateur @ ? pour gerer MEG / IRM / BEHAV
for trial, trial_num in zip(block.trials, range(N_TRIALS)):  


    # -------------------------------------------------------------------------
    # CUE AND RESPONSE
    # -------------------------------------------------------------------------
    # Display cue
    trial.stimuli[0].present() 
    # Get time at start of trial
    trial_start = exp.clock.stopwatch_time
    if IS_MEG:
        print('ONSET sent')
        MEGport.send(data = 1)                ## 1STIM 
        exp.clock.wait(durationTriggers)
        MEGport.send(data = 0)
   
    # Wait for response (up to max cue duration)
    free_forced = block_inputs['forced'][trial_num]
    if np.isnan(free_forced): # allow both on free trials
        available_keys =  [LEFT_KEY, RIGHT_KEY] #TODO
    elif free_forced == 0: # forced trial, left required
        available_keys =  [LEFT_KEY,]
    elif free_forced == 1:
        available_keys =  [RIGHT_KEY,]
    else:
        raise KeyError
    
    if IS_FMRI:
        key, rt = exp.keyboard.wait_char(available_keys, duration= CUE_DUR*1000)
    elif IS_MEG:
        key, rt = response_meg.wait(duration=2000) ## 2RESPONSE
        if key not in available_keys:
            key,rt = None, None
    elif IS_BEHAV:
        key, rt = exp.keyboard.wait_char(available_keys)
    else:
        raise KeyError 
    
    print("OOOOOOOOOOH", rt, key)
    # Get arm choice corresponding to key press
    arm_choice = rd_ct.get_arm_choice(key, arm_id_this_sess)
    # Get color corresponding ot the choice
    color_choice = rd_ct.get_color_choice(key, color_order_this_sess)

    
    # -------------------------------------------------------------------------
    # MISSED RESPONSE WINDOW
    # -------------------------------------------------------------------------
    # If the response window missed, show red cross until next trial
    if rt == None: 
        reward = None
        frameOn_start = None
        outcome_start = None 

        current_SD = block_inputs['SD'][trial_num]
        if current_SD == LOW_SD:
            fix_low_miss.present()
            fix_center_miss.present(clear=False)
            
        elif current_SD == HIGH_SD:
            fix_high_miss.present()
            fix_low_miss.present(clear=False)
            fix_center_miss.present(clear=False)
        
        
        
        # record late button presses
        key_miss, rt_miss = exp.keyboard.wait([LEFT_KEY, RIGHT_KEY], duration=((OUT_DUR+ISI)*1000))
        if rt_miss != None:
            print('RT_MISSED:' , rt_miss)
            exp.clock.wait((OUT_DUR+ISI)*1000 - rt_miss)
        
    else: # If response was registered
        # assign values to missed button presses for save
        key_miss = 0
        rt_miss = 0
    
    # ---------------------------------------------------------------------
    # ISI (Inter -Stimulus Interval) (time between cue and outcome)
    # ---------------------------------------------------------------------
    # Show selection without frame
    if key == LEFT_KEY:
        cueLeft_mask.present(clear=False)  
    elif key == RIGHT_KEY:
        cueRight_mask.present(clear=False)
    # Display without frame for ISI and leftover cue duration (adjusted for RT)
    frameOn_start = exp.clock.stopwatch_time
    
    
    if IS_FMRI:
        exp.clock.wait((FRAME_OFF_DUR + CUE_DUR)*1000 - rt)
    if IS_MEG:
        print('FRAMEON sent')
        MEGport.send(data = 2)                 ## 3FRAMEON 
        exp.clock.wait(durationTriggers)
        MEGport.send(data = 0)
        exp.clock.wait((ISI - FRAME_ON_DUR)*1000)
    if IS_BEHAV:
        exp.clock.wait((FRAME_OFF_DUR + CUE_DUR)*1000 - rt)
    
    # Show frame again to signal outcome time
    if key == LEFT_KEY:
        cueLeft_frame.present(clear=False)
        
    elif key == RIGHT_KEY:
        cueRight_frame.present(clear=False)
    
    # Display without frame for ISI and leftover cue duration (adjusted for RT)
    exp.clock.wait(FRAME_ON_DUR*1000)
    
    # ---------------------------------------------------------------------
    # OUTCOME
    # ---------------------------------------------------------------------
    
    # Prepare reward display for the chosen option
    if key == LEFT_KEY:
        reward = int(block_inputs['A'][trial_num])
        rewardText = expy.stimuli.TextLine(str(reward),
                                    position=(POS_LEFT+meg_pos, 0),
                                    text_font=EXP_FONT,
                                    text_size=FONT_SIZE)

    elif key == RIGHT_KEY:
        reward = int(block_inputs['B'][trial_num])
        rewardText = expy.stimuli.TextLine(str(reward),
                                    position=(POS_RIGHT+meg_pos,0),
                                    text_font=EXP_FONT,
                                    text_size=FONT_SIZE)
        
    outcome_start = exp.clock.stopwatch_time
        
    if key != None:
        rewardText.present(clear=False)       
        if IS_MEG:
            print('outcome sent')
            MEGport.send(data = 4)                     ## 4OUTCOME
            exp.clock.wait(durationTriggers)
            MEGport.send(data = 0)
        exp.clock.wait(OUT_DUR*1000) 

        
        
        
    if (rt == None and key != None) or (rt != None and key == None):
        raise ValueError('RT and key are not consistent') #TODO put in test file
    
    
        
    trial_end = exp.clock.stopwatch_time # outcome_dur = trial_end - outcome_start  & trial_dur = trial_end - trial_start
    # -------------------------------------------------------------------------
    # CUE AND RESPONSE
    # -------------------------------------------------------------------------
    if rt != None:
        fix_low.present()
        fix_center.present(clear=False)
        if block_inputs['SD'][trial_num] == HIGH_SD:
            fix_high.present(clear=False)

    
    ITI_start = exp.clock.stopwatch_time  # exp_time_elapsed = exp.clock.stopwatch_time - exp_start_time
    if IS_MEG:
        print('ITI sent')
        MEGport.send(data = 8)                     ## 5ITI_start
        exp.clock.wait(durationTriggers)
        MEGport.send(data = 0)
    exp.clock.wait(ITI[trial_num] * 1000) 
    
    # -------------------------------------------------------------------------
    # RATINGS (once ITI is over)
    # -------------------------------------------------------------------------
    if block_inputs['isQ'][trial_num] == 1:
        if IS_MEG: 
            print('MEG mode')
            ## TODO [in the rating function] send TTL pulse for MEG (except if photodiode is used... change the stimuli) 
            keyQ1_val, rtQ1_val, keyQ1_conf, rtQ1_conf, keyQ2_val, rtQ2_val, keyQ2_conf, rtQ2_conf, stimVal1, stimConf1, stimVal2, stimConf2, startQuestion = MEG_rating_block(exp, cueLeft, cueRight, whichCue, qsTitle, MEGport, response_meg)
        else:
            print('Normal mode')
            keyQ1_val, rtQ1_val, keyQ1_conf, rtQ1_conf, keyQ2_val, rtQ2_val, keyQ2_conf, rtQ2_conf = rating_block(exp, cueLeft, cueRight, whichCue, qsTitle)
        
    else:
        keyQ1_val = 0
        rtQ1_val = 0
        keyQ1_conf = 0
        rtQ1_conf = 0
        
        keyQ2_val = 0
        rtQ2_val = 0
        keyQ2_conf = 0
        rtQ2_conf = 0

        stimVal1 = 0
        stimConf1 = 0
        stimVal2 = 0
        stimConf2 = 0
        startQuestion = 0
    
    # TODO move it to saving class
    if not IS_MEG:
        startQuestion, stimVal1, stimConf1, stimVal2, stimConf2 = 0, 0, 0, 0, 0
    data_add = pd.DataFrame({'BlockID': saver.block_name,'TrialID': trial.id,
                            'arm_choice': arm_choice,'color_choice': color_choice, 'Key': key, 'key_miss': key_miss, 'reward': reward,  
                            'keyQ1_val': keyQ1_val, 'keyQ1_conf': keyQ1_conf, 'keyQ2_val': keyQ2_val, 'keyQ2_conf': keyQ2_conf,
                            'startQuestion': startQuestion, 'stimVal1': stimVal1, 'stimConf1': stimConf1, 'stimVal2': stimVal2, 'stimConf2': stimConf2,
                            'rtQ1_val': rtQ1_val, 'rtQ1_conf': rtQ1_conf, 'rtQ2_val': rtQ2_val, 'rtQ2_conf': rtQ2_conf,
                            'trial_start': trial_start,'RT': rt, 'rt_miss': rt_miss,'frameOn_start':frameOn_start,'outcome_start': outcome_start, 'trial_end': trial_end, 'ITI_start': ITI_start,
                            'A': block_inputs['A'][trial_num],'B': block_inputs['B'][trial_num],
                            'outcome_SD': block_inputs['SD'][trial_num],'forced': block_inputs['forced'][trial_num],
                            'A_mean': block_inputs['A_mean'][trial_num],'B_mean': block_inputs['B_mean'][trial_num],
                            'isQ': block_inputs['isQ'][trial_num], 'ITI': ITI[trial_num], 'rdSeed': seqgen.rdSeed,
                            }, index=[0])


    
    saver.save(data_add)
   

# -----------------------------------------------------------------------------
# END SESSION
# -----------------------------------------------------------------------------
## TODO send TTL pulse for MEG (except if photodiode is used... change the stimuli)
# Final fixation
fb.display_total_gain()
fix_center.present()
exp.clock.wait(FIX_DUR * 1000)
exp_end = exp.clock.stopwatch_time
fb.show(duration=15000) #TODO understand the bug in MRI mode
expy.control.end()
