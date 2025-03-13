#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 17:53:36 2021

@author: apaunov
"""

which_color = 'orange'

# import sounddevice as sd
from expyriment import control, design, misc, stimuli

# =============================================================================
# COLORS
# =============================================================================
# Background
DARK_GRAY = (96, 96, 96)
# CUE_PURPLE = (161, 50, 162) # ORIGINAL
# CUE_PURPLE = (130, 30, 130) #USED ON LINUX
CUE_PURPLE = (126, 30, 126)
# CUE_ORANGE = (195, 63, 6) # ORIGINAL
# CUE_ORANGE = (180, 50, 6) #USED ON LINUX
CUE_ORANGE = (150, 38, 6)
BLACK = (0, 0, 0)

# WITH THE ABOVE, LUMINANCE METER SAYS LUM ~15-15.5 (LUX) FOR ALL 

if which_color == 'gray':
    TEST_COLOR = DARK_GRAY
elif which_color == 'purple':
    TEST_COLOR = CUE_PURPLE
elif which_color == 'orange':
    TEST_COLOR = CUE_ORANGE

# =============================================================================
# OTHER CONSTANTS
# =============================================================================
END_CHAR = "e"

# =============================================================================
# INITIALISATION
# =============================================================================

# control.set_develop_mode(False)

exp = design.Experiment(name="Test_Screen_Color",
                        background_colour=TEST_COLOR,
                        foreground_colour=BLACK)


control.initialize(exp)

trigger = exp.keyboard

# =============================================================================
# START THE EXPERIMENT
# =============================================================================

# Start Experiment
control.start(skip_ready_screen=True)
stimuli.TextLine(".").present()
trigger.wait_char(END_CHAR)


control.end()
