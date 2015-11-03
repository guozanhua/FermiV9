from common import *


def IV(state=[], fixed=False):
	# IMMEDIACY VECTOR
	# gives how important increasing each M12 value is

	# fixed: the state is aingle unit to perform the
	#    hierarchy weight calculation on
	# --> if not fixed, then split it up and calculate
	if not fixed:
		if state == []:
			state = GLOB['MOOD']
			return IV(state[:3], fixed=True)+IV(state[3:], fixed=True)
		else:
			return IV(state[:3], fixed=True)+IV(state[3:], fixed=True)


	# main idea:
	#   - you do not start working on the next level
	#     of the hierarchy until you fulfill the previous ones

	IVec = [0]*len(state)

	#IVec[0] = 0.5*(1.0-state[0])

	# individual weights
	R = [0.5*(1.0-v) for v in state]

	for i in range(0, len(state)):
		#IVec[i] = 0.5*(1.0-state[i])*0.5 * (1.0 + state[i-1])

		IVec[i] = math.pow(R[i], 1.5)*(1.0 - sum(IVec))
	

	#print "SUM:", sum(IVec)
	return IVec

def stateScore(state, IM):
	# IM = immediacy vector

	# if something is badly needed by IM
	# and state has it, then SPtIM will indicate a match
	SPtIM = [state[i]*IM[i] for i in range(GLOB['MOODDIM'])]


	weightSum = 1 # sum of all 12 weights
	return sum(SPtIM)/weightSum

def satisfactionScore(stateBefore, stateAfter, current=False):
	# Hbefore = CMDHIST[occIndex-1+t][3][0]
	# Hafter = CMDHIST[occIndex+t][3][0]
	# Hdiff = Hafter - Hbefore
	# ---> this doesn't work because what we care about maximizing can change over time



	# check how well moving from stateBefore to stateAfter
	#  satisfies a given immediacy vector
	IM=[]
	if not current:
		IM = IV(state=stateBefore) # specify alternative state
	else:
		IM = IV(state=[])# current immediacy vector


	scoreBefore = stateScore(stateBefore, IM)
	scoreAfter = stateScore(stateAfter, IM)

	return scoreAfter - scoreBefore

def longTermSatisfactionMaximization(cmdList, nameList):
	CMDHIST = GLOB['CMDHIST']

	'''
	Algorithm:
		- for each cmd:
			- look at things happening after that
			  command is executed
	'''

	# how far into the future to look to determine happiness after an action
	lookAhead = setting("LTS_LOOKAHEAD") #5

	# ADDICTION SUSCEPTIBILITY FACTOR
	# ADF : large -> high susceptibility (> 1)
	# 	- more weight on happiness delta immediately after action
	# ADF : small -> low susceptibility (< 1)
	#	- more weight on happiness delta longer after action
	ADF = setting("LTS_ADDICTION_SUSCEPTIBILITY") #1.5

	# MEMORY SALIENCE FACTOR
	# MSF : large -> high weight on most recent memories (> 1)
	# MAS : 1 -> equal weight on all memories
	# MSF : small -> higher weight on older memories (< 1)
	MSF = setting("LTS_MEMORY_SALIENCE") #1.5

	# store scores for each command
	cmdSList = []
	

	# store top thing said by user for the top command
	topUserCmd = ""

	for cmd in cmdList:

		# store score for each occurrence of the command
		occSList = []

		# store top thing said to initiate this command type
		tmpTopUserCmd=""

		# for each occurrence of the command
		for occ in cmd:
			
			# get array of deltaH's following occ
			occIndex = CMDHIST.index(occ)
			# tmpDHList = []
			occSHistList=[]

			for t in range(0, min(lookAhead, len(CMDHIST[occIndex:]))):
				stateBefore = CMDHIST[occIndex-1+t][3]
				stateAfter = CMDHIST[occIndex+t][3]
				Sscore = satisfactionScore(stateBefore, stateAfter, current=(t==0))

				occSHistList.append(Sscore)


			# now calculate weighted average of happiness jumps
			pos = 0
			sSum = 0
			sWeightSum = 0
			
			for s in occSHistList:
				weight = pow(ADF, -1.0*pos) # each memory is more salient than previous one
				sWeightSum += weight
				sSum += s * weight
				pos += 1

			expectedS = sSum/sWeightSum
			occSList.append(expectedS)

			# check if this was so far the best thing said to start cmd
			if expectedS >= max(occSList):
				tmpTopUserCmd = CMDHIST[occIndex][1]

		# now calculate weighted average of expected DH's for the command
		occSList.reverse() # reverse list so recent ones are first
		pos = 0
		sSum = 0
		sWeightSum = 0
		
		for s in occSList:
			weight = pow(MSF, -1.0*pos) # each memory is more salient than previous one
			sWeightSum += weight
			sSum += s * weight
			pos += 1

		expectedS = sSum/sWeightSum
		cmdSList.append(expectedS) # add result to list of expected DH's for each cmd

		# check if this was so far the best thing said to start any cmd
		if expectedS >= max(cmdSList):
			topUserCmd = tmpTopUserCmd

		cmdName = nameList[cmdList.index(cmd)]
		#print cmdName, "->", expectedS, " with ", tmpTopUserCmd

	# find command with highest DH value
	if cmdSList == []:
		return "", 0, ""
	topS = max(cmdSList)
	topCmd = nameList[cmdSList.index(topS)] #top command type

	# motivation score = max weight of unfulfilled need
	mot = IV(state=[], fixed=False)

	#return topCmd, topS, topUserCmd
	return topCmd, max(mot), topUserCmd

