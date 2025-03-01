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
    n_blocks = 3
    number_stimuli = number_images * number_rep
    size_photodiode=100
    origin_position=(-300,0) #Define center position for the figure

    ### Create stimuli lists for all blocks
    list_order_stimuli = np.array([])
    for i in range(number_rep):
        a = np.random.permutation(number_images)+1
        list_order_stimuli = np.concatenate([list_order_stimuli,a])
    list_order_stimuli = list(list_order_stimuli)


    faces = [i for i in range (1,97) if i%24>=1 and i%24<=4]
    bodies = [i for i in range (1,97) if i%24>=5 and i%24<=8]
    animals = [i for i in range (1,97) if i%24>=9 and i%24<=12]
    plants = [i for i in range (1,97) if i%24>=13 and i%24<=16]
    objects = [i for i in range (1,97) if i%24>=17 and i%24<=20]
    landscapes = [i for i in range (1,97) if i%24>=21 or i%24==0]

    dico_instru = {
        0:'des visages ou des parties de visages',
        1:'des corps ou des parties du corps, sauf les visages',
        2:'des animaux ou insectes',
        3:'des plantes, fruits ou légumes',
        4:'des objets ou véhicules',
        5:'des lieux'
    }
    dico_results = {
        0:faces,
        1:bodies,
        2:animals,
        3:plants,
        4:objects,
        5:landscapes
    }
    #_______________________________________________
    # Temporal parameters
    #_______________________________________________

    fixationStart = 1000 # fixation at the start of the run. Set to 0 when debugging.
    fixationEnd = 6000 # fixation after the last ITI.
    instruction_time = 10000
    duration_stimuli = 200 # Stimulus duration in milliseconds.
    duration_inter_stimuli = 800 # Inter-stimulus duration in milliseconds.  
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

    buttonChecked = 0

    #_______________________________________________
    # Preparation of the experiment : visual stimuli
    #_______________________________________________

    # -- Photodiode item
    photodiode = expyriment.stimuli.Rectangle(size=(size_photodiode,size_photodiode), position=(700,-400), colour=(255,255,255))
    photodiode.preload()

    ### Different types of possible instructions
    instructions = []

    for i in range(6):

        instructions.append(expyriment.stimuli.TextScreen(
            heading = "", 
            text = f"""
            Tu dois maintenant appuyer sur le bouton dès que tu vois {dico_instru[i]}.

            """,
            text_size = 80,
            ))
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
    order_type_button = list(np.random.permutation(6))
    list_order_stimuli = []
    for i in range(n_blocks):
        block = expyriment.design.Block("First Run")
        block_stimuli = np.array([])
        for j in range(number_rep):
            a = np.random.permutation(number_images)+1
            block_stimuli = np.concatenate([block_stimuli,a])
        list_order_stimuli.append(block_stimuli)

        for trialId in range(0,number_stimuli):
        #for trialId in range(0,4):
    
            trial = expyriment.design.Trial()
            stimuli_trial = int(list_order_stimuli[i][trialId])
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

    expyriment.control.start(exp)


    init_time_exp = exp.clock.time

    for block in exp.blocks:

        for trial in block.trials:
            stimuli_index = list_order_stimuli[block.id][trial.id]
            allButtons = []
            allRespTime = []
            

            type_button = order_type_button[2*block.id + trial.id//96]
            ### Give new instructions at the beginning of each block
            if trial.id%96 ==0:
                instructions[type_button].present()
                exp.clock.wait(instruction_time)
                exp.screen.clear()
                exp.screen.update()
                trial.stimuli[1].present()
                exp.clock.wait(fixationStart)

            # Send triggers
            if ns_meg == 1:
                port4send.send(data = int(stimuli_index)) 
                exp.clock.wait(durationTriggers)
                port4send.send(data = 0)

            # Loop for the duration of the stimuli
            init_time = exp.clock.time - init_time_exp
            new_time = exp.clock.time - init_time_exp
            rt = None
            while (new_time - init_time) < duration_stimuli:
                new_time = exp.clock.time - init_time_exp
                # photodiode.present(clear=False,update=False)
                trial.stimuli[0].present(clear=False)
                if ns_meg == 0:
                    resp, rt = exp.keyboard.wait_char(' ', duration=duration_inter_stimuli)
                else:
                    resp = port4read.read_status()
                if (resp != buttonChecked):
                    rt = new_time - init_time
                    allButtons.append(resp)
                    allRespTime.append(rt)
            
            # Inter-stimuli duration
            trial.stimuli[1].present()
            exp.clock.wait(duration_inter_stimuli)
            exp.data.add([trial.id, stimuli_index, allButtons, allRespTime, block_number, type_button])

        ### Give pause at the end of each block, and end text at the very end
        if block.id<n_blocks-1:  
            instruction_pause.present()
            exp.clock.wait(duration_pause_max)

        else:
            texte_fin.present()
            exp.clock.wait(fixationEnd)  
    expyriment.control.end(exp)


    #_______________________________________________
    # Save the data in the csv format
    #_______________________________________________


    #files = sorted(listdir("data/expe_active*"))
    files = sorted(glob.glob("data/expe_active*"))
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



