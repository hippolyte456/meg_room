if IS_EYELINK:
    from BehavioralTask.utils.later.eyelink_functions import init_eyelink, end_eyelink, end_recording, start_recording
    from pylink import getEYELINK
elif IS_TOBII: 
    import tobii_research as tobii


#################################################
if CALL_EXPY_DEV_MODE:
    control.set_develop_mode(True)
else:
    control.set_develop_mode(False)

# Check experiment conditions 
if IS_FMRI:
    print('\n \t            fMRI: enabled') 
else:
    print('\n \t            fMRI: disabled')
    
if IS_EYELINK:
    print('\n \t         EyeLink: enabled')
else:   
    print('\n \t         EyeLink: disabled')
    
if IS_TOBII:
    print('\n \t         TOBII: enabled')
else:   
    print('\n \t         TOBII: disabled')
    
    
if IS_TOBII:
    alltobii = tobii.find_all_eyetrackers()
    mytobii = alltobii[0]
    
    def what_tobii_records(flux_oculo,):
        global timeflow
        timeflow        = flux_oculo['device_time_stamp']
        coord_RE        = flux_oculo['right_gaze_point_on_display_area']
        coord_LE        = flux_oculo['left_gaze_point_on_display_area']
        diam_RE_pupil   = flux_oculo['right_pupil_diameter']
        diam_LE_pupil   = flux_oculo['left_pupil_diameter']    
        #print("t: {0} \t\t RE: {1} \t LE: {2} \t Diam (R,L) ({3},{4})".format(timeflow, coord_RE, coord_LE, diam_RE_pupil, diam_LE_pupil))
        eyetracking_outputfile.write(str(timeflow) +" \t "+ str(coord_RE) +" \t "+ str(coord_LE) +" \t "
                          + str(diam_RE_pupil) +" \t "+ str(diam_LE_pupil)+ "\t "+ "\n")
    
    mytobii.subscribe_to(tobii.EYETRACKER_GAZE_DATA, what_tobii_records, as_dictionary=True)


#########################dev mode and irm specifictiy###############""
if DEV_MODE: # ask for switch to windows mode
    control.defaults.window_mode = True  
else:
    control.defaults.window_mode = False

control.defaults.open_gl= False

control.initialize(exp)

if not IS_FMRI:
    exp.mouse.show_cursor()
###################################################################""












