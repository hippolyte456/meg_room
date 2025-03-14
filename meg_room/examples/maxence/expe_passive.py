import expyriment
import numpy as np
import random
import os
import sys
from os import listdir
import csv
import glob

#path = '/Users/maxencepajot/Library/Mobile Documents/com~apple~CloudDocs/Neurospin/geometry_brain/python/meg_experiment/final_stimuli'
path = "./final_stimuli"
ns_meg = 1

#_______________________________________________
# Experiment parameters
#_______________________________________________

def main(block_number):
    if ns_meg == 1:

        port4send = expyriment.io.ParallelPort(address = "/dev/parport1")
        port4read = expyriment.io.ParallelPort(address = "/dev/parport0")
        durationTriggers = 10 # 300 ms

    number_images = 96
    number_rep = 2
    n_blocks = 8
    buttonChecked = 0
    size_photodiode=100
    origin_position=(-300,0) #Define center position for the figure


    #_______________________________________________
    # Temporal parameters
    #_______________________________________________

    fixationStart = 2000 # fixation at the start of the run. Set to 0 when debugging.
    fixationEnd = 6000 # fixation after the last ITI.
    instruction_time = 1000 # 1000
    duration_stimuli = 200 # Stimulus duration in milliseconds.
    duration_inter_stimuli = 200 # Inter-stimulus duration in milliseconds.  
    duration_pause_max = 5000
    #_______________________________________________
    # Expyriment parameters
    #_______________________________________________

    # Window parameters
    width = 800
    height = 600
    window_fs = True

    exp = expyriment.design.Experiment(name="Attention MEG")
    if window_fs == True:
        expyriment.control.defaults.window_mode = False
    else:
        expyriment.control.defaults.window_mode = True
        expyriment.control.defaults.window_size = (width,width)
    expyriment.control.initialize(exp)

    fix_cross = expyriment.stimuli.FixCross(position=(0,0))
    fix_cross.preload()

    #_______________________________________________
    # Preparation of the experiment : visual stimuli
    #_______________________________________________

        
    # -- Photodiode item
    photodiode = expyriment.stimuli.Rectangle(size=(size_photodiode,size_photodiode), position=(700,-400), colour=(255,255,255))
    photodiode.preload()

    ### Different types of instructions

    instruction = expyriment.stimuli.TextScreen(
            heading = "", 
            text = f"""
            Tu dois appuyer sur le bouton lorsque tu vois une étoile.

            """,
            text_size = 80,
            )
    instruction_pause = expyriment.stimuli.TextScreen(
            heading = "", 
            text = f"""
            Tu as quelques secondes pour te reposer. 
            """,
            text_size = 80,
            )
    texte_fin = expyriment.stimuli.TextScreen(
            heading = "", 
            text = f"""
            Le block est terminé !

            """,
            text_size = 80,
            )
    ### Create the lists of stimuli for all blocks
    list_order_stimuli_star = []
    for i in range(n_blocks):
        block = expyriment.design.Block("First Run")

        ### Create the pseudo random list of stimuli
        block_stimuli = np.array([])
        for j in range(number_rep):
            a = np.random.permutation(number_images)+1
            block_stimuli = np.concatenate([block_stimuli,a])

        n_stars = 8
        star_intervals = np.array([random.randint(15, 25) for _ in range(n_stars)])
        star_positions = np.cumsum(star_intervals)
        block_stimuli_star = np.insert(block_stimuli, star_positions, 97)

        block_stimuli_star = list(block_stimuli_star)
        number_stimuli_star = len(block_stimuli_star)
        list_order_stimuli_star.append(block_stimuli_star)
        ### Definition of the block
        for trialId in range(0,number_stimuli_star):
        #for trialId in range(0,4):
            
            trial = expyriment.design.Trial()

            stimuli_trial = int(list_order_stimuli_star[i][trialId])
            stim = expyriment.stimuli.Picture(path + '/' + str(stimuli_trial) + ".png", position = origin_position)
            stim.preload()
            trial.add_stimulus(stim)
            greyStim = expyriment.stimuli.Picture(path + "/98_with_cross.png", position = origin_position)
            greyStim.preload()
            trial.add_stimulus(greyStim)
            block.add_trial(trial)
        exp.add_block(block)



    #_______________________________________________
    ###### RUN EXPERIMENT ########
    #_______________________________________________

    ### present instructinos
    expyriment.control.start(exp)
    instruction.present()
    exp.clock.wait(instruction_time)
    
    init_time_exp = exp.clock.time
    exp.screen.clear()
    exp.screen.update()
    ### present fixation cross after the instructions
    expyriment.stimuli.Picture(path + "/98_with_cross.png", position = origin_position).present()
    exp.clock.wait(fixationStart)
    count_blocks = 0
    for block in exp.blocks:
        for trial in block.trials:
            
            stimuli_index = list_order_stimuli_star[count_blocks][trial.id]
            # Send triggers
            if ns_meg == 1:
                port4send.send(data = int(stimuli_index)) 
                exp.clock.wait(durationTriggers)
                port4send.send(data = 0)
                
            
            allButtons = []
            allRespTime = []
            init_time = exp.clock.time - init_time_exp
            new_time = exp.clock.time - init_time_exp
            rt = None

            ### trick needed to get the right stim duration
            while (new_time - init_time) < duration_stimuli:
                new_time = exp.clock.time - init_time_exp
                # photodiode.present(clear=False,update=False)
                trial.stimuli[0].present()
                if ns_meg == 0:
                    resp, rt = exp.keyboard.wait_char(' ', duration=duration_inter_stimuli)
                else:
                    resp = port4read.read_status()
                if (resp != buttonChecked):
                    rt = new_time - init_time
                    allButtons.append(resp)
                    allRespTime.append(rt)



            
            trial.stimuli[1].present(clear=False)
            exp.clock.wait(duration_inter_stimuli)
            exp.data.add([trial.id, stimuli_index, allButtons, allRespTime, block_number])

        ### Give pause at the end of each block, and end text at the very end
        if count_blocks<n_blocks-1:  
            instruction_pause.present()
            exp.clock.wait(duration_pause_max)  
            expyriment.stimuli.Picture(path + "/98_with_cross.png", position = origin_position).present()
            exp.clock.wait(fixationStart)      
        else:
            texte_fin.present()
            exp.clock.wait(fixationEnd)  
        count_blocks += 1 
    expyriment.control.end(exp)

    #_______________________________________________
    # Save the data in the csv format
    #_______________________________________________


    files = sorted(glob.glob("data/expe_passive*"))
    files_last = files[-1]
    data_test = expyriment.misc.data_preprocessing.read_datafile(files_last)
    numRow = len(data_test[0])
    nameFiles = files_last.split("data/")[1]
    with open("Outputs/" + nameFiles + ".csv", mode='w') as outputFile:
        output_writer = csv.writer(outputFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in range(0,numRow):
            output_writer.writerow(data_test[0][row])


if __name__ == "__main__":
    
    block_number = int(sys.argv[1])

    main(block_number)


