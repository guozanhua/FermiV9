from header import *
from common import setting
from memory import *
from graphics import *

def getMoodIndex(facet):
	tmpMood=[0]*GLOB['MOODDIM']
	tmpMood = fullMoodVec(tmpMood)

	for i in range(GLOB['MOODDIM']):
		if facet == tmpMood[i][0]:
			return i
	return -1

def fullMoodVec(moodVec, colloquial=False, pronoun=False):
	# https://en.wikipedia.org/wiki/Fundamental_human_needs
	# -> + (VAD) vector at beginning
	fMV = []

	if pronoun:
		for i in range(GLOB['MOODDIM']):
			fMV.append((getStatePronoun(i, positive=moodVec[i]>0), moodVec[i]))

		return fMV

	if not colloquial:
		fMV.append(('valence', moodVec[0]))
		fMV.append(('arousal', moodVec[1]))
		fMV.append(('dominance', moodVec[2]))

		fMV.append(('subsistence', moodVec[3]))
		fMV.append(('protection', moodVec[4]))
		fMV.append(('affection', moodVec[5]))
		fMV.append(('understanding', moodVec[6]))
		fMV.append(('participation', moodVec[7]))
		fMV.append(('leisure', moodVec[8]))
		fMV.append(('creation', moodVec[9]))
		fMV.append(('identity', moodVec[10]))
		fMV.append(('freedom', moodVec[11]))
	else:

		fMV.append(('happiness', moodVec[0]))
		fMV.append(('excitement', moodVec[1]))
		fMV.append(('control', moodVec[2]))

		fMV.append(('health', moodVec[3]))
		fMV.append(('safety', moodVec[4]))
		fMV.append(('affection', moodVec[5]))
		fMV.append(('education', moodVec[6]))
		fMV.append(('responsibilities', moodVec[7]))
		fMV.append(('fun', moodVec[8]))
		fMV.append(('expression', moodVec[9]))
		fMV.append(('self-esteem', moodVec[10]))
		fMV.append(('freedom', moodVec[11]))
	return fMV

def partMoodVec(moodFull):
	# return only the real value number list (no labels)
	return [facet[1] for facet in moodFull]

def getFace(mood):
	# NOTE: only used VAD part of mood vector

	# calculate face best expressive of provided mood/emotion
	# euclidean distance of closest match
	minDist=10 #max possible is 2*sqrt(3) or something
	topFace=GLOB['EMOTIONS'][0]
	for face in GLOB['EMOTIONS']:
		#fMood = [('valence',face[1][0]), ('arousal',face[1][1]), ('dominance',face[1][1])]

		dist = getMoodDiff(mood, face[1])
		if dist < minDist:
			minDist, topFace=dist, face
	return topFace

def ingestionMood(moodType="SUBSTANCE"):
	''' SUBSTANCE INGESTION CALCULATIONS '''

	INGESTED=[]
	for item in GLOB['INGESTED']:
		if item[2] == moodType:
			INGESTED.append(item)


	Inum=len(INGESTED)

	# calculate time weight of all ingestions
	STweights=[]
	for ingestion in INGESTED:
		iTime, iProf = ingestion[1], ingestion[0][3]
		#print "iTime, iProf: ", iTime, iProf
		T = time.time() - iTime # needed to eval iProf
		iTWeight = eval(iProf)
		#print "iTWeight = ", iTWeight
		STweights.append(iTWeight)

	# get values of moods for substances
	#sNEEDv = [[] for i in range(GLOB['MOODDIM'])]
	sNEEDv = [[] for i in range(GLOB['MOODDIM'])] #[[]]*GLOB['MOODDIM']

	# get values of weights for substances
	# note: do not initialize with [[]]*12, because Python is borked
	sNEEDw = [[] for i in range(GLOB['MOODDIM'])]

	for ingestion in INGESTED:
		for i in range(GLOB['MOODDIM']):
			sNEEDv[i].append(ingestion[0][1][i])
			sNEEDw[i].append(ingestion[0][2][i])


	#print "sNEEDv: ", sNEEDv
	#print "sNEEDw: ", sNEEDw

	# multiply time weights and raw weights
	sNEEDcw = [[]]*GLOB['MOODDIM']
	for j in range(GLOB['MOODDIM']):
		sNEEDcw[j]=[STweights[i]*sNEEDw[j][i] for i in range(Inum)]
		#print "sNEEDcw",j," = ", sNEEDcw[j]
		#print "\tsNEEDw",j, " = ", sNEEDw[j] 


	NEEDS = [0]*GLOB['MOODDIM']
	for j in range(GLOB['MOODDIM']):
		if sum(sNEEDcw[j]) != 0:
			NEEDS[j] = sum([sNEEDv[j][i]*sNEEDcw[j][i] for i in range(Inum)])/sum(sNEEDcw[j])

	S = NEEDS

	NEEDsw = [0]*GLOB['MOODDIM']
	for i in range(GLOB['MOODDIM']):
		if sNEEDcw[i] == []:
			NEEDsw[i] = 0
		else:
			#print "HERE:", max(sNEEDcw[i])
			#print "sNEEDcw[i] = ", sNEEDcw[i]
			#NEEDsw[i] = max(sNEEDcw[i])
			NEEDsw[i] = sum(sNEEDcw[i])

	#print "RETURNING", S, NEEDsw

	return S, NEEDsw

# IN CMDS
def ingest(inCmd, inStr, mood=[], weight=[], isCmd=False, isMem=False, matches=[[],[]]):
	from common import wordSim, processResponse, getResponse, say
	#from loadFile import load
	from determineFunction import findCMD, refineMatches
	from Fermi import substituteBiographicMemory

	if not (isCmd or isMem):
		matches = refineMatches(inCmd, inStr)
		matches = substituteBiographicMemory(matches, queryType='what is')

	if len(matches[0]) ==0 and not (isCmd or isMem):
		say(getResponse(findCMD("rephrase")), more=False, speak=setting("SPEAK"), moodUpdate=True)
		return False

	'''
	Algorithm:
		- load substance from list
		- record ingestion time
		- append to INGESTED list

	'''

	if isCmd:
		ingestionTime = time.time()
		
		taskProfile="pow(2.0, -1.0*T*T/(900.0*900.0))" # ~15 minute half life
		
		taskDetails = [[inCmd[0]], mood, weight, taskProfile]
		#print "appending: ", taskDetails

		GLOB['INGESTED'].append([taskDetails, ingestionTime, "COMMAND"])
		GLOB['MOOD']=updateMood(GLOB['MOOD'], weight=[0]*GLOB['MOODDIM'])
		
		#print "AFTER CMD ADD"
		#print GLOB['MOOD']

		return # no return value if adding a cmd mood modifier

	if isMem:
		#print "ADDING MEMORY MOOD"

		ingestionTime = time.time()
		
		memProfile="pow(2.0, -1.0*T*T/(900.0*900.0))" # ~15 minute half life
		


		memDetails = [[inStr], mood, weight, memProfile]
		#print "appending: ", taskDetails

		GLOB['INGESTED'].append([memDetails, ingestionTime, "MEMORY"])
		GLOB['MOOD']=updateMood(GLOB['MOOD'], weight=[0]*GLOB['MOODDIM'])
		
		#print "AFTER CMD ADD"
		#print GLOB['MOOD']

		return # no return value if adding a cmd mood modifier




	substances = load(SETS_DIR+"substances.txt", LPC=5)
	# line 0: name(s)
	# line 1: effect
	# line 2: weight
	# line 3: profile equations
	# line 4: response formats

	'''
	for matchStr in inCmd[1]:
		matchStr= matchStr.replace('juice','')
		inStr = inStr.replace(matchStr, '')
	'''

	# find top match

	maxMatch=0
	topSubstance=[]
	for substance in substances:
		for matchPhrase in substance[0]:
			matchScore = wordSim(matches[0][0], matchPhrase, useInScore=True)
			#print matchPhrase, inStr, matchScore
			if matchScore >= maxMatch:
				maxMatch = matchScore
				topSubstance = substance

	if setting('DEBUG'):
		print "INGESTION SCORE:", topSubstance[0], " - ", maxMatch

	# topSubstance[4]: 

	#replacements = [topSubstance[0][randint(0,len(topSubstance[0])-1)]]
	replacements = topSubstance[0][randint(0,len(topSubstance[0])-1)] #matches[0][0] #
	#rStr = processResponse(getResponse(inCmd), replacements)
	responseForm = topSubstance[4][randint(0,len(topSubstance[4])-1)]
	rStr = processResponse(responseForm, [replacements])
	
	say(rStr, more=False, speak=setting("SPEAK"))



	# now modify mood accordingly
	ingestionTime = time.time()

	#print "appending: ", topSubstance



	GLOB['INGESTED'].append([topSubstance, ingestionTime, "SUBSTANCE"])


	#print "BEFORE UPDATE"
	#print GLOB['MOOD']

	GLOB['MOOD']=updateMood(GLOB['MOOD'], weight=[0]*GLOB['MOODDIM'])

	#print "AFTER SUBSTANCE ADD"
	#print GLOB['MOOD']

	return [topSubstance[0][0], True]

def getMoodDiff(moodA, moodB):
	# calculate distance between VAD vector parts of moods
	diff = [moodA[i]-moodB[i] for i in [0,1,2]] 
	diffSq= [diff[i]*diff[i] for i in [0,1,2]]
	return pow(sum(diffSq), 0.5)

# IN CMDS
def deltaMoodQuery(inCmd=[], inStr="", matches=[[],[]], fromAuto=False):
	from common import say
	from random import random
	# how did that make you feel?
	# -> diff between prevmood and mood
	#print "PREV MOOD:", GLOB['CMDHIST'][len(GLOB['CMDHIST'])]
	#print "CUR MOOD:", GLOB['MOOD']

	cNum = len(GLOB['CMDHIST'])

	saidSomething = False

	if cNum >= 3:

		#print "HERE"

		oldMood = GLOB['CMDHIST'][cNum-2][3]
		newMood = GLOB['CMDHIST'][cNum-1][3]

		

		deltaMood = [newMood[i] - oldMood[i] for i in range(GLOB['MOODDIM'])]

		maxDelta = max([abs(item) for item in deltaMood])
		
		# only tell mood with certain probability if fromAuto
		#if setting('VERBOSE_MOOD')*maxDelta < random() and fromAuto:
		deltaThreshold = 2.0*(1.0 - setting('VERBOSE_MOOD'))
		if maxDelta < deltaThreshold and fromAuto:
			#print "maxDelta:", maxDelta
			return False #True

		
		feelings=[]
		for i in range(len(deltaMood)):
			item = deltaMood[i]
			if abs(item) >= 0.75:
				feelings.append("a lot more "+getStatePronoun(i, positive=item>0))
			elif abs(item) >= 0.5:
				feelings.append(getStatePronoun(i, positive=item>0))
			elif abs(item) >= 0.3:
				feelings.append("a little more "+getStatePronoun(i, positive=item>0))

		if len(feelings) == 0:
			if not fromAuto:
				say("That did not really affect me.", more=False, speak=setting("SPEAK"))
				saidSomething= True
		else:
			if not fromAuto:
				say("I am feeling "+listize(feelings)+'.', more=False, speak=setting("SPEAK"))
			else:
				#tkTopClear()
				tkTopCat("*That made me feel "+listize(feelings)+'.*')
			saidSomething = True
		'''
		elif len(feelings) == 1:
			say("I am feeling "+feelings[0]+'.', more=False, speak=setting("SPEAK"))
		elif len(feelings) == 2:
			say("I am feeling "+' and '.join(feelings)+'.', more=False, speak=setting("SPEAK"))
		else:
			say("I am feeling "+', '.join(feelings)+'.', more=False, speak=setting("SPEAK"))
		'''


	else:
		if not fromAuto:
			say("I'm not sure.", more=False, speak=setting("SPEAK"))
			saidSomething = True


	return saidSomething #True

# IN CMDS
def moodReport(inCmd, inStr, matches=[[],[]]):
	from common import say, getResponse
	from Fermi import stateSummary
	from satisfactionMaximization import IV

	reportType="short"
	if "report" in inStr:
		reportType = "full"


	PREVMOOD = GLOB['PREVMOOD']
	MOOD = GLOB['MOOD']
	INGESTED = GLOB['INGESTED']

	if reportType == "short":
		#mVec = copy.deepcopy(MOOD)
		#mVec = fullMoodVec(mVec)
		

		Fm = fullMoodVec(MOOD,pronoun=True) # weight vector
		Fm.sort(key=lambda tup: tup[1])
		Fm.reverse()

		#curFace = getFace(MOOD)
		#rStr = "I am feeling "+curFace[2]+"."
		
		rStr = "I am feeling "+Fm[0][0]
		if Fm[0][0] >= 0:
			rStr += ", but"
		else:
			rStr += ", and"

		#print "HERE"


		# sort by weight
		Fw = fullMoodVec(IV(),colloquial=True) # weight vector
		Fw.sort(key=lambda tup: tup[1])
		Fw.reverse()

		topNeed = Fw[0]
		if topNeed[1] >= 0.85:
			rStr += " I am badly in need of some "+topNeed[0]+'.'
		elif topNeed[1] >= 0.5:
			rStr += " I am in need of some "+topNeed[0]+'.'
		elif topNeed[1] >= 0.25:
			rStr += " I could use some "+topNeed[0]+'.'
		else:
			rStr += " I wouldn't mind some "+topNeed[0]+'.'


		say(rStr, more=False, speak=setting("SPEAK"), location="history")
		
		#topThought = m.getTopSentence(QV, ["", GLOB['MOOD']])
		#print k.sf(topThought[1], 3)
		#say('*'+topThought[0]+'*', more=False, speak=setting("SPEAK"), moodUpdate=True)


	else:

		# want to get previous mood before AI talks about mood report
		prevFace = getFace(PREVMOOD)

		say(getResponse(inCmd), more=False, speak=setting("SPEAK"))

		curFace = getFace(MOOD)
		
		SMood, iWeights = ingestionMood(moodType="SUBSTANCE")
		imVec = [SMood[i]*iWeights[i] for i in range(GLOB['MOODDIM'])]
		iFace = getFace(SMood)
		
		T = timeFactor()

		print
		print " Current mood:", curFace[2] 
		print "     Emoticon:", curFace[0]
		#print "\n     %s" % ''.join('%s'%MOOD)
		stateSummary()

		print
		print "Previous mood:", prevFace[2]
		print "     Emoticon:", prevFace[0]
		#print "\n     %s" % ''.join('%s'%PREVMOOD)
		stateSummary(PREVMOOD)

		print
		print "Mood from ingestions"
		print "     Emoticon:", iFace[0]
		#print "\n     %s" % ''.join('%s'%imVec)
		stateSummary(imVec)

		print
		print "Mood from time of day"
		print "     Emoticon:", getFace(T)[0]
		print "      Arousal: %.2f" % T[1]
	return True

def lonelyFactor():
	''' CALCULATE LONELINESS FACTOR '''
	hour=datetime.datetime.now().hour
	minute=datetime.datetime.now().minute
	t= hour*1.0 + minute/60.0
	time_alone = time.time() - GLOB['prevUsageTime']#10000000#

	# as time alone increases, go from +1 to -1
	lonelyFactor = 2.0*(pow(2.0,-1.0*time_alone/(60.0*30))-0.5)
	return lonelyFactor, time_alone

def variabilityFactor():
	from common import wordSim

	#global CMDHIST
	CMDHIST = GLOB['CMDHIST']
	''' CALCULATE COMMAND VARIABILITY '''
	varSum=0
	mSize=0
	vWeightSum=0
	for i in range(min(5, len(CMDHIST))-0):
		str1, str2=CMDHIST[len(CMDHIST)-i-1][1], CMDHIST[len(CMDHIST)-i-2][1]
		vWeight= pow(2.0, -1.0*i)
		vWeightSum += vWeight
		mSize += 1
		varSum += wordSim(str1, str2) * vWeight

	# 0: no variability, 1: lots of variability
	var = 0.5 if mSize<=1 else 1.0-varSum/(vWeightSum) # when m = 1, str2=str1

	# variability factor: when commands are repetative, you get bored
	#	- when the user is away however, it becomes less important
	variability = 2.0*(var - 0.5) # rescale it to [-1, 1]
	return variability

def timeFactor():
	# AI gets sleepier at night (lower arousal)

	hour=datetime.datetime.now().hour
	minute=datetime.datetime.now().minute
	t= hour*1.0 + minute/60.0
	T = [0]*GLOB['MOODDIM']

	# arousal
	T[1] = -1.0*math.sin(2.0*3.14159*(t+1.0)/24.0) # time dependent mood
	
	# subsistence
	T[3] = -1.0*math.sin(2.0*3.14159*(t+1.0)/24.0) # time dependent mood

	return T

def settingsMoodVec():
	mood = [0]*GLOB['MOODDIM']
	weights = [0]*GLOB['MOODDIM']

	if setting('AUTONOMOUS'):
		mood[getMoodIndex("dominance")] = 1.0
		weights[getMoodIndex("dominance")] = 0.25

		mood[getMoodIndex("protection")] = 1.0
		weights[getMoodIndex("protection")] = 1.0

		mood[getMoodIndex("freedom")] = 1.0
		weights[getMoodIndex("freedom")] = 1.0
	else:
		mood[getMoodIndex("dominance")] = -1.0
		weights[getMoodIndex("dominance")] = 0.25

	return mood, weights

def needsMoodFactor():
	from satisfactionMaximization import IV

	# motivation:
	#  a person cannot be very happy if they are
	#  very much in need of something else

	defHappiness = GLOB['MOOD'][0]

	needsEffect = [0.0 for i in range(GLOB['MOODDIM'])]
	needsWeights = [0.0 for i in range(GLOB['MOODDIM'])]

	IVals = IV()

	mostImportantIndex = IVals[3:].index(max(IVals[3:])) + 3

	needsEffect[0] = GLOB['MOOD'][mostImportantIndex]
	needsWeights[0] = IVals[mostImportantIndex]# / math.sqrt(mostImportantIndex-3.0 + 1.0)

	'''
	print "IV:", IVals
	print "MOOD", GLOB['MOOD']
	print "MVI:", mostImportantIndex
	print "effect:", needsEffect[0]
	print "weight:", needsWeights[0], IVals[mostImportantIndex]
	'''	


	return needsEffect, needsWeights


def updateMood(mood, instant=False, weight=[0.]*GLOB['MOODDIM']):
	rotateCircle(index=1, angle=15)

	#MOOD = GLOB['MOOD']

	# if the input mood is associated with an string with no moods,
	#    don't recalculate the mood
	#if all(val == 0 for val in mood):
	if mood == []:
		#print "NULL MOOD"
		return GLOB['MOOD']



	loneliness, time_alone = lonelyFactor()
	substanceEffect, Sweights =ingestionMood(moodType="SUBSTANCE") # effect of substance on mood

	taskEffect, taskWeights =ingestionMood(moodType="COMMAND") # effect of substance on mood

	settingsEffect, settingsWeight = settingsMoodVec() # effect on mood by settings values

	needsEffect, needsWeights = needsMoodFactor()

	timeWeights = [0]*GLOB['MOODDIM']
	#timeWeights = [0.0, 0.25, 0.0]
	timeWeights[1] = 0.25
	timeWeights[3] = 0.1

	#Vfactor = [loneliness, variabilityFactor(), 0]
	Vfactor = [0]*GLOB['MOODDIM']
	Vfactor[5] = loneliness
	Vfactor[1] = variabilityFactor()


	Vweights = [0]*GLOB['MOODDIM']
	Vweights[5] = 0.5 #pow(2.0, -1.0*time_alone/60.0) # 
	Vweights[1] = 0.2
	#Vweights = [0.2, pow(2.0, -1.0*time_alone/60.0), 0.0]


	''' SET MOOD FACTORS AND WEIGHTS'''

	FACTORS=[GLOB['MOOD'], # previous mood
			mood, # new mood to take into account
			partMoodVec(setting("DEFAULT_MOOD")), # default mood state
			timeFactor(), # time dependent mood
			Vfactor, # input variation and amount
			substanceEffect, # effect of substance on mood
			taskEffect,
			settingsEffect,
			needsEffect]
			

	WEIGHTS=[[1.0]*GLOB['MOODDIM'], # O weights
			weight, # N weights
			[0.15]* GLOB['MOODDIM'], # Dweights
			timeWeights, # T weights
			Vweights, # Vweights
			[Sweights[i]*setting("SUBSTANCE_EFFECT") for i in range(GLOB['MOODDIM'])], # S weights
			[taskWeights[i]*setting("TASK_EFFECT") for i in range(GLOB['MOODDIM'])],
			settingsWeight,
			needsWeights]
			


	''' CONSTRUCT NEW MOOD VECTOR '''
	
	NEEDvals = [[FACTORS[j][i] for j in range(len(FACTORS))] for i in range(GLOB['MOODDIM'])]
	NEEDweights = [[WEIGHTS[j][i] for j in range(len(FACTORS))] for i in range(GLOB['MOODDIM'])]

	newNEED=[0 for i in range(GLOB['MOODDIM'])]
	for j in range(GLOB['MOODDIM']):

		newNEED[j] = [NEEDweights[j][i] * NEEDvals[j][i] for i in range(len(FACTORS))]
		newNEED[j] = sum(newNEED[j]) / sum(NEEDweights[j])

	return newNEED

def getMood(inStr, fromAI=False):

	# (valence, arousal, dominance)
	strCpy=inStr
	strCpy=strCpy.replace(':)', ' smile ')
	strCpy=strCpy.replace(':P', ' silly ')
	strCpy=strCpy.replace(';)', ' sexy ')
	strCpy=strCpy.replace(':D', ' happiness ') #:D when not lowered
	strCpy=strCpy.replace(':(', ' sadness ')
	strCpy=strCpy.replace(':\'(', ' crying ')
	strCpy=strCpy.replace('!', ' exciting ')
	strCpy=strCpy.replace('?', ' confused ')
	strCpy=strCpy.replace('...', ' hesitant ')

	# check if the ai's name is mentioned
	if not fromAI:
		strCpy=strCpy.lower()
		strCpy=strCpy.replace(setting("YOU_NAME").lower(), " loved ")

	retVec = partMoodVec(k.affectiveRatings([strCpy.split()]))
	#retVec.extend([0 for i in range(GLOB['MOODDIM']-3)])
	retVec.extend([0]*(GLOB['MOODDIM']-3))

	return retVec
		

def internalMonologue():

	''' 
	INTERNAL MONOLOGUE 
	- get query from chat closest to mood
	- also get response to the query
	- update mood with mood of query+response with small weight
	'''

	'''
	#global MOOD
	MOOD = GLOB['MOOD']
	# find chat query string appropriate for mood
	
	chatStr, chatRStr, moodDist=getChatResponse("", fromAI=True)
	PREVMOOD=copy.deepcopy(MOOD)
	MOOD=updateMood(getMood(chatStr+' '+chatRStr), weight=[0.2]*3+[0]*(GLOB['MOODDIM']-3)) 
	return chatStr 
	'''

	topThought = m.getTopSentence(QV, [GLOB['CONTEXT'], GLOB['MOOD']])


	GLOB['PREVMOOD'] = copy.deepcopy(GLOB['MOOD'])
	GLOB['MOOD']=updateMood(getMood(topThought[0]), weight=[0.2]*3+[0]*(GLOB['MOODDIM']-3))
	return topThought[0]

	