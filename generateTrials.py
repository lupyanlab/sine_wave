import glob, os, random, sys
from itertools import product, chain
from math import ceil

import pandas as pd
import random
import numpy as np


def generateTrials(runTimeVars,runTimeVarsOrder):
	if not runTimeVars['subjCode']:
		sys.exit('Please provide subject code as subjCode')
	try:
		random.seed(int(runTimeVars['seed']))
		np.random.seed(int(runTimeVars['seed'])+1)
	except:
		print("Seed not set")

	
	trials = pd.read_csv('trial_info.csv')
	trials_sine = trials.loc[trials.trial_type=="sine_wave"]
	trials_mooney = trials.loc[trials.trial_type=="mooney"]
	separator = ','
	num_blocks_sine_wave = 3
	num_blocks_mooney = 1
	
	trials_sine = trials_sine.sample(frac=1, random_state=runTimeVars['seed']).reset_index(drop=True)
	orig_order = trials.copy()

	trial_file = open('trials/'+runTimeVars['subjCode']+'_trials.csv','w')
	header = separator.join(runTimeVarsOrder+['trial_type','block', 'stim_num','first_seen', 'word', 'file_name'])
	trial_file.write(header+'\n')

	for cur_block in range(num_blocks_sine_wave):
		if cur_block>0:
			trials_sine = trials_sine.sample(frac=1, random_state=runTimeVars['seed']+cur_block+1).reset_index(drop=True)
		for cur_stim_num, row in trials_sine.iterrows():
			trial_info = [runTimeVars[_] for _ in runTimeVarsOrder]
			cur_first_seen = orig_order.index[orig_order.file_name == row['file_name']].tolist()[0]
			trial_info.extend([row['trial_type'],cur_block+1, cur_stim_num, cur_first_seen, row['word'], row['file_name']]) 
			trial_file.write(separator.join(map(str,trial_info))+'\n')

	for cur_block in range(num_blocks_mooney):
		trials_mooney = trials_mooney.sample(frac=1, random_state=runTimeVars['seed']+cur_block+1).reset_index(drop=True)
		for cur_stim_num, row in trials_mooney.iterrows():
			trial_info = [runTimeVars[_] for _ in runTimeVarsOrder]
			cur_first_seen = cur_stim_num
			trial_info.extend([row['trial_type'], cur_block+1, cur_stim_num, cur_first_seen, row['word'], row['file_name']]) 
			trial_file.write(separator.join(map(str,trial_info))+'\n')



	trial_file.close()
	return True


if __name__ == '__main__':
	generateTrials({'subjCode':'testSubj_1', 'seed':8,'gender':'M'}, ['subjCode','seed', 'gender'])	
	generateTrials({'subjCode':'testSubj_2', 'seed':9,'gender':'M'}, ['subjCode','seed', 'gender'])	

	