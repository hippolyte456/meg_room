'''
This file implement a class to give feedback to the subject during the experiment.
'''
import pandas as pd
import matplotlib.pyplot as plt
from expyriment import stimuli
import expyriment as expy

#TODO make sure it generalizes to fmri code when there is no answer...
class Feedback:
    def __init__(self, exp, block_inputs, csv_dir):
        self.exp = exp
        self.inputs = block_inputs
        self.save_graph_dir = 'tmp/temp_plot.png'
        self.csv_dir = csv_dir
    

    def show(self,duration=2000, real_reward = True):
        self.save_graph(real_reward)
        self.load_graph()
        self.display_seqGen(duration)

    #TODO compare the choices and the total gain with the ideal observer
    def save_graph(self, real_reward = True):
        # in the tmp folder, save the graph of the sequence
        # recupération des valeurs de A et B
        A = self.inputs['A']
        B = self.inputs['B']
        trueA = self.inputs['A_mean']
        trueB = self.inputs['B_mean']
        self.get_choices()
        
        if real_reward:
            plt.plot(A, label='A', color = 'purple', linestyle='dotted',linewidth=0.5)
            plt.plot(B, label='B', color = 'red', linestyle='dotted',linewidth=0.5)
            
        plt.plot(trueA, label='A_mean', linewidth=2.5, color = 'purple') #linestyle='--'
        plt.plot(trueB, label='B_mean', linewidth=2.5, color = 'red')
        plt.ylim(0, 100) 

    
        plt.scatter(self.num_trial, self.reward,label='Points de choix', color='black', s=10)
        plt.savefig(self.save_graph_dir)  # Sauvegarde la figure en tant qu'image temporaire

    def get_choices(self):
        #on récupère dans le folder data les valeurs de A et B grâce au numero de sujet, session, block
        df = pd.read_csv(self.csv_dir)
        self.reward = df['reward']
        self.item_choice = df['arm_choice']
        self.num_trial = df['TrialID']
        self.num_trial = self.num_trial[self.item_choice.notna()]   #TODO check this line

    def load_graph(self):
        self.image = stimuli.Picture(self.save_graph_dir)
        self.image.preload()

    def display_seqGen(self, duration):
        '''Display the sequence of the trial'''
        self.image.present()
        self.exp.clock.wait(duration)

    def get_reward(self):
        '''Get the reward of the subject'''
        df = pd.read_csv(self.csv_dir)
        self.total_reward = sum(df['reward'])
    
    def display_total_gain(self):
        '''Display the total gain of the subject'''
        self.get_reward()
        text1 = 'Votre gain total pour la session est de ' + str(self.total_reward) + ' euros.'
        text2 = "Celui de l'observateur idéal est de " + str(self.total_reward) + ' euros'
        stim1 = expy.stimuli.TextLine(text1, position=(0,30), text_size=40)
        stim2 = expy.stimuli.TextLine(text2, position=(0,-30), text_size=40)
        
        expy.stimuli.BlankScreen().present()
        stim1.present(clear=False)
        stim2.present(clear=False)
        self.exp.clock.wait(5000)
        self.exp.screen.clear()
        

        