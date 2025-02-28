'''
To fusion with 'generate_sequence.py' file --> Discuss with Alex for the organization of function
'''
import os
import random as rd
import numpy as np
import pandas as pd
import utils.generate_sequence as gs
from utils.CBandit_parameters import *

#some constants for pregeration of sequences 

SUBS = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115,116,117,200] # add subjects after, not before !
SESSIONS = [1, 2, 3, 4, 5]
BLOCKS = [1, 2, 3, 4]
SEEDS = [i for i in range(len(SUBS)*len(SESSIONS)*len(BLOCKS))]
MEGsess = [[101,4],[101,5],[102,5],[102,5]] #add here the sessions in MEG

#TODO ATTENTION cette manière de faire oblige à ce que la generation soit indépendnate du type de session... mais quelle soit faites en une seule fois 
# donc s'assurer que les choses qui dépendent du type de session sont bien générées dans un second temps !! (par exemple le nombre de question IS_Q !)

#TODO faire les teeeeeeests unitaires !
#TODO la bonne manière de généré les sequences simplement ???......
#TODO no hardcoding
#TODO it would be better to code getter and setter function for the attribute... check the best way to do it
class SeqGen():
    """
    Class to generate all what is required for the experiment of one session.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the class. 
        """
        self.rdSeed = self.setRdmSeed()
        self.subID = kwargs['subID']
        self.sessionID = kwargs['sessionID']
        self.blockID = kwargs['blockID']
        self.nbQForced = NbQForced
        self.nbQFree = NbQFree
        self.min_Qspacing = Min_Qspacing
        self.sd_levels = SD_LEVELS
        self.sd = self.get_sd_level()


    def setRdmSeed(self, choose=None):
        '''
        Set the random seed for the generation of the sequences.
        '''
        if choose is None:
            s = rd.randint(0,100000)
        else:
            s = choose
        
        rd.seed(s)
        np.random.seed(s)
        self.rdSeed = s
        return s
    

    def update_session_param(self):
        '''
        to fill if some parameters has to change between sessions for one subject
        '''
        pass 
    
    #TODO testing the function, and generalize for more option ? 
    #TODO practice the decorator skill, to avoid conditional imbrication in the function
    def get_sd_level(self): 
        '''
        chose the sd level to apply for the seq generation, function of the sessionID and subID ?
        '''
        if self.subID % 2 == 0:
            if self.blockID % 2 == 0:
                return self.sd_levels[0]
            else:
                return self.sd_levels[1]
        else:
            if self.blockID % 2 == 0:
                return self.sd_levels[1]
            else:
                return self.sd_levels[0]
       
    #TODO do the unitary test for all these type of function ! 
    #TODO toutes les variables dans kwargs !!! pas déclarer directment dans la fonction !  
    def gen_isQ(self):
        '''
        define where the questio are asked to the subject. Constrains : 
        - 6 questions in the block
        - no question in the 10 first trials
        - 2 questions in the forced trials and 4 in the free trials
        - add one question at the beggining to help normalization between subjects ? nope...
        '''
        isQ = np.zeros(HORIZON)
        # isQ = np.ones(HORIZON)    #for quick test of questions rendering

        #get the index of forced and free trials 
        forced = gs.gen_forced_seq(NOPT, HORIZON, FORCED_LEN, FORCED_PERIOD, 
                                     n_from_start=None, max_same_choice=MAX_SAME_CHOICE, 
                                     output="info")["forced_seq"]
        forced_ind = np.where((forced == 1) | (forced == 0))[0]                     
        free_ind = np.setdiff1d(np.arange(HORIZON), forced_ind) #contrary of forced_ind
        
        #take two randow indexes in the forced trials and 4 in the free trials
        forced_ind = forced_ind[forced_ind > 10]
        free_ind = free_ind[free_ind > 10]
        forced_ind, free_ind = self.select_values_with_min_spacing(forced_ind, free_ind, 
                                                                   self.nbQForced, self.nbQFree,
                                                                   self.min_Qspacing)
        print('forced_ind : ', forced_ind)
        print('free_ind : ', free_ind)
        isQ[forced_ind] = 1
        isQ[free_ind] = 1

        return isQ

###### for the pregeneration of sequences ######
    def gen_all_sequences(self):
        '''
        Caution, This function is used in the contect of pregeneration of sequence
        '''
        i = 0
        for sub in SUBS:
            for sess in SESSIONS:
                for block in BLOCKS:
                    #global init when genration of all sequences
                    self.rdSeed = self.setRdmSeed(SEEDS[i]) 
                    self.subID = sub
                    self.sessionID = sess
                    self.blockID = block
                    self.sd = self.get_sd_level()
                    #session behavior
                    if sess == 1:  
                        self.nbQForced, self.nbQFree = 2, 4
                    else:
                        self.nbQForced, self.nbQFree = 2, 2
                    #generation of the sequence and save 
                    block_inputs = self.gen_block_input()
                    block_inputs.to_csv(SEQ_DIR + 'sub{}_sess{}_block{}.csv'.format(sub,sess,block), index=False)
                    i += 1


    def gen_one_sequence(self,sub,sess,block,new_rdseed):
        '''
        Caution, this function is used in the contect of pregeneration of sequence
        '''
        # self.rdSeed = new_rdseed
        # print('RDSEED', self.rdSeed)
        self.rdSeed = self.setRdmSeed(new_rdseed)
        block_inputs = self.gen_block_input()
        block_inputs.to_csv(SEQ_DIR + 'sub{}_sess{}_block{}.csv'.format(sub,sess,block), index=False)
################################################

    def gen_block_input(self):
        sds = gs.set_sd_sequence(self.sd, HORIZON, nopt=NOPT, ord_type="fixed", 
                         order=None, opts_match=True, out_type="sequence")
        
        forced_with_info = gs.gen_forced_seq(NOPT, HORIZON, FORCED_LEN, FORCED_PERIOD, 
                                     n_from_start=None, max_same_choice=MAX_SAME_CHOICE, 
                                     output="info")
        forced = forced_with_info["forced_seq"]
        seq_with_info = gs.gen_outcome_sequence(NOPT, HORIZON, LATENT_LEVELS, self.sd, VOL, 
                                        ideal_vol=IDEAL_VOL, ncp_range=NCP_RANGE, 
                                        cp_min_from_start=CP_MIN_FROM_START, cp_min_to_end=CP_MIN_TO_END, 
                                        cp_min_dist=CP_MIN_DIST, cp_min_opt_dist=CP_MIN_OPT_DIST, 
                                        cp_max_iter=10000, ll_current=None, 
                                        ll_startwith=None, ll_opt_diff_tol = LL_OPT_DIFF_TOL,
                                        sd_ord_type="fixed", sd_order=None, 
                                        sd_opts_match=True, out_bounds=OUT_BOUNDS,
                                        out_bound_method="regen",ll_mean_tol=LL_MEAN_TOL,
                                        out_mean_tol=OUT_MEAN_TOL, norm_noise=NORM_NOISE, 
                                        reg_max_iter=10000,output="info")
        out = seq_with_info["out_seq"]
        seq = gs.get_obs_seq(out, forced)
        isQ = self.gen_isQ()
        # print(seq_with_info)
        # print(seq_with_info['ll_seq'])

        # if MINI_MODE:
        #     return pd.DataFrame({'A': seq[0][:n_mini],'B': seq[1][:n_mini],'SD': sds[0][:n_mini], 'forced': forced[:n_mini],
        #                       'A_mean':seq_with_info['ll_seq'][0][:n_mini], 'B_mean':seq_with_info['ll_seq'][1][:n_mini],'isQ': isQ[:n_mini]})
        
        return pd.DataFrame({'rdSeed': self.rdSeed ,'A': seq[0],'B': seq[1],'SD': sds[0], 'forced': forced,
                              'A_mean':seq_with_info['ll_seq'][0], 'B_mean':seq_with_info['ll_seq'][1],'isQ': isQ})


    def select_values_with_min_spacing(self,index1,index2, nQ_Fo, nQ_Fr, min_spacing):
        '''
        Select values in a list with a minimum spacing between them.
        '''
        selected_forced,selected_free = [],[]
        while len(selected_forced) < nQ_Fo:
            value = rd.choice(index1) 
            if all(abs(value - v) >= min_spacing for v in selected_forced):
                selected_forced.append(value)
            #on enleve la valeur de l'index pour ne pas la rechoisir
            index1 = np.setdiff1d(index1, value)    
        while len(selected_free) < nQ_Fr:
            value = rd.choice(index2) 
            if all(abs(value - v) >= min_spacing for v in selected_free) and all(abs(value - v) >= min_spacing for v in selected_forced):
                selected_free.append(value)
            index2 = np.setdiff1d(index2, value)
        return selected_forced,selected_free

    
    def get_block_input(self):
        file = pd.read_csv(SEQ_DIR +'sub{}_sess{}_block{}.csv'.format(self.subID,self.sessionID,self.blockID))
        self.rdSeed = file['rdSeed'][0]
        return file

    def check_sequence(self,block_input):
        '''
        Check if the sequence is well generated (type of session, number of questions in isQ etc...)
        '''
        print('number of questions : ', np.sum(block_input['isQ']))
        print('sd_level: ', block_input['SD'][0])
        print('rdSeed: ', block_input['rdSeed'][0])

    def MEG_transform(self):
        '''
        Transform the csv in TaskSequences for MEG (isQ = 6, etc...)
        '''
        for sub_sess in MEGsess:
            for block in BLOCKS:
                self.nbQForced, self.nbQFree = 2, 4
                file = pd.read_csv(SEQ_DIR + 'sub{}_sess{}_block{}.csv'.format(sub_sess[0],sub_sess[1], block))
                isQ = self.gen_isQ()
                #on remplace la colonne isQ
                file['isQ'] = isQ
                file.to_csv(SEQ_DIR + 'sub{}_sess{}_block{}.csv'.format(sub_sess[0],sub_sess[1], block))
            
























# =============================================================================
# INITIALIZE SEQ with COUNTERBALANCING
# ============================================================================

#TODO remove ans replace by generation of sequences
'''
cb = generate_sequences()
# Get counterblancing for this subject (across sessions) and save
cb_sub = {'sequence_set_order': cb['sequence_sets'][subject_idx].tolist(),
          'block_order': cb['blocks'][subject_idx,:].tolist(), 
          'arm_ids': cb['arm_ids'][subject_idx,:].tolist(),
          'colors': cb['colors'][subject_idx,:].tolist(),
          'questions': cb['question_orders'][subject_idx].tolist()}


#TODO in an outside function
# Which arm (left/right) is "PURPLE"  
if cb_sub['colors'][session_idx] == 0:
    left_color = CUE_PURPLE
    right_color = CUE_ORANGE
    color_order_this_sess = 'PO'
else:
    left_color = CUE_ORANGE
    right_color = CUE_PURPLE
    color_order_this_sess = 'OP'
# Question order
q_order = cb_sub['questions'][session_idx]
# Save the sequence for this block in experiment info
#exp.add_experiment_info(which_sequence)
'''