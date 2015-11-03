from patternMatching import *

def getCommands(inStr, trials=10, subTrials=100):

	patternStr = "{} [then, and then] {}"

	inStr = inStr.replace('then,', 'then')
	inStr = inStr.replace(', then', ' then')
	inStr = inStr.replace(', and', ' and')

	cleanSet, score, lengthSum = varMatches(patternStr, inStr, trials=trials, subTrials=subTrials, minSubs=1)

	# only multiple commands if score == 1.0

	# if we only have one command
	if score != 1.0:
		#print "SCORE:", score, "inStr: ", inStr
		return [inStr]

	# otherwise, see if we can split them up	

	
	if len(cleanSet[0]) == 0:
		print "ERROR"
		return []
	elif len(cleanSet[0]) == 1:
		return []
		print "ERROR"
	elif len(cleanSet[0]) == 2:
		pt1 = getCommands(cleanSet[0][0], trials=trials, subTrials=subTrials)
		pt2 = getCommands(cleanSet[0][1],trials=trials, subTrials=subTrials)
		return pt1+pt2
		#return [cleanSet[0][0]]+[cleanSet[0][1]]
	else: 
		print "ERROR"
		return []




inStr = "play the song happy and then tell me about dragons"

