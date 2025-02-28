if IS_TOBII:
    eyetracking_outputfilename = os.path.join(TOBII_DIR, ("CBandit_TobiiData_subject_" + str(subject) + '_session_' + str(session) + ".txt"))
    
    eyetracking_outputfile=open(eyetracking_outputfilename, "w")
    
# Initilise eye-tracker______________
if IS_EYELINK:
    tracker, edfFileName = init_eyelink(exp)
    start_recording()
elif IS_TOBII:
    
    #header of the output file
    eyetracking_outputfile.write("time flow" + " \t " + "RE(x,y)" + " \t " + "LE(x,y)" + "\t diam (RE,LE)" 
                    +"\t " + "\n") 
    eyetracking_outputfile.write(str(timeflow)+" MSG: Displaying Introduction" + "\n")


#run expe______________
if IS_EYELINK:
    getEYELINK().sendMessage(" MSG: T0received")
    print("got thru T0 message\n")



#fixation______________
    if IS_EYELINK:
        getEYELINK().sendMessage(f" MSG: Trial {trial.id};")
        print("should be displaying trials\n")
    elif IS_TOBII:
        eyetracking_outputfile.write(str(timeflow)+f" MSG: Trial {trial.id}\n") #add here free / forced
        




# Stop the eye-tracker and save data_____________
if IS_EYELINK:
    end_recording()
    end_eyelink(exp, edfFileName)
elif IS_TOBII:
    eyetracking_outputfile.write(str(timeflow)+" MSG: End\n")
    time.sleep(2)
    mytobii.unsubscribe_from(tobii.EYETRACKER_GAZE_DATA, what_tobii_records)
    


#=========OUTCOME================
    # Display the reward for outcoome duration
    if IS_EYELINK:
        getEYELINK().sendMessage(" MSG: Outcome received")
    elif IS_TOBII: 
        eyetracking_outputfile.write(str(timeflow)+f" MSG: Outcome received: {reward}\n")



########CUE###########
# Questions
# # First cue
# if IS_EYELINK:
#     getEYELINK().sendMessage(" MSG: estim1\n")
# elif IS_TOBII:
#     eyetracking_outputfile.write(str(timeflow)+" MSG: estim1\n")

# Second cue
# if IS_EYELINK:
#     getEYELINK().sendMessage(" MSG: estim2;")
# elif IS_TOBII:
#     eyetracking_outputfile.write(str(timeflow)+" MSG: estim2\n")   