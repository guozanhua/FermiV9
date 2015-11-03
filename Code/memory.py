from header import *
from common import *
from fileIO import jsonSave
from graphics import *

'''
	memory.py:
		- context updating and substituting
		- memory substitution
		- adding new context memories

	(aasr.py is for adding and querying factual memories)

'''

def getMemoryTitle(mem):

	if mem['context']!="":
		titleStr = mem['context']
	else:
		titleStr = mem['recentHist'][len(mem['recentHist'])-1]


	absDM = [abs(m) for m in mem['deltaMood']]
	maxIndex = absDM.index(max(absDM))

	goodMemory = (mem['deltaMood'][maxIndex] >= 0)

	titleStr += ' '+getStatePronoun(maxIndex, positive=goodMemory)
	return titleStr

def getMemoryStr(mem, confidence, memType):
	magnitude = mem['weight']

	posSum = 0
	negSum = 0
	for m in mem['deltaMood']:
		#changeSum += math.copysign(m*m, m) #m^2 with the original sign
		if m > 0:
			posSum += m
		else:
			negSum += -1.0*m

	rStr=""

	if memType == "predict":
		if confidence >= 0.8:
			rStr += "strongly predict"
		else:
			rStr += "predict"
	else:
		if confidence >= 0.8:
			rStr += "am strongly reminded of"
		else:
			rStr += "am reminded of"

	rStr += " something "

	if magnitude >= 1.5:
		rStr += "very"
	else:
		rStr += "a little"

	if posSum > 1.5*negSum:
		rStr += ' good'
	elif negSum > 1.5*posSum:
		rStr += ' bad'
	else:
		rStr += ' mixed'

	return rStr

def memoryImportance(mem, confidence):

	recalls = mem['count_recalled']
	happens = mem['count_happened']

	# simple initial model
	importance = mem['novelty'] * mem['weight'] * (happens+1.0)/(recalls+1.0)

	return importance

def rememberMemory(mem, confidence, memType):
	from emotions import ingest

	if mem=={} or memType=="":
		return

	if (confidence < 0.4 and memType == "remember"):
		return False
	elif (confidence < 0.6 and memType == "predict"):
		return False


	playMemSound(mem)

	importance = memoryImportance(mem, confidence)

	# UPDATE MEMORY DETAILS
	memIndex = GLOB['AUTOBIOGRAPHIC_MEMORY'].index(mem)
	GLOB['AUTOBIOGRAPHIC_MEMORY'][memIndex]['count_recalled'] += 1

	if confidence >= 0.95 and memType == "remember":
		GLOB['AUTOBIOGRAPHIC_MEMORY'][memIndex]['count_happened'] += 1

	jsonSave(GLOB['AUTOBIOGRAPHIC_MEMORY'], DATA_DIR+'autobiographic_memory.txt')


	# decide if we're going to act on the memory
	# count_recalled
	# count_happened
	# -> if the memory is often recalled but never happens and weight is low
	#    then we don't act on it
	
	if memoryImportance(mem, confidence) < 0.5:
	#	print "IMPORTANCE = ", importance
		return False

	#sayStr = "*I "+getMemoryStr(mem, confidence, memType)+' %s'%round(importance, 2)+'.*'
	#sayStr += ' '+mem['title']
	
	sayStr = "*I "+getMemoryStr(mem, confidence, memType)+'.*'
	say(sayStr, more=False, speak=setting("SPEAK"), location="top")

	if sum(mem['deltaMood']) >= 0:
		memoryAnimation(mood="positive")
	else:
		memoryAnimation(mood="negative")

	memMood=[m[0]+m[1] for m in zip(GLOB['MOOD'], mem['deltaMood'])]
	memMood = [max(min(memMood[i], 1), -1) for i in range(GLOB['MOODDIM'])]



	# weight of each facet of memory is equal to the magnitude of the
	#   emotion change in that memory
	memWeight = [abs(m)*confidence for m in mem['deltaMood']]

	if memType == "predict":
		memWeight = [m*0.25 for m in memWeight]

	# add memory effects to mood
	ingest(inCmd=[], inStr=mem['title'], mood=memMood, weight=memWeight, isMem=True)

	return True

def autobiographicRecall(useContext=True, useHistory=True):

	# only look for recall if hist to look at
	#  and if we actually have memories
	if len(GLOB['CMDHIST']) < 3 or len(GLOB['AUTOBIOGRAPHIC_MEMORY']) == 0:
		return [{}, 0, ""]

	if not useContext and not useHistory:
		return [{}, 0, ""]

	#contextRareness = k.wordRareness(GLOB['CONTEXT'])

	memLen = len(GLOB['AUTOBIOGRAPHIC_MEMORY'][0]['recentHist'])

	cNum = len(GLOB['CMDHIST'])
	realRecentHist = [GLOB['CMDHIST'][cNum-1-i][1] for i in range(memLen-1, -1, -1)]

	# check if recent history reminds you of something
	#  stored in autobiographic memory

	# check for context match as well as recent hist match

	topScore = 0
	topMemory = {}
	topMatchType = ""
	for mem in GLOB['AUTOBIOGRAPHIC_MEMORY']:
		contextScore = wordSim(GLOB['CONTEXT'], mem['context'], basic=True)

		#print GLOB['CONTEXT'], mem['context'], "->", contextScore
		#contextScore *= (contextRareness*0.5 + 0.5)
		
		histRememberScore = 0
		# get sum of string matches
		for hp in zip(realRecentHist, mem['recentHist']):
			
			s = wordSim(hp[0], hp[1], basic=True)
			if s >= 0.8:
				#print "COMPARING:", hp[0], "vs", hp[1], "->", s
				histRememberScore += 1.0/(memLen)

		histPredictScore = 0
		# get sum of string matches
		for hp in zip(realRecentHist[1:], mem['recentHist'][:memLen-1]):
			#print "COMPARING:", hp[0], "vs", hp[1]
			s = wordSim(hp[0], hp[1], basic=True)
			if s >= 0.8:
				histPredictScore += 1.0/(memLen-1.0)

		matchType = ""
		if histRememberScore > histPredictScore:
			matchType = "remember"
		else:
			matchType = "predict"


		score = 0
		if useContext:
			score += contextScore
		if useHistory:
			score += 2.0*max(histRememberScore, histPredictScore)
		
		if score >= topScore:
			topScore = score
			topMemory = copy.deepcopy(mem)
			topMatchType = matchType



			#print contextScore, histRememberScore, histPredictScore, mem['context']

	maxPossibleScore = 0.0
	if useContext:
		maxPossibleScore += 1.0
	if useHistory:
		maxPossibleScore += 2.0
	topScore = topScore / maxPossibleScore

	topScore = topScore #*min(1.0, 0.5*topMemory['novelty'])

	#print "TOP MEM:", topMemory['title'], "score = ", topScore, "type = ", topMatchType
	#print "MEM:", topMemory
	#print "HIST = ", realRecentHist

	return topMemory, topScore, topMatchType

	#return

def getMemoryNovelty(mem):
	# first check that weight >= threshold

	# mem['weight'] = sum of abs vals in mem['deltaMood']

	# novelty based on:
	#	- context uniqueness
	#	- deltaMood uniqueness
	#	- mem weight (sum of delta mood)

	contextRareness = k.wordRareness(mem['context'])
	# since we don't want to completely ignore a new event with
	#   a boring context
	cRF = contextRareness*0.5 + 0.5

	if len(GLOB['AUTOBIOGRAPHIC_MEMORY']) == 0:
		deltaMoodNovelty = mem['weight']
		contextNovelty = cRF
		return deltaMoodNovelty + contextNovelty

	# see the smallest difference between the new
	# memory and an older one
	lowestNovelty = [float('inf'), float('inf')]
	closestMem = {}

	for oldMem in GLOB['AUTOBIOGRAPHIC_MEMORY']:

		#deltaMoodNovelty = mem['weight']*getVecDiffSum(mem['deltaMood'], oldMem['deltaMood'])
		deltaMoodNovelty = getVecDiffSum(mem['deltaMood'], oldMem['deltaMood'])
		contextNovelty = cRF*(1.0 - wordSim(mem['context'], oldMem['context'], basic=True))

		#novelty = deltaMoodNovelty + contextNovelty

		if deltaMoodNovelty + contextNovelty < sum(lowestNovelty):
			lowestNovelty = [deltaMoodNovelty, contextNovelty]
			closestMem = copy.deepcopy(oldMem)


	'''
	print "dMoodNovelty:", lowestNovelty[0]
	print "contextNovelty:", lowestNovelty[1], "cRF = ", cRF
	print "weight = ", mem['weight']
	print "closestMem:", closestMem['context'], closestMem['recentHist'][2]
	'''
	return sum(lowestNovelty)

def playMemSound(mem):
	if setting('QUIET'):
		return

	vSum = sum(m for m in mem['deltaMood'])
	if vSum >= 0:
		playSound("chirp-happy", delay=round(1.5*random(),2))
	else:
		playSound("chirp-sad", delay=round(1.5*random(),2))

def addAutobiographicMemory(threshold = 1.5):
	# memory:
	#	- time tag
	#	- delta mood vector
	#	- context
	#	- recent cmd hist

	new_mem = {}

	memLen = 3

	# check that memory is of sufficient emotional magnitude
	# deltaM12 = delta mood

	cNum = len(GLOB['CMDHIST'])
	
	if cNum < memLen:
		return False
	
	oldMood = GLOB['CMDHIST'][cNum-2][3]
	newMood = GLOB['CMDHIST'][cNum-1][3]

	deltaMood = [round(newMood[i] - oldMood[i], 2) for i in range(GLOB['MOODDIM'])]
	maxDelta = max([abs(item) for item in deltaMood])
	memoryWeight = sum([abs(item) for item in deltaMood])

		


	NowTime = datetime.datetime.now()
	NowTotalSecs = (NowTime-datetime.datetime(1970,1,1)).total_seconds()

	new_mem['deltaMood'] = deltaMood
	#new_mem['mood'] = GLOB['CMDHIST'][cNum-1][3]
	new_mem['weight'] =round(memoryWeight, 3)
	new_mem['time'] = NowTotalSecs
	new_mem['context'] = GLOB['CONTEXT']
	# get the last memLen commands: [old, .. , new]
	new_mem['recentHist'] = [GLOB['CMDHIST'][cNum-1-i][1] for i in range(memLen-1, -1, -1)]
	new_mem['novelty'] = round(getMemoryNovelty(new_mem), 3)

	new_mem['title'] = getMemoryTitle(new_mem)

	new_mem['count_recalled'] = 0
	new_mem['count_happened'] = 0

	#print "weight, maxDelta, novelty = ", memoryWeight, maxDelta, new_mem['novelty']

	if new_mem['novelty'] >= threshold and (new_mem['weight'] >= 1.5 or maxDelta >= 0.5):

		GLOB['AUTOBIOGRAPHIC_MEMORY'].append(new_mem)

		jsonSave(GLOB['AUTOBIOGRAPHIC_MEMORY'], DATA_DIR+'autobiographic_memory.txt')

		playMemSound(new_mem)

		return True
	else:
		return False

		#print "ADDING MEMORY:", "weight, maxDelta, novelty = ", memoryWeight, maxDelta, new_mem['novelty']
	#else:
		#print "FORGETTING", "weight, maxDelta, novelty = ", memoryWeight, maxDelta, new_mem['novelty']
	#print new_mem


def substituteContext(inStr, maxLength=2, reSub=False):

	if len(GLOB['CONTEXT']) == 0: return inStr

	# prevent context: do not replace word with -c
	stopContext = ('-c' in inStr)
	if stopContext:
		return inStr.replace('-c', '').strip()


	# force context: replace word that has +c with context
	forceContext = ('+c' in inStr)



	# only substitute if it's the only word
	contextSuitable = (len(inStr.split()) <= maxLength) or forceContext

	#print "CONTEXT:", GLOB['CONTEXT']
	#print "CONTEXT SUITABLE:", contextSuitable
	#print "ANALYZING FOR CONTEXT SUB: ", inStr

	# TODO: only replace with context if it fits the type
	vagueItWords = ["it", "these", "those", "this", "that"]
	vaguePeopleWords = ["them", "they", "him", "her", "he", "she"]

	vagueWords = vagueItWords+vaguePeopleWords

	if contextSuitable:
		inStr = inStr.split()

		for j in range(len(inStr)):
			cleanStr = inStr[j].lower()
			cleanStr = cleanStr.replace('?', '')
			cleanStr = cleanStr.replace('.', '')
			if cleanStr in vagueWords or '+c' in cleanStr:
				if setting('DEBUG'):
					print "CONTEXT SUB:", inStr[j], "->", GLOB['CONTEXT']
				inStr[j] = GLOB['CONTEXT']

		inStr = ' '.join(inStr)

	#print "CONTEXTED:", inStr
	if reSub:
		inStr = substituteBiographicMemory(subStr=inStr, subContext=False)
		#print "\tRESUB:", inStr
	return inStr

def substituteBiographicMemory(matches=[[],[]], subStr="", queryType='what is',
								append=False, subContext=True, onlyContext=False, maxContextSub=2):
	# from determineFunction import findCMD

	if matches == [[],[]] and subStr != "":
		matches[0].append(subStr)

	# substitute context for value words

	#qCmd = findCMD("queryPersonalData")
	for i in range(len(matches[0])):

		if setting('CONTEXT') and subContext:
			#print "PRE:", matches[0][i]
			matches[0][i] = substituteContext(matches[0][i], maxLength = maxContextSub)	
			#print "POST:", matches[0][i]	

		if not onlyContext:

			# see if it is in memory

			#res = queryPersonalData(qCmd, inStr=queryType+' '+matches[0][i], rawData=True)

			
			res=""
			queryStr=""
			if not aasr.clearlyQuestion(matches[0][i]):
				queryStr = queryType+' '+matches[0][i]
			else:
				queryStr = matches[0][i]

			#queryRes = aasr.queryFacts(queryStr)[0]
			queryRes = aasr.queryFacts(queryStr, factList=GLOB['FACTUAL_MEMORY'], topOne=True)[0]

			score = queryRes[3]
			if score > 0.5:
				res = queryRes[2]
				#res = ' '.join(res)

			if setting('DEBUG'):
				print "MEMORY QUERY:", queryStr, "->", res, "SCORE:", score

			if '%s'%res in ["True", "False"]:
				res = ""

			if res != "":
				#print "FOUND DATA:", res
				if setting('DEBUG'):
					print "FOUND DATA:", res
				if append:
					matches[0][i] = matches[0][i]+' ('+res+')'
				else:
					matches[0][i] = res
	
	if subStr != "":
		return matches[0][0]
	else:
		return matches

def updateContext(matches=[[],[]], inStr="", cmdConfidence=0):

	# check if the context has been freed
	if GLOB['contextLocked']:
		return

	if setting('DEBUG'):
		print "CONTEXT inStr:", inStr

	# get guess from matches
	#print "Matches:", matches
	if len(matches[0]) >= 1 and cmdConfidence >= 0.95:
		if setting('DEBUG'):
			print "CONTEXT matches:", matches[0]
		
		bioSub = substituteBiographicMemory(matches, queryType='what is', append=False)[0]
		bioSub = bioSub[len(bioSub)-1]
		
		if setting('DEBUG'):
			print "\t = ", bioSub
			print "\tcmdConfidence = ", cmdConfidence

		F = k.filter([bioSub.split()], lemmatize=False, lemType=1, removeStops=True)
		if len(F[0]) != 0 and bioSub.lower() not in ["true", "false"] and not "eval(" in inStr:
			GLOB['CONTEXT'] = bioSub
			GLOB['contextLocked'] = True
			return
		else:
			if setting('DEBUG'):
				print "\t (too short so using unfiltered)"
			GLOB['CONTEXT'] = bioSub
			GLOB['contextLocked'] = True
			return

		return

	if len(inStr.split()) >= 1:


		# check if its code
		if ("eval(" in inStr):
			return

		#K = k.filter([meantStr.split()], lemmatize=False, lemType=1, removeStops=True)

		# first look for nouns
		inStr = expandContractions(inStr)

		'''
		print "PRE INSTR:", inStr
		inStrSub = substituteBiographicMemory(subStr=inStr)
		print "POST INSTR:", inStrSub

		if inStr != inStrSub:
			GLOB['CONTEXT'] = inStrSub
			GLOB['contextLocked'] = True
			return
		'''

		filteredStr = k.filter([inStr.split()], lemmatize=False, lemType=1, removeStops=False)
		N = k.nouns(filteredStr)
		if len(N) >= 1:
			if setting('DEBUG'):
				print "CONTEXT nouns:", N[0][0]
			GLOB['CONTEXT'] = N[0][0]
			GLOB['contextLocked'] = True
			return

		F = k.filter([inStr.split()], lemmatize=False, lemType=1, removeStops=True)
		Ff = k.getWordFreqs(F)
		if len(Ff) >= 1:
			if setting('DEBUG'):
				print "CONTEXT filter:", Ff[0][0]
			GLOB['CONTEXT'] = Ff[0][0]
			GLOB['contextLocked'] = True
			return
	return

