

from math import atan2, degrees, copysign
from expyriment import stimuli
import expyriment as expy

from utils.CBandit_parameters import *

def rating_block(exp, cueLeft, cueRight, whichCue, qsTitle):
    # Initial screen
    expy.stimuli.BlankScreen().present()
    qsTitle.present()
    exp.clock.wait(Q_GAP*1000)
    # Questions   
    keyQ1_val, rtQ1_val, keyQ1_conf, rtQ1_conf = ratings(exp, cueLeft, cueRight, whichCue)
    if rtQ1_val == None:
        rtQ1_val, rtQ1_conf = TOT_TIME_Q*1000, 0
    elif rtQ1_conf == None:
        rtQ1_conf = TOT_TIME_Q*1000 - rtQ1_val

    keyQ2_val, rtQ2_val, keyQ2_conf, rtQ2_conf = ratings(exp, cueLeft, cueRight, 1-whichCue, currTime= rtQ1_conf+rtQ1_val)
    if rtQ2_val == None:
        rtQ2_val, rtQ2_conf = TOT_TIME_Q*1000 - (rtQ1_conf+rtQ1_val), 0
    elif rtQ2_conf == None:
        rtQ2_conf = TOT_TIME_Q*1000 - (rtQ2_val + rtQ1_conf+rtQ1_val)

    if IS_FMRI:
        exp.clock.wait(TOT_TIME_Q*1000 - (rtQ1_conf + rtQ1_val + rtQ2_val + rtQ2_conf))

    # Final screen
    expy.stimuli.BlankScreen().present()
    exp.clock.wait(Q_GAP*1000)
    
    return keyQ1_val, rtQ1_val, keyQ1_conf, rtQ1_conf, keyQ2_val, rtQ2_val, keyQ2_conf, rtQ2_conf


def ratings(exp, cueLeft, cueRight, whichCue, currTime=0): 
    '''
    Function to present the rating scales and collect responses in expyriment.
    '''
    
    valuePrompt = stimuli.TextLine("Estimation de la valeur",
                                   position=(0,POS_RATE_PROMPT),
                                   text_size=FONT_SIZE,
                                   text_font=EXP_FONT)
    confPrompt = stimuli.TextLine("Confiance",
                                  position=(0,POS_RATE_PROMPT),
                                  text_size=FONT_SIZE,
                                  text_font=EXP_FONT)
    #___________________________________________________________________________
    # VALUE 
    valueOptsText = VALUES
    n_valueOpts, valueOpts, valueOptsChoice = choseAndPreload_ValueOpts(valueOptsText)
    dict_keys_valOpts = { KEYS_VAL[i]: valueOptsChoice[i] for i in range(len(valueOptsText))}

    #___________________________________________________________________________
    # CONFIDENCE   
    confOptsTextEnds = ['Pas confiant', 'Très confiant']
    confOptsText = ['0','1','2','3']
    n_confOpts = 4
    n_confEnds = 2
    confOpts = []
    confOptsChoice = []
    confOptsEnds = []
    for endpt in range(n_confEnds):
        confOptsEnds.append(stimuli.TextLine(confOptsTextEnds[endpt],
                                            position=(POS_RATE_OPTIONS_ENDS[endpt],POS_RATE_OPTIONS_VERT),
                                            text_size=FONT_SIZE,
                                            text_font=EXP_FONT))
        confOptsEnds[endpt].preload()
        
    for opt in range(n_confOpts):
        position = get_positions(n_confOpts,opt)     
        confOpts.append(stimuli.TextBox(confOptsText[opt], (RATE_SIZE, RATE_SIZE),
                                    position = position,
                                    # position=(POS_RATE_OPTIONS_HORZ_4[opt], POS_RATE_OPTIONS_VERT),
                                    text_size=FONT_SIZE,
                                    text_font=EXP_FONT,
                                    background_colour=GRAY))
        confOptsChoice.append(stimuli.Rectangle((RATE_SIZE_FRAME, RATE_SIZE_FRAME),
                                    position= position,
                                    #position=(POS_RATE_OPTIONS_HORZ_4[opt],POS_RATE_OPTIONS_VERT),
                                    colour=BLACK,
                                    line_width=RATE_LINE_FRAME))
        confOpts[opt].preload()
        confOptsChoice[opt].preload()
    
    #___________________________________________________________________________
    # VALUE
    if whichCue == 0:
        cueLeft.present()
    elif whichCue == 1:
        cueRight.present()
    # Show the "title" (Value guess)
    valuePrompt.present(clear=False)
    # Show the response options
    for opt in range(n_valueOpts):
        valueOpts[opt].present(clear=False)
   
    # Register response
    key_val, rt_val = exp.keyboard.wait_char(KEYS_VAL, duration = 1 + TOT_TIME_Q*1000 - currTime)
    if rt_val != None:
        currTime += rt_val
        dict_keys_valOpts[key_val].present(clear=False)
        stimuli.BlankScreen().present()
    else:
        currTime = TOT_TIME_Q*1000
    

    
    #___________________________________________________________________________
    # CONFIDENCE #TODO --> faire le gain en modularité ici aussi ?
    if whichCue == 0:
        cueLeft.present()
    elif whichCue == 1:
        cueRight.present()
    
    # Show the "title" (Confidence)
    confPrompt.present(clear=False) 
    # Show the end points of the scale (not at all - totally)
    for endpt in range(n_confEnds):
        confOptsEnds[endpt].present(clear=False)
    # Show the response options
    for opt in range(n_confOpts):
        confOpts[opt].present(clear=False)
    
    
    key_conf, rt_conf = exp.keyboard.wait_char(KEYS_CONF, duration= 1 + TOT_TIME_Q*1000 - currTime)
    if rt_conf != None:
        currTime += rt_conf
        # dict_keys_valOpts[key_val].present(clear=False)
        stimuli.BlankScreen().present()
        if key_conf == KEYS_CONF[0]:
            confOptsChoice[0].present(clear=False)
        elif key_conf == KEYS_CONF[1]:
            confOptsChoice[1].present(clear=False)
        elif key_conf == KEYS_CONF[2]:
            confOptsChoice[2].present(clear=False)
        elif key_conf == KEYS_CONF[3]:
            confOptsChoice[3].present(clear=False)
        stimuli.BlankScreen().present() 
    return key_val, rt_val, key_conf, rt_conf


def MEG_rating_block(exp, cueLeft, cueRight, whichCue, qsTitle, MEGport, response_meg):
    # Initial screen
    expy.stimuli.BlankScreen().present()
    qsTitle.present()
    startQuestion = exp.clock.stopwatch_time
    MEGport.send(data = 16)                            ##6questionScreen
    exp.clock.wait(durationTriggers) 
    MEGport.send(data = 0)
    
    exp.clock.wait(Q_GAP*1000)
    # Questions   stimVal1, stimVal2, stimConf1, stimConf2 are the timing of the questions
    keyQ1_val, rtQ1_val, keyQ1_conf, rtQ1_conf, stimVal1, stimConf1 = MEG_ratings(exp, cueLeft, cueRight, whichCue, MEGport, response_meg)
    keyQ2_val, rtQ2_val, keyQ2_conf, rtQ2_conf, stimVal2, stimConf2 = MEG_ratings(exp, cueLeft, cueRight, 1-whichCue, MEGport, response_meg)
    # Final screen
    expy.stimuli.BlankScreen().present()
    exp.clock.wait(Q_GAP*1000)
    
    return keyQ1_val, rtQ1_val, keyQ1_conf, rtQ1_conf, keyQ2_val, rtQ2_val, keyQ2_conf, rtQ2_conf, stimVal1, stimConf1, stimVal2, stimConf2, startQuestion


def MEG_ratings(exp, cueLeft, cueRight, whichCue, MEGport, response_meg): 
    '''
    Function to present the rating scales and collect responses in expyriment.
    '''
    
    valuePrompt = stimuli.TextLine("Estimation de la valeur",
                                   position=(meg_pos,POS_RATE_PROMPT),
                                   text_size=FONT_SIZE,
                                   text_font=EXP_FONT)
    confPrompt = stimuli.TextLine("Confiance",
                                  position=(meg_pos,POS_RATE_PROMPT),
                                  text_size=FONT_SIZE,
                                  text_font=EXP_FONT)
    #___________________________________________________________________________
    # VALUE 
    valueOptsText = VALUES
    n_valueOpts, valueOpts, valueOptsChoice = choseAndPreload_ValueOpts(valueOptsText)
    dict_keys_valOpts = { KEYS_VAL[i]: valueOptsChoice[i] for i in range(len(valueOptsText))}

    #___________________________________________________________________________
    # CONFIDENCE   
    confOptsTextEnds = ['Pas confiant', 'Très confiant']
    confOptsText = ['0','1','2','3']
    n_confOpts = 4
    n_confEnds = 2
    confOpts = []
    confOptsChoice = []
    confOptsEnds = []
    for endpt in range(n_confEnds):
        confOptsEnds.append(stimuli.TextLine(confOptsTextEnds[endpt],
                                            position=(POS_RATE_OPTIONS_ENDS[endpt]+meg_pos,POS_RATE_OPTIONS_VERT),
                                            text_size=FONT_SIZE,
                                            text_font=EXP_FONT))
        confOptsEnds[endpt].preload()        
    for opt in range(n_confOpts):
        position = get_positions(n_confOpts,opt)     
        confOpts.append(stimuli.TextBox(confOptsText[opt], (RATE_SIZE, RATE_SIZE),position = (position[0]+meg_pos,position[1]),text_size=FONT_SIZE,text_font=EXP_FONT,background_colour=GRAY))
        confOptsChoice.append(stimuli.Rectangle((RATE_SIZE_FRAME, RATE_SIZE_FRAME),position= (position[0]+meg_pos,position[1]),colour=BLACK,line_width=RATE_LINE_FRAME))
        confOpts[opt].preload()
        confOptsChoice[opt].preload()
    
    #___________________________________________________________________________
    # VALUE
    if whichCue == 0:
        cueLeft.present()
    elif whichCue == 1:
        cueRight.present()
    # Show the "title" (Value guess)
    valuePrompt.present(clear=False)
    # Show the response options
    for opt in range(n_valueOpts):
        valueOpts[opt].present(clear=False)
    timeQval = exp.clock.stopwatch_time
    MEGport.send(data = 16)                            ##7Question
    exp.clock.wait(durationTriggers) 
    MEGport.send(data = 0)
    

     # Register response
    key_val, rt_val = response_meg.wait(duration=3000)  ##8Reponses 
    if key_val not in KEYS_VAL:
        key_val, rt_val = None, None
    print('motor response estim')
    if key_val in KEYS_VAL : 
        dict_keys_valOpts[key_val].present(clear=False)
    stimuli.BlankScreen().present()
    exp.clock.wait(1000)
    

    #___________________________________________________________________________
    # CONFIDENCE 
    if whichCue == 0:
        cueLeft.present()
    elif whichCue == 1:
        cueRight.present()
    
    # Show the "title" (Confidence)
    confPrompt.present(clear=False) 
    # Show the end points of the scale (not at all - totally)
    for endpt in range(n_confEnds):
        confOptsEnds[endpt].present(clear=False)
    # Show the response options
    for opt in range(n_confOpts):
        confOpts[opt].present(clear=False)
    timeQconf = exp.clock.stopwatch_time
    MEGport.send(data = 16)                               ##Question 
    exp.clock.wait(durationTriggers) 
    MEGport.send(data = 0) 
    
    
     # Register response
    key_conf, rt_conf = response_meg.wait(duration=3000)   ##Response
    if key_conf not in KEYS_CONF:
        key_conf, rt_conf = None, None

    print('motor response conf')
    if key_conf in KEYS_CONF : 
        for i, key in enumerate(KEYS_CONF):
            if key_conf == key:
                confOptsChoice[i].present(clear=False)
                break
    stimuli.BlankScreen().present()
    exp.clock.wait(1000)

    return key_val, rt_val, key_conf, rt_conf, timeQval, timeQconf



def choseAndPreload_ValueOpts(valueOptsText):
    '''
    Function to define the rating options in expyriment.
    '''
    n_valueOpts = len(valueOptsText)
    valueOpts = []
    valueOptsChoice = []
    for opt in range(n_valueOpts): 
        position = get_positions(n_valueOpts,opt)                                 
        valueOpts.append(stimuli.TextBox(valueOptsText[opt], (RATE_SIZE, RATE_SIZE),
                                      position=(position[0]+meg_pos,position[1]),
                                      text_size=FONT_SIZE,
                                      text_font=EXP_FONT,
                                      background_colour=GRAY))
        valueOptsChoice.append(stimuli.Rectangle((RATE_SIZE_FRAME, RATE_SIZE_FRAME),
                                                 position=(position[0]+meg_pos,position[1]),
                                                 colour=BLACK,
                                                 line_width=RATE_LINE_FRAME))
        valueOpts[opt].preload()
        valueOptsChoice[opt].preload()
    return n_valueOpts, valueOpts, valueOptsChoice


def get_positions(n_valueOpts,opt):
    ''' 
    Function to define the display positions of the rating options in expyriment.
    '''
    scale = opt/(n_valueOpts - 1) #scale between 0 and 1
    coeff = 2*scale - 1 #coeff between -1 and 1
    pos_rate = 5 * coeff * stim_sizes['stim_rad']  #+ copysign(1,coeff)) * stim_sizes['position']
    return (pos_rate, POS_RATE_OPTIONS_VERT)



