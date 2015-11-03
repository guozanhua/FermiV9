import difflib		# for string similarity
import re
from random import *
import copy

bracketFreePatternStr = ""
testedMatches=[]
testedScores=[]

savedQuestions=[]
savedAnswers=[]
#numDups = 0
#totalTrials = 0

def patternWordSim(wA, wB):
	raw = difflib.SequenceMatcher(a=wA.lower(), b=wB.lower()).ratio()
	return raw


def removeRanges(matches, inStr):
	# >>> testMatch([[1,2], [3, 4]], "the cat in the hat")
	# 'the in the'
	words = inStr.split()

	# need to go in reverse order so that
	#   ranges do not changes words they apply to
	revMatches = [item for item in matches]
	revMatches.reverse()

	for item in revMatches:
		words = words[:item[0]]+words[item[1]:]

	return ' '.join(words)	

def fillPattern(matches, patternStr, inStr, subs):

	global bracketFreePatternStr

	varSet = []
	for match in matches[0]:
		varSet.append(inStr.split()[match[0]:match[1]])


	subsSet = [] # words that go into sub spots
	for i in range(len(matches[1])):
		subsSet.append(subs[i][matches[1][i]])

	# remove things between []'s so we can easily replace with test matches
	patternStr = bracketFreePatternStr #re.sub('\[.*?\]','[]', patternStr)

	patternStr = patternStr.split()
	
	pos = 0
	for i in range(len(patternStr)):
		if patternStr[i] == "[]":
			patternStr[i] = subsSet[pos]
			pos += 1

	pos = 0
	for i in range(len(patternStr)):
		if patternStr[i] == "{}":
			patternStr[i] = ' '.join(varSet[pos])
			pos += 1

	patternStr = ' '.join(patternStr)

	return patternStr

def testMatch(matches, inStr, patternStr, subs):
	# matches: [[var substitutions], [sub tests]]
	# inStr: origin string to find matches in
	# patternStr: pattern string with []s and {}s

	patternStr = fillPattern(matches, patternStr, inStr, subs)

	simScore = patternWordSim(re.sub('\s+', ' ', inStr.strip()), re.sub('\s+', ' ', patternStr.strip()))
	#simScore = patternWordSim(inStr.strip(), patternStr.strip())

	#if simScore >= 0.6:
	#	print patternStr.strip(), " & ", inStr.strip(), " -> ", simScore

	return simScore
	
def perturbMatch(matches, numVars, numWords, subs):
	# match: [[[1,2], [4,6]], [0, 1]]

	#S = [randint(0, numWords) for i in range(numVars*2)]
	#S.sort()

	#matches[0] = [[S[2*i],S[2*i+1]] for i in range(numVars)]

	# extract current sorted index list
	S = []
	for item in matches[0]:
		S.append(item[0])
		S.append(item[1])

	# now perturn index list
	for i in range(len(S)):
		if random() > 0.5:
			S[i] = min(max(S[i] + randint(-1, 1), 0), numWords)
	#print " S:", S
	S.sort()
	#print "Ss:", S

	# reassign S
	matches[0] = [[S[2*i],S[2*i+1]] for i in range(numVars)]

	for i in range(len(matches[1])):
		if random() > 0.75:
			matches[1][i] = randint(0, len(subs[i])-1)

	return matches


def randomMatch(numVars, numWords, subs):
	matches=[[[] for i in range(numVars)], []]#[[] for i in range(len(subs))]]

	# note: randint is inclusive

	#S = sample(range(0, numWords+1), numVars*2)
	S = [randint(0, numWords) for i in range(numVars*2)]
	S.sort()

	matches[0] = [[S[2*i],S[2*i+1]] for i in range(numVars)]

	# choose random subs from lists
	matches[1] = [randint(0, len(sub)-1) for sub in subs]

	return matches

	# 

def cleanStr(inStr):
	if not ("(" in inStr and ")" in inStr):
		inStr = inStr.replace('"', '').replace('\'', '')
	
	inStr = inStr.strip()
	#inStr = inStr.replace('?', '')
	if inStr[len(inStr)-1] == '?':
		inStr = inStr.replace('?', '')

	return inStr

def hillClimb(patternStr, inStr, numVars, numWords, subs, trials=100, earlyQuit=False):
	
	global testedMatches, testedScores #, numDups, totalTrials

	bestMatches = randomMatch(numVars, numWords, subs)
	maxScore = testMatch(bestMatches, inStr, patternStr, subs)

	bestLenSum = pow(len(inStr)+10, 2.0)
	bestSubNum = 0

	# don't let them get too big
	if len(testedMatches) >= 100:
		testedMatches=[]
		testedScores=[]


	for t in range(trials): # random trials

		

		#totalTrials += 1

		# now slightly perturb guess
		#if matches != bestMatches:
		matches = copy.deepcopy(bestMatches)
		#else:
		#	print "COPY SKIPPED"
		matches = perturbMatch(matches, numVars, numWords, subs)

		score=0

		if matches not in testedMatches:

			testedMatches.append(matches)
			score = testMatch(matches, inStr, patternStr, subs)
			testedScores.append(score)

		else:
			score = testedScores[testedMatches.index(matches)]

		#score = testMatch(matches, inStr, patternStr, subs)

		lenSum = sum([(m[1]-m[0])*(m[1]-m[0]) for m in matches[0]])
		subNum = len(matches[1])

		if score > maxScore:
			maxScore = score
			bestMatches = copy.deepcopy(matches)
			bestLenSum = lenSum
			bestSubNum = subNum
		elif score == maxScore and lenSum < bestLenSum:
			#print "MINIMIZE LENGTH"
			maxScore = score
			bestMatches = copy.deepcopy(matches)
			bestLenSum = lenSum
			bestSubNum = subNum
		'''
		if score == maxScore and subNum > bestSubNum:
			#print "MAXIMIZE SUBS"
			maxScore = score
			bestMatches = copy.deepcopy(matches)
			bestLenSum = lenSum
			bestSubNum = subNum
		'''

		# see if we've actually found the best match
		if maxScore == 1.0 and earlyQuit:
			break
		#else:
			#numDups += 1
			#print "TESTED", len(testedMatches)

	return bestMatches, maxScore

def optimization(patternStr, inStr, trials=5, subTrials=100, earlyQuit=False):
	''' ------------ '''
	''' OPTIMIZATION '''
	''' ------------ '''

	inStr = cleanStr(inStr)
	patternStr = cleanStr(patternStr)


	# assuming properly used braces and none used
	#   unless for patterns
	numVars= len(re.findall(r"\{\}", patternStr))
	numSubs = len(re.findall(r"\[", patternStr))
	numWords = len(inStr.split())

	# check if theres actually stuff to do
	if numSubs == 0 and numVars == 0:
		#print "\tSHORTCUT"
		return [[],[]], patternWordSim(re.sub('\s+', ' ', inStr.strip()), re.sub('\s+', ' ', patternStr.strip()))

	subs = re.findall(r"\[([^]]+)\]", patternStr)
	subs = [item.split(',') for item in subs]
	subs = [[item.strip() for item in sub] for sub in subs]


	bestMatches = randomMatch(numVars, numWords, subs)
	maxScore = testMatch(bestMatches, inStr, patternStr, subs)

	bestLenSum = pow(len(inStr)+10,2) # want to minimize sum of length of matches
	bestSubNum = 0

	for t in range(trials): # random trials

		# quit early if we've done some trials and are getting nowhere
		if t >= 1 and maxScore <= 0.7 and subTrials >= 75:
			#print "EARLY QUIT 1"
			break
		elif t >= 2 and maxScore <= 0.7 and subTrials >= 50:
			#print "EARLY QUIT 2"
			break

		#matches = copy.deepcopy(bestMatches)

		# now slightly perturb guess
		#matches = perturbMatch(matches, numVars, numWords, subs)
		matches, score = hillClimb(patternStr, inStr, numVars, numWords, subs, trials=subTrials, earlyQuit=earlyQuit)

		#print "matches: ", matches
		lenSum = sum([pow(m[1]-m[0],2) for m in matches[0]])
		subNum = len(matches[1])

		#score = testMatch(matches, inStr, patternStr, subs)

		if score > maxScore:
			maxScore = score
			bestMatches = copy.deepcopy(matches)
			bestLenSum = lenSum
			bestSubNum = subNum
		elif score == maxScore and lenSum < bestLenSum:
			#print "MINIMIZE LENGTH"
			maxScore = score
			bestMatches = copy.deepcopy(matches)
			bestLenSum = lenSum
			bestSubNum = subNum

		# see if we've actually found the best match
		if maxScore == 1.0 and earlyQuit:
			break

	return bestMatches, maxScore

def testOptimization(patternStr, inStr):
	totalTrials = 500


	global bracketFreePatternStr, testedMatches #, numDups, totalTrials
	testedMatches=[]
	testedScores=[]
	#numDups = 0
	#totalTrials=0
	bracketFreePatternStr = re.sub('\[.*?\]','[]', patternStr)

	#for trials in range(1, 25, 1):
	for tests in range(1, 15):
		trials = 5
		subTrials = 100

		#subTrials = 500/trials


		numRuns = 1
		scoreSum = 0
		for run in range(numRuns): # average over many runs

			bestMatches, score = optimization(patternStr, inStr, trials=trials, subTrials=subTrials)
			scoreSum += score

		print trials,"\t",subTrials,"\t",1.0*scoreSum/numRuns

def extractVarOrders(patternStr):
	# create order list of vars and remove 
	#   the numbers from braces

	origPatternStr = patternStr

	orderList = []

	patternWords = patternStr.split()
	newPatternWords = []

	curPos = 0
	foundNoIndex=False
	foundIndex=False
	for word in patternWords:

		i1 = word.find('{')
		i2 = word.find('}')
		if i2 > i1 and not (i2 == -1 or i1 == -1):

			# just remove the stuff between the braces
			newPatternWords.append(word[0:i1+1]+word[i2:])

			if i1 == i2-1: # no index provided
				orderList.append(curPos)
				curPos += 1
				foundNoIndex = True
			else:
				try:
					orderList.append(int(word[i1+1:i2]))
					foundIndex = True
				except:
					print "ERROR IN PATTERN VAR INDEX: index must be an integer", word
					return "", []
		else:
			newPatternWords.append(word)



		if foundIndex and foundNoIndex:
			print "ERROR IN PATTERN VAR INDEX: cannot combine indexed and non-index variables"
			return "", []

	# check if orderList contains all integers from min to max, starting from 0
	S = copy.deepcopy(orderList)
	S.sort()
	if len(S) != 0:
		if S[0] != 0:
			print "ERROR IN PATTERN VAR INDEX: 0 index missing:", origPatternStr
			return "", []
	for i in range(len(S)-1):
		if S[i]+1 != S[i+1]:
			print "ERROR IN PATTERN VAR INDEX: missing indices:", origPatternStr
			return "", []

	return ' '.join(newPatternWords), orderList



def varMatches(patternStr, inStr, trials=5, subTrials=100, minSubs=1, earlyQuit=False):
	global bracketFreePatternStr, testedMatches, testedScores #, numDups, totalTrials
	global savedQuestions, savedAnswers

	# TREAT SOME OTHER CHARACTERS AS WORDS
	patternStr = patternStr.replace('],', '] ,')
	patternStr = patternStr.replace('},', '} ,')
	patternStr = patternStr.replace(':', ' :')
	inStr = inStr.replace(':', ' :')
	inStr = inStr.replace(',', ' ,')

	patternStr, orderList = extractVarOrders(patternStr)

	# simple pretest:
	cleanPattern = re.sub(r'[^\w'+' '+']', '',patternStr.lower().replace(':', 'is'))
	cleanPattern = re.sub('\s+', ' ', cleanPattern.strip())

	cleanInstr = inStr.lower().replace(':', 'is')
	pretestSim = patternWordSim(re.sub(r'[^\w'+' '+']', '',cleanPattern), cleanInstr)
	commonWords = len(set(cleanPattern.split()) & set(cleanInstr.split()))
	
	#print "PRETEST: ", pretestSim
	#print "COMMON: ", commonWords
	if not (pretestSim > 0.33 or commonWords >= minSubs):
		#print "PRETEST:", pretestSim, "inStr:", inStr
		return [[],[]], 0, 0

	origInStr = inStr

	inStr = cleanStr(inStr)
	
	inStr = inStr.replace(', and then', ' and then')
	inStr = inStr.replace(', then', ' then')

	# precalculate this to make testing faster
	bracketFreePatternStr = re.sub('\[.*?\]','[]', patternStr)
	testedMatches=[]
	testedScores=[]


	# find strings that fit into the variable spots
	#   in the pattern string

	# patternStr ex. "play the song {}", "remind me to {} later"
	#   "at {} play the song {}"

	bestMatches=[[],[]]
	score=0
	bestMatches, score = optimization(patternStr, inStr, trials=trials, subTrials=subTrials, earlyQuit=earlyQuit)


	#print "TOP MATCH: ", bestMatches

	subs = re.findall(r"\[([^]]+)\]", patternStr)
	subs = [item.split(',') for item in subs]
	subs = [[item.strip() for item in sub] for sub in subs]

	# get the words that go in the var spots
	varSet = []
	lengthSum = 0

	for match in bestMatches[0]:
		lengthSum += match[1] - match[0]
		varSet.append(inStr.split()[match[0]:match[1]])
		#varSet.append(origInStr.split()[match[0]:match[1]])

	varSet = [' '.join(var) for var in varSet]
	v2 = zip(varSet, orderList)
	v2.sort(key=lambda tup: tup[1])
	varSet = [item[0] for item in v2]
	#varSet.reverse()

	subsSet = [] # words that go into sub spots
	for i in range(len(bestMatches[1])):
		subsSet.append(subs[i][bestMatches[1][i]])

	
	cleanSet = []
	for item in varSet:
		if len(item.strip()) > 0:
			cleanSet.append(item.replace(' ,', ','))

	if lengthSum == len(inStr.split()) and len(cleanSet) == 1:
		score = 0

	cleanSet = [cleanSet, subsSet]

	#print "SCORE =", score

	return cleanSet, score, lengthSum
	

def matchFromList(matchList, inStr, trials=5, subTrials=100, minSubs=1, earlyQuit=False, includeLenScore=False):
	confidence = 0
	topMatches = [[],[]]
	smallestLengthSum = float('inf')

	for patternStr in matchList:
		tmpMatches, score, lengthSum = varMatches(patternStr, inStr, trials=trials, subTrials=subTrials, earlyQuit=False)
		if score > confidence:
			#print "MATCHES:", matches, "confidence:", score, "with: ", patternStr
			confidence = score
			topMatches = tmpMatches
		if score == confidence and lengthSum < smallestLengthSum:
			smallestLengthSum = lengthSum
			topMatches = tmpMatches

	if includeLenScore and smallestLengthSum != 0 and confidence >= 1.0:
		confidence = confidence + 1.0 / smallestLengthSum
	return topMatches, confidence

#patternStr = 'what do {} and {} have in common?'
#inStr = 'what do birds and bees have in common?'

p1 = '[the, a, some] {} went to {} [yesterday, today], to {}'
i1 = 'a cat went to the store yesterday, to die'
# expected output: [[cat], [the store]], [[a], [yesterday]]

p2 = '[the, a, some] {} or [a couple of, some] {} [flew, went] to {} [yesterday, today]'
i2 = 'some of my friends or some enemies flew to alberta yesterday'

p3 = 'from {1}, {0}'
i3 = "From Antarctica, researchers have excavated."

p4 = "{0}: {1}"
i4 = "The next step: sharper imaging."


#patternStr = "[ , what is the, whats the] [ ,current] [time, date, month, year, day]"
#inStr = "whats the time?"

#testOptimization(p2, i2)

#print varMatches(patternStr, inStr, trials=5, subTrials=100, minSubs=1, earlyQuit=False)

#matches = [[[1,2], [4,6]], [2, 1]]

#subs = [['the', 'a', 'some'], ['yesterday', 'today']]

#numVars= len(re.findall(r"\{\}", patternStr))
#numSubs = len(re.findall(r"\[", patternStr))
#numWords = len(inStr.split())