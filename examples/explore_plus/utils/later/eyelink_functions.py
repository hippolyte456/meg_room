#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Useful functions to handle EyeLink with Expyriment.

Script adapted from Oliver Lindemann's code.
https://gist.github.com/lindemann09/ad09d9d685e782349cfb

"""

import gc
import pylink 
from pylink import getEYELINK
import shutil
import os


def init_eyelink(exp, dummy=False):
    """
    Initializes the eyetracker for the experiment. 

    Parameters
    ----------
    exp : expyriment experiment
        The experiment object

    dummy : bool
        should tracker run in dummy mode
        
    Returns
    -------
    tracker : EyeLink object
        the tracker object
    edfFileName : str
        name of the EDF file

    """
    if dummy:
        tracker = pylink.EyeLink(None)
    else:
        tracker = pylink.EyeLink("100.1.1.1") #defaults to tracker address "100.1.1.1"

    screen_size = exp.screen.size
    SCN_WIDTH = screen_size[0]
    SCN_HEIGHT = screen_size[1]
    # pylink.openGraphics((screen_size[0], screen_size[1]), 32)
    # disp = pylink.getDisplayInformation()
    # SCN_WIDTH = disp.width
    # SCN_HEIGHT = disp.height


    # experimental code
    exp_code = exp.experiment_info[0]
    
    # subject and session number
    if exp.subject is not None: # not in developer mode
        subject_code = str(exp.subject)
        
        fileslist = os.listdir(f'data/subj_{subject_code}')
        isxpd = ['.xpd' in f for f in fileslist]
        session_code = sum(isxpd)
        session_code = str(session_code)
    else:
        subject_code = "XX"
        session_code = "XX"
    
        
    # filename    
    edfFileName = exp_code + subject_code + "_" + session_code + ".edf"
    #print edfFileName
    pylink.getEYELINK().openDataFile(edfFileName)
    
    pylink.flushGetkeyQueue() #gets rid of old keys from the tracker key queue
    pylink.getEYELINK().setOfflineMode()                      

    # screen_size = exp.screen.size
    #print screen_size
    # left, top, right, bottom coordinates:
        
    # test_screen_size = (160, 120)
    # pylink.getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %(test_screen_size[0] - 1, test_screen_size[1] - 1))
    # pylink.getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" %(test_screen_size[0] - 1, test_screen_size[1] - 1))
    
    pylink.getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %(SCN_WIDTH - 1, SCN_HEIGHT - 1))
    pylink.getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" %(SCN_WIDTH - 1, SCN_HEIGHT - 1))
    
    # pylink.getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %(screen_size[0] - 1, screen_size[1] - 1))
    
    # pylink.getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" %(screen_size[0] - 1, screen_size[1] - 1))
    # pylink.getEYELINK().sendCommand("screen_pixel_coords =  %d %d %d %d" %(-screen_size[0]/2 + 1, screen_size[1]/2 - 1, 
    #                                                                       screen_size[0]/2 - 1, -screen_size[1]/2 + 1))
    # pylink.getEYELINK().sendMessage("DISPLAY_COORDS  %d %d %d %d" %(-screen_size[0]/2 + 1, screen_size[1]/2 - 1, 
    #                                                                       screen_size[0]/2 - 1, -screen_size[1]/2 + 1))

    tracker_software_ver = 0
    eyelink_ver = pylink.getEYELINK().getTrackerVersion()
    if eyelink_ver == 3:
        tvstr = pylink.getEYELINK().getTrackerVersionString()
        vindex = tvstr.find("EYELINK CL")
        tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))    

    if eyelink_ver>=2:
        pylink.getEYELINK().sendCommand("select_parser_configuration 0")
    if eyelink_ver == 2: #turn off scenelink camera stuff
        pylink.getEYELINK().sendCommand("scene_camera_gazemap = NO")
    else:
        pylink.getEYELINK().sendCommand("saccade_velocity_threshold = 35")
        pylink.getEYELINK().sendCommand("saccade_acceleration_threshold = 9500")
    
    # set EDF file contents 
    pylink.getEYELINK().sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
    if tracker_software_ver>=4:
        pylink.getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")
    else:
        pylink.getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")

    # set link data (used for gaze cursor) 
    pylink.getEYELINK().sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
    if tracker_software_ver>=4:
        pylink.getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
    else:
        pylink.getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")
    #button to accept fixation during drift
    pylink.getEYELINK().sendCommand("button_function %d 'accept_target_fixation'"%(5));
    #pylink.getEYELINK().sendCommand("button_function %d 'accept_target_fixation'"%(pylink.ENTER_KEY));

    # AP COMMENTED OUT
    # bg_col = exp.background_colour
    # fg_col = exp.foreground_colour
    # pylink.setCalibrationColors(fg_col, bg_col)
    
    
    # pylink.setTargetSize(screen_size[0] / 70, screen_size[0] / 300);    #select best size for calibration target
    # pylink.setCalibrationSounds("", "", "");
    # pylink.setDriftCorrectSounds("", "off", "off");
    
    return tracker, edfFileName


def start_recording(disable_gc = False):
    error = getEYELINK().startRecording(1, 1, 1, 1) #0 if successful, takes 10-30 ms for recording to begin
    print('got thru startRecording\n')
    #print getEYELINK().getTrackerMode()
    if error:
        print ("ERROR: Could not start Recording!")
        exit()

    if disable_gc:
        gc.disable() #disable python garbage collection to avoid delays
    
    # AP: commented out - cause of error? 
    pylink.beginRealTimeMode(100) #sets system priority highest (for windows?) and waits 100 ms
    print('got thru beginRealTimeMode\n')
    #wait for sample data via link for max 1000 ms
    if not getEYELINK().waitForBlockStart(1000,1,0): #returns true if data available
        end_recording()
        print ("ERROR: No link samples received!")
        getEYELINK().sendMessage("TRIAL ERROR")
        return 
    print('got thru waitForBlockStart\n')
    
    #try to get rid of pylink graphics
    pylink.closeGraphics()


def end_eyelink(exp, edfFileName):
    '''
    Cleanup and close tracker.
    '''
    # subject number
    if exp.subject is not None: # not in developer mode
        # subject_code = str(exp.subject)[0:-2]
        subject_code = str(exp.subject)
    else:
        subject_code = "XX"
        
    if pylink.getEYELINK() != None:
        # File transfer and cleanup!
        pylink.getEYELINK().setOfflineMode();                          
        pylink.msecDelay(500);                 

        #Close the file and transfer it to Display PC
        pylink.getEYELINK().closeDataFile()
        pylink.getEYELINK().receiveDataFile(edfFileName, edfFileName)
        shutil.move(edfFileName, f"data/subj_{subject_code}")
        pylink.getEYELINK().close();
        pylink.closeGraphics()


def end_recording(enable_gc = True):
    '''
    Ends recording: adds 100 msec of data to catch final events
    '''
    pylink.getEYELINK().sendMessage("REC_STOP");
    pylink.endRealTimeMode();  #set system priority back to normal (still slightly higher though)
    pylink.pumpDelay(100);       
    pylink.getEYELINK().stopRecording();
    #process and dispatch any waiting messages:
    while pylink.getEYELINK().getkey() : #0 if no key pressed
        pass;
    if enable_gc:
        gc.enable() #re-enable python garbage collection to do memory cleanup at the end of trial

