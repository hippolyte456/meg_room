
import os
import pandas as pd
from utils.CBandit_parameters import IS_MEG


'''
This class is used to save the behavioral data of the experiment.
Organization tree of the data:
- data
    - subj_01
        - sess_01
            - data_subject_01_session_01_block_01.csv
            - data_subject_01_session_01_block_02.csv
            - ...
        - sess_02
            - data_subject_01_session_02_block_01.csv
            - ...
    - subj_02
        - sess_01
            - data_subject_02_session_01_block_01.csv
            - ...
    - ...
with ~15 subjects, doing ~5sessions each, and ~8 blocks per session.
'''

#TODO test the class correctly
class Saver:
    
    #TODO make the .csv tidy ! (caution between the header and the savee because i remove some columns)
    def __init__(self, exp):
        self.exp = exp
        self.block_per_session = 4 #TODO change this to a parameter #9 (less 1)
        self.root_dir = 'data'
        self.subject_idx  = self.exp.subject
        self.subj_dir = os.path.join(self.root_dir, f'sub-{self.subject_idx}')
        self.make_new_dir(self.subj_dir)
        self.session_idx,self.block_idx = self.get_session_and_block()
        self.save_dir = os.path.join(self.subj_dir, f'sess_{self.session_idx}')
        self.make_new_dir(self.save_dir)
        
        self.fname = "data_subject_%02d_session_%d_block%f.csv" % (self.subject_idx,self.session_idx,self.block_idx)
        if IS_MEG:
            self.fname = "MEG_" + self.fname
        self.save_path = os.path.join(self.save_dir, self.fname)
        self.data_save = pd.DataFrame({ 'BlockID': [],'TrialID':[],
                            'arm_choice':[],'color_choice':[], 'Key': [], 'key_miss': [], 'reward': [],  
                            'keyQ1_val': [], 'keyQ1_conf': [], 'keyQ2_val': [], 'keyQ2_conf': [],
                            'startQuestion': [], 'stimVal1': [], 'stimConf1': [], 'stimVal2': [], 'stimConf2': [],
                            'rtQ1_val': [], 'rtQ1_conf': [], 'rtQ2_val': [], 'rtQ2_conf': [],
                            'trial_start': [],'RT': [], 'rt_miss': [],'frameOn_start': [],'outcome_start': [], 'trial_end': [], 'ITI_start': [],
                            'A': [],'B': [],
                            'outcome_SD': [],'forced': [],
                            'A_mean': [],'B_mean': [],
                            'isQ': [], 'ITI': [], 'rdSeed': [], })
        self.data_save.to_csv(self.save_path, header=True)
        self.block_name = 'block_' + str(self.session_idx) 

    def get_session_and_block(self):
        '''given the number of the subject, returns the id of session and block, the subject is about to do.'''
        
        #how many sessions folder already done for this subject
        folderlist = os.listdir(self.subj_dir) 
        session_idx = len(folderlist)

        #how many blocks for this session
        if session_idx == 0:
            block_idx = 1
            session_idx = 1
        
        else:
            fileslist = os.listdir(os.path.join(self.subj_dir, f'sess_{session_idx}') )
            #isxpd = ['.xpd' in f for f in fileslist]  # TODO change the file filter for more robust one ? or at least check it.
            block_idx = len(fileslist) +1 

            #if the session is already done, we start a new one
            if block_idx > self.block_per_session:
                session_idx += 1
                block_idx = 1
    
        print(f'New block: subject {self.subject_idx} session {session_idx}, block {block_idx}')
        return int(session_idx), int(block_idx)
    
    
    def make_new_dir(self,dir):
        '''creates a new directory to save the block data '''
        # si le dossier existe déjà, on ne fait rien
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except FileExistsError:
                pass

        
    def save(self, data): 
        data.to_csv(self.save_path, mode='a', header=False)
  
        
    def get_save_path(self):
        return self.save_path
