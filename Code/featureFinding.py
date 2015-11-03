import collections
import numpy as np
from fileIO import *

def getClusters(data):
	# data: set of points to cluster
	# return: sizes of each cluster and its/a representative point
	return

def getOrd(num):
	if num == 0:
		return '0th'
	elif num == 1:
		return '1st'
	elif num == 2:
		return '2nd'
	elif num == 3:
		return '3rd'
	else:
		return '%sth'%num

def frequencies(data):
	counter=collections.Counter(data)
	freqs = counter.values()
	data = counter.keys()

	# sort list by frequency from highest to lowest
	combo=[(data[i], freqs[i]) for i in range(len(freqs))]
	combo.sort(key=lambda tup: tup[1])
	combo.reverse()

	totalData=sum(n for _, n in combo)
	combo=[(combo[i][0], combo[i][1]*1.0/totalData) for i in range(len(combo))]

	return combo

def freqFeatures(data, fDescr, IF=[]):


	Freqs = frequencies(data)

	# check if any of this is interesting
	expectedFreq = 1.0 / len(set(data))

	pos= 0
	minSalience = 1.25
	while 1.0*Freqs[pos][1]/expectedFreq >= 2.0 and pos < 3:
		salience = 1.0*Freqs[pos][1]/expectedFreq
		#IF.append([('%sth'%(pos+1))+" most frequent "+fDescr, Freqs[pos][0], round(salience,1)])
		IF.append([getOrd(pos+1)+" most frequent", fDescr, Freqs[pos][0], salience])

		pos += 1
		#break

	pos = 0
	#if Freqs[len(Freqs)-1][1] <= expectedFreq*0.75:
	'''
	while 1.0*expectedFreq / Freqs[len(Freqs)-1-pos][1] >= 2.0:
		salience = 1.0*expectedFreq / Freqs[len(Freqs)-1-pos][1]
		IF.append([('%sth'%(pos+1))+" least frequent "+fDescr, Freqs[len(Freqs)-1-pos][0], round(salience,1)])
	
		pos += 1
	'''
	
	return IF



def findFeatures(data, pairTests=[]):

	if len(data) <= 1:
		print "NO DATA"
		return ()

	# extract column names
	COL_NAMES = data[0]
	data = data[1:]

	# store interesting features of data
	IF = []
	# [ 1st most frequent, said, exit]# , salience] <- until return
	featureColNames = ["feature type", "feature description", "value"]#, "salience"]

	# get number of columns in data (properties)
	# assume homogeneous data set dimensions
	COL_NUM = len(data[0]) if isinstance(data[0], type((0,0))) else 0

	npData = np.array(data) # convert to numpy array for easier processing
	COLS = [npData[:,i] for i in range(COL_NUM)]



	for col in range(COL_NUM):
		# nth most/least frequent col_name is x
		IF = freqFeatures(COLS[col], IF=IF, fDescr=COL_NAMES[col])


	if pairTests == []:
		for col1 in range(COL_NUM):
			for col2 in range(col1+1, COL_NUM):
				C_COMBO = zip(COLS[col1], COLS[col2])
				C_COMBO = ['('+', '.join(item)+')' for item in C_COMBO]
				IF = freqFeatures(C_COMBO, IF=IF, fDescr=COL_NAMES[col1]+'-'+COL_NAMES[col2]+' element')
	else:
		for colPair in pairTests:
			col1 = colPair[0]
			col2 = colPair[1]

			C_COMBO = zip(COLS[col1], COLS[col2])
			C_COMBO = ['('+', '.join(item)+')' for item in C_COMBO]
			IF = freqFeatures(C_COMBO, IF=IF, fDescr=COL_NAMES[col1]+'-'+COL_NAMES[col2]+' element')		
	
	
	for col in range(COL_NUM):
		# nth most/least frequent col_name 2-sequence is x->y
		SEQ_2 = ['('+' and then '.join([COLS[col][i], COLS[col][i+1]])+')' for i in range(len(COLS[col])-1)]
		IF = freqFeatures(SEQ_2, IF=IF, fDescr=COL_NAMES[col]+' consecutive values')

	IF = [tuple(f) for f in IF]

	IF.sort(key=lambda tup: tup[3])
	IF.reverse()

	# get rid of salience column
	IF = [item[0:3] for item in IF]

	IF = [featureColNames]+IF

	return IF


def loadHist(HIST=[]):
	if HIST == []:
		HIST = yamlLoad('../Database/history.txt')#, 1)
		#HIST = [item[0] for item in HIST]

	#print HIST[0:5]

	for i in range(len(HIST)):
		mood = HIST[i][3]
		#print "MOOD:", mood
		mood = [round(val, 1) for val in mood] # round elems to 1 dcml place
		HIST[i] = list(HIST[i][1:3])
		HIST[i].extend(mood)
		HIST[i] = tuple(HIST[i])

	colNames = ["said",
				"cmd",
				"valence",
				"arousal",
				"dominance",
				"subsistence",
				"protection",
				"affection",
				"understanding", 
				"participation",
				"leisure",
				"creation",
				"identity",
				"freedom"]

	HIST = [colNames]+HIST
	return HIST

data = [1, 1, 1, 1, 2, 1, 2, 1]
data2 = [[0, 1], [1, 2], [0, 1], [1, 3], [1, 2], [0, 1]]
data3 = [(item[0], item[1]) for item in data2] 

H = loadHist()
FEATURES = findFeatures(H)