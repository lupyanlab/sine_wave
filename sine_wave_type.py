from psychopy import core, visual, prefs, event
import random
import sys
import copy
import socket
import webbrowser as web
from useful_functions_python3 import getKeyboardResponse, showText, setAndPresentStimulus, createDirectories, openOutputFile, printHeader, importTrialsWithHeader, calculateRectangularCoordinates, loadFiles, popupError, getRunTimeVars, evaluateLists, writeToFile
from generateTrials import *


from psychopy import logging
logging.console.setLevel(logging.CRITICAL)

expName='SNR'

class Exp:

	def __init__(self):

		while True:
			runTimeVarOrder = ['subjCode','seed','gender']
			runTimeVars = getRunTimeVars({'subjCode':'SNR_',  'seed':10, 'gender':['Choose', 'male','female','other']},runTimeVarOrder,expName)
			if runTimeVars['subjCode']=='':
				popupError('Subject code is blank')
			else:
				try:
					createDirectories(['data','trials'])
					self.outputFile = openOutputFile('data/'+runTimeVars['subjCode'],expName+'_test')
					if self.outputFile: #files were opened for writing
						break
				except:
					popupError('Output file(s) could not be opened for writing')

		generateTrials(runTimeVars, runTimeVarOrder)
		(self.header,self.trialInfo) = importTrialsWithHeader('trials/'+runTimeVars['subjCode']+'_trials.csv', separator=',')

		#self.win = visual.Window(fullscr=True,allowGUI=False, color="gray", units='pix')
		self.win = visual.Window([800,600],allowGUI=True, color="gray", units='pix')
		#visual.TextStim(win=self.win,text="Loading stimuli...").draw()
		self.win.flip()
		self.pics =  loadFiles('stimuli/visual','.png','image', win=self.win)
		self.sounds =  loadFiles('stimuli/sounds','.wav','sound', win=self.win)
		self.waitForTarget = visual.TextStim(win=self.win,text="",color="black",height=40)
		self.fixationCross = visual.TextStim(win=self.win,text="+",color="black",height=40)

		# self.takeBreakEveryXTrials = 3
		self.pre_sine_delay = .3
		self.pre_mooney_delay = .5
		self.press_when_ready = "Please press spacebar when you're ready to hear the next sound"
		self.sine_typing_prompt = "What was the word you heard? "
		self.mooney_typing_prompt = "What object do you see in this image?"
		self.confidence_rating_sine = visual.TextStim(win=self.win,text="How sure are you that you heard the word...",height=20,pos=(0,210))
		self.confidence_rating_mooney = visual.TextStim(win=self.win,text="How sure are you that you see a...",height=20,pos=(0,210))

		self.position = {'response_box_sine': (0,0), 'response_box_mooney': (0,-180), 'response_prompt_mooney': (0,180), 'response_prompt_sine':(0,80)}

		runTimeVars['room'] = socket.gethostname().upper()
		self.surveyURL = 'QUALTRICS_URL'
		self.surveyURL += '?subjCode='+runTimeVars['subjCode']+'&room='+runTimeVars['room']

		self.inputDevice = "keyboard"
		
		self.sine_instructions_text = """
			Please put on the headphones and keep them on throughout the duration of this task.\n
			On each trial, you will hear ... .\n 
			Finish instructions here...
			"""

		self.mooney_instructions_text = """
			For this part you won't need the headphones.\n
			Mooney image instructions
			"""

		self.break_text = "Please take a short break.  Press one of the response keys to continue"


	def collectWordResponse(self,stimsToDraw,startString='→ ',pos=(200,-80)):
		responded=False
		response=startString
		if type(stimsToDraw)==list:
			for curStimToDraw in stimsToDraw:
				curStimToDraw.draw()
		else:
			stimsToDraw.draw()
		visual.TextStim(self.win,text=response,pos=pos, height = 30,color="white").draw()
		self.win.flip()
		typingTimer = core.Clock()
		firstKeypress=True
		while not responded: #collect one response
			for key in event.getKeys():
				changed=False
				key = key.lower()
				if key in ['enter','return'] and response != startString:
					responded = True
					self.win.flip()
				if key in ['backspace']:
					if len(response) > 0:
						response = response[0:-1]
						changed=True
				elif key in 'abcdefghijklmnopqrstuvwxyz' or key in ['space','quote','quotedbl']:
					if firstKeypress:
						startedTypingRT = typingTimer.getTime()
						firstKeypress=False
					responded = False
					if key=='space':
						key=' '
					elif key=='quote':
						key='\''
					response += key
					changed=True
				if changed:
					if type(stimsToDraw)==list:
						for curStimToDraw in stimsToDraw:
							curStimToDraw.draw()
					else:
						stimsToDraw.draw()
					visual.TextStim(self.win,font="Courier", text=response,pos=pos, height = 30,color="white").draw()
					self.win.flip()
		response = response.replace(startString,'') #remove the start string from the final response
		finishedTypingRT = typingTimer.getTime()
		return (response,startedTypingRT,finishedTypingRT)





	def takeBreak(self):
		visual.TextStim(win=self.win,text=self.break_text,color="white",height=40).draw()
		self.win.flip()
		event.waitKeys()

	def create_placeholder(self,lineColor="black", fillColor="white",size=(507,507),pos=(0,0)):
	 	return visual.Rect(win=self.win,size=size, pos=pos, lineColor=lineColor, fillColor=fillColor, lineWidth=3)

	def show_instructions(self,text):
		visual.TextStim(win=self.win,text=text,color="white",height=20).draw()
		self.win.flip()
		event.waitKeys(keyList=['q'])

	def thanks(self):
		visual.TextStim(win=self.win,text="Thank you! A short questionnaire will now pop up and then we'll be all done.\nPress a button/key to continue.",color="white",height=40).draw()
		self.win.flip()
		event.waitKeys()

	def show_trial(self,curTrial):

		rating_scale = visual.RatingScale(win=self.win,tickMarks=[1,2,3,4,5],marker='triangle', tickHeight=0.5,
			textColor='white', size=1.2, pos=[0.0, -340.0], low=1, high=5,markerColor="black",
			mouseOnly=False,labels = ['Just guessing', 'Completely Sure'], scale='1=Just guessing; 5=Completely sure', markerStart=None, showValue = True, 
			disappear=True, showAccept=False, acceptPreText="pretext", acceptText="",
			lineColor='white')


		core.wait(self.pre_sine_delay) 

		if curTrial['trial_type']=='sine_wave':
			prompt_pos = self.position['response_box_sine']
			response_pos = self.position['response_prompt_sine']
			visual.TextStim(self.win,self.press_when_ready,height=30).draw()
			self.win.flip()
			event.waitKeys(keyList=['space'])
			self.sounds[curTrial['file_name']]['stim'].play()
			self.win.flip()
			core.wait(self.sounds[curTrial['file_name']]['duration'])
			stims_to_draw = visual.TextStim(self.win,self.sine_typing_prompt,height=30,pos=response_pos)

		elif curTrial['trial_type']=='mooney':
			prompt_pos = self.position['response_box_mooney']
			response_pos = self.position['response_prompt_mooney']
			setAndPresentStimulus(self.win,[self.create_placeholder()])
			core.wait(self.pre_mooney_delay)
			mooney_prompt = visual.TextStim(self.win,self.mooney_typing_prompt,height=30,pos=response_pos)
			stims_to_draw = [self.pics[curTrial['file_name']]['stim'], mooney_prompt]
			prompt_pos = self.position['response_box_mooney']

		(response,startedTypingRT,finishedTypingRT) = self.collectWordResponse(stims_to_draw,pos=prompt_pos)
		responseTimer = core.Clock()


		response_string = visual.TextStim(self.win,height=30, pos=response_pos, text=response)
		while rating_scale.noResponse:
			if curTrial['trial_type']=='sine_wave':
				setAndPresentStimulus(self.win,[response_string, self.confidence_rating_sine, rating_scale])
			elif curTrial['trial_type']=='mooney':
				setAndPresentStimulus(self.win,[self.create_placeholder(), self.pics[curTrial['file_name']]['stim'], response_string, self.confidence_rating_mooney, rating_scale])
		rating = rating_scale.getRating()
		ratingRT = rating_scale.getRT()

		print(rating,ratingRT)

		#write test data to output file
		curTrial['header']=self.header
		trial_data=[curTrial[_] for _ in curTrial['header']] # add independent and runtime variables to what's written to the output file
		#write dependent variables
		trial_data.extend((response,
							startedTypingRT*1000,
							finishedTypingRT*1000,
							rating,
							ratingRT*1000))
		writeToFile(self.outputFile,trial_data,writeNewLine=True)



if __name__ == '__main__':
	exp = Exp()

	train_header = exp.header[:] #assign list by value since we're extending it below and don't want to change the orig header list
	train_header.extend(('response','startedTypingRT','finishedTypingRT','confidence_rating','confidence_rating_RT'))
	printHeader(train_header,headerFile="train_header.txt",separator=",")


	for i,curTrial in enumerate(exp.trialInfo):
		
		if i==0 and curTrial['trial_type']=='sine_wave':
			exp.show_instructions(exp.sine_instructions_text)
		elif i==0 and curTrial['trial_type']=='mooney':
			exp.show_instructions(exp.mooney_instructions_text)

		# #show break screen
		# if i>0 and i % exp.takeBreakEveryXTrials == 0:
		# 	exp.takeBreak()
	
		exp.show_trial(curTrial)
	

	web.open(exp.surveyURL, autoraise=True)

