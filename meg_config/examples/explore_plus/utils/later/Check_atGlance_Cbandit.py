#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 17:39:40 2021

@author: maeva
"""

import os
import csv
import ast
import glob
import random
import numpy as np
import pandas as pd
from statistics import stdev
import matplotlib.pyplot as plt

N_PARTICIPANTS = 38
EXCLUDED = []
N_SESSIONS = 8

SEQUENCES_PATH = '/Users/maeva/Documents/Neurospin/EXPLORE/' +\
    'CBandit_Behavioral_Task/CBanditTask_tobii/sequences/'


def compute_chance_level():

    # Pick the files
    sequences_files = glob.glob(SEQUENCES_PATH + 'sequence*.csv')
    armA_reward = []
    armB_reward = []
    choice = []

    for file in sequences_files:
        with open(file,  "r") as thisfile:
            # extract values from the file.
            reader = csv.reader(thisfile)
            for line in reader:
                if line[4] == '':  # if trial is not forced
                    armA_reward.append(float(line[1]))
                    armB_reward.append(float(line[2]))
            for sim in range(100000):
                for i in range(len(armA_reward)):
                    choice.append(random.choice(
                        [armA_reward[i], armB_reward[i]]))

            mean_reward = sum(choice) / len(choice)
            print(file, round(mean_reward, 2))


summary_vals = np.zeros((N_PARTICIPANTS, N_SESSIONS))
summary_estims = np.zeros((N_PARTICIPANTS, N_SESSIONS))


def get_obtained_reward(participant, session):
    '''Computes the obtained reward value for only free choices in the session 
    of interest for the participant.'''

    if participant < 10:
        num_participant = '0' + str(participant)
    else:
        num_participant = participant

    csv_file = '/data_csv/data_subject_{}_session_{}.csv'.format(
        num_participant, session)

    sum_rewards = []

    with open(os.getcwd() + csv_file,  "r") as thisfile:
        reader = csv.reader(thisfile)
        armA_reward = []
        armB_reward = []

        for line in reader:
            if participant < 3:
                if line[-5] == '':
                    if line[15] != 'reward':  # ignoring the headers line
                        sum_rewards.append(int(line[15]))
                        armA_reward.append(int(line[-7]))
                        armB_reward.append(int(line[-6]))
            else:
                if line[-6] == '':
                    if line[7] != 'reward':
                        sum_rewards.append(int(line[7]))
                        armA_reward.append(int(line[-9]))
                        armB_reward.append(int(line[-8]))

        mean_reward = sum(sum_rewards)/len(sum_rewards)

    print('Vous avez gagné un total de {} points'.format(sum(sum_rewards)))

    if participant < 10:
        num_participant = '0' + str(participant)

    else:
        num_participant = participant

    infos_file = '/data_csv/data_subject_{}_info.txt'.format(num_participant)

    with open(os.getcwd() + infos_file) as f:
        infos_seq = f.readlines()
        infos_seq = str(infos_seq[0])
        infos_seq = ast.literal_eval(infos_seq)
        sequence_set = infos_seq['sequence_set_order'][session - 1]
        block = infos_seq['block_order'][session-1] + 1

    sequence_file = '/sequences/sequence_{}_{}.csv'.format(sequence_set, block)

    return mean_reward, sequence_file


def get_recap_table(participant, session):
    '''Computes the number of matches between the estimated and true reward
    value of each arm, as well as a detailed table with question-wise matches
    and confidence reports associated to the estimations'''

    if participant < 10:
        num_participant = '0' + str(participant)

    else:
        num_participant = participant

    infos_file = '/data_csv/data_subject_{}_info.txt'.format(num_participant)

    with open(os.getcwd() + infos_file) as f:
        infos_seq = f.readlines()
        infos_seq = str(infos_seq[0])
        infos_seq = ast.literal_eval(infos_seq)
        sequence_set = infos_seq['sequence_set_order'][session - 1]
        block = infos_seq['block_order'][session-1] + 1
        questions = infos_seq['questions'][session - 1]

    sequence_file = '/sequences/sequence_{}_{}.csv'.format(sequence_set, block)
    print(sequence_file)

    with open(os.getcwd() + sequence_file) as file:
        reader = csv.reader(file)
        A_mean = []
        B_mean = []
        for line in reader:
            if line[-1] == '1':
                A_mean.append(float(line[-5]))
                B_mean.append(float(line[-4]))

    csv_file = '/data_csv/data_subject_{}_session_{}.csv'.format(
        num_participant, session)

    with open(os.getcwd() + csv_file) as file:
        estimationsA = []
        confidenceA = []
        estimationsB = []
        confidenceB = []
        reader = csv.reader(file)

        for line in reader:

            if participant < 3:
                if line[36] != '':
                    if line[36] != 'optLeft_val':
                        estimationsA.append(float(line[36]))
                        confidenceA.append(line[37])
                        estimationsB.append(float(line[38]))
                        confidenceB.append(line[39])

            else:
                if line[-1] == '1':
                    estimationsA.append(line[9])
                    confidenceA.append(line[11])
                    estimationsB.append(line[13])
                    confidenceB.append(line[15])

                interpret_estimationA = []
                for estim in estimationsA:
                    if estim == 's':
                        interpret_estimationA.append(30)
                    if estim == 'd':
                        interpret_estimationA.append(50)
                    if estim == 'f':
                        interpret_estimationA.append(70)

                interpret_estimationB = []
                for estim in estimationsB:
                    if estim == 's':
                        interpret_estimationB.append(30)
                    if estim == 'd':
                        interpret_estimationB.append(50)
                    if estim == 'f':
                        interpret_estimationB.append(70)

                interpret_confA = []
                for conf in confidenceA:
                    if conf == 'j':
                        interpret_confA.append(0)
                    if conf == 'k':
                        interpret_confA.append(1)
                    if conf == 'l':
                        interpret_confA.append(2)
                    if conf == ';':
                        interpret_confA.append(3)
                    if conf == 'm':
                        interpret_confA.append(3)

                interpret_confB = []
                for conf in confidenceB:
                    if conf == 'j':
                        interpret_confB.append(0)
                    if conf == 'k':
                        interpret_confB.append(1)
                    if conf == 'l':
                        interpret_confB.append(2)
                    if conf == ';':
                        interpret_confB.append(3)
                    if conf == 'm':
                        interpret_confB.append(3)

    score_estim = 0

    if participant < 3:
        df = pd.DataFrame(list(zip(A_mean, estimationsA, confidenceA,
                               B_mean, estimationsB, confidenceB)),
                          columns=['A_mean', 'A_estim', 'A_conf',
                                   'B_mean', 'B_estim', 'B_conf'])
        for i in range(len(A_mean)):
            if A_mean[i] == estimationsA[i]:
                score_estim += 1
            if B_mean[i] == estimationsB[i]:
                score_estim += 1
    else:
        df = pd.DataFrame(list(zip(A_mean, interpret_estimationA,
                                   interpret_confA,
                                   B_mean, interpret_estimationB,
                                   interpret_confB)),
                          columns=['A_mean', 'A_estim', 'A_conf',
                                   'B_mean', 'B_estim', 'B_conf'])

        for i in range(len(A_mean)):
            if A_mean[i] == int(float(interpret_estimationA[i])):
                score_estim += 1
            if B_mean[i] == int(float(interpret_estimationB[i])):
                score_estim += 1

    print(df)
    print('Nombre estimations correctes : ', score_estim, '/{}'.format(
        str(len(A_mean) + len((B_mean)))))

    return score_estim


def get_all_participants_performance():

    for i in range(1, N_PARTICIPANTS + 1):
        if i not in EXCLUDED:
            for j in range(1, N_SESSIONS + 1):
                print('participant ', i, 'session', j)

                val, seq = get_obtained_reward(i, j)
                val = round(val, 2)
                estim = get_recap_table(i, j)

                if seq == '/sequences/sequence_1_1.csv':
                    summary_vals[i-1, 0] = val
                    summary_estims[i-1, 0] = estim
                if seq == '/sequences/sequence_1_2.csv':
                    summary_vals[i-1, 1] = val
                    summary_estims[i-1, 1] = estim
                if seq == '/sequences/sequence_1_3.csv':
                    summary_vals[i-1, 2] = val
                    summary_estims[i-1, 2] = estim
                if seq == '/sequences/sequence_1_4.csv':
                    summary_vals[i-1, 3] = val
                    summary_estims[i-1, 3] = estim
                if seq == '/sequences/sequence_2_1.csv':
                    summary_vals[i-1, 4] = val
                    summary_estims[i-1, 4] = estim
                if seq == '/sequences/sequence_2_2.csv':
                    summary_vals[i-1, 5] = val
                    summary_estims[i-1, 5] = estim
                if seq == '/sequences/sequence_2_3.csv':
                    summary_vals[i-1, 6] = val
                    summary_estims[i-1, 6] = estim
                if seq == '/sequences/sequence_2_4.csv':
                    summary_vals[i-1, 7] = val
                    summary_estims[i-1, 7] = estim

    return summary_vals, summary_estims
