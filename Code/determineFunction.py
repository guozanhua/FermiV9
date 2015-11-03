from common import *
from Fermi import *
from memory import *
from basicCmds import *
from learnForm import wrongCmd
from graphics import *

def executeCMDE(cmd, inStr, matches=[[],[]]):


	# execute appropriate code in terminal
	from searchEngines import urlify

	cmdStruct = findCMD(cmd)

	if setting('DEBUG'):
		print "EXECUTE CMDE:\n\t", matches

	#matches = refineMatches(cmdStruct, inStr)
	
	matches = substituteBiographicMemory(matches, queryType='what is')

	#if setting('DEBUG'):
	#print "\t", matches

	
	rStr = processResponse(getResponse(cmdStruct), matches[0])

	say(rStr, more=False, speak=setting("SPEAK"))

	for item in cmdStruct[3]:

		if "www" in item or "http" in item:
			for i in range(len(matches[0])):
				matches[0][i] = urlify('%s'%matches[0][i], space='+')

		# perform match substitutions
		item = processResponse(item, matches[0], syns=True)



		subprocess.call(item, shell=True)

	addToCmdHist(cmd, inStr)

	return [True, "new prompt", "cmde"]

def executeCMDS(cmd, inStr, matches=[[],[]], histPos=0):

	retVal=[]
	cmdWorked=False

	autoCmd=""

	cmdStruct = findCMD(cmd)
	if cmd == "lastCmd":
		
		cmdWorked = eval(cmd + "(cmdStruct, inStr, histPos=histPos)")
	else:
		#try:
		cmdWorked = eval(cmd + "(cmdStruct, inStr, matches=matches)")
		#except:
		#	print "ERROR", cmd
		#	pass

		if isinstance(cmdWorked, type([])):
			# check if cmdWorked is return from suggestCommand with a new command
			if cmd == "suggestCommand":
				autoCmd = cmdWorked[0]
				cmdWorked = cmdWorked[1] # get whether command was successful or not
			elif cmd == "ingest":
				cmd = cmd+' '+cmdWorked[0]
				cmdWorked = cmdWorked[1] # get whether command was successful or not
			elif cmd == "changeSettings":
				cmd = cmd+' '+cmdWorked[0]
				cmdWorked = cmdWorked[1] # get whether command was successful or not

	if histPos==0 and cmdWorked:
		addToCmdHist(cmd, inStr)

	if autoCmd != "":
		#print "performing autoCmd (prompted by user)"
		autonomousAction(autoCmd)

	if not cmdWorked:
		cmd = "fail"


	if cmd=="goodbye":
		return [cmdWorked, "exit", cmd]
	else:
		return [cmdWorked, "new prompt", cmd]

	

	#return ["new prompt", retVal[0], retVal[1]]

def refineMatches(cmd, inStr, trials = 10, subTrials=150):
	
	rotateCircle(index=6, angle=15)

	if setting('DEBUG'):

		print "REFINING WITH", trials, "TRIALS", "on", inStr

	topMatches, confidence = matchFromList(cmd[1], inStr, trials=trials, subTrials=subTrials, earlyQuit=False)
	return topMatches

def correctedStr(inStr):
	CORRECTIONS = GLOB['CORRECTIONS']

	# [if following pair is true], [cmd name], [user input], [intended input]

	maxMatch = 0
	retStr=""
	for item in CORRECTIONS:

		#matchScore = wordSim(k.cleanWord(item[2]), k.cleanWord(inStr), useInScore=True)
		matchScore = wordSim(k.cleanWord(item[2]), k.cleanWord(inStr), basic=True)

		if matchScore >= maxMatch and item[3] != '':
			maxMatch = matchScore
			#print "REPLACED!"
			#print inStr, item[2], maxMatch
			retStr=item[3]
	
	if maxMatch >= 0.95:
		return retStr
	else:
		return inStr

def evalConfidence(meantStr):
	if meantStr[0:5] == "eval(":
		return 1.0
	else:
		return 0.0

def cmdConfidence(meantStr, cmdType, useInScore=True):

	CMDList = []
	for cmd in GLOB[cmdType]:
		if cmd[1] != ['']:
			CMDList.append(cmd)

	#CMDList = GLOB[cmdType]



	strippedStr = k.cleanWord(meantStr) # removes most non-alphanumeric

	confidence = 0
	topCmd = []
	topMatches = [[],[]]

	smallestLengthSum = float('inf')

	matchNum = 0

	for cmd in CMDList:

		CS = correctionScore(cmd, meantStr)
		if CS != 0.0:

			for patternStr in cmd[1]:
				#print "patternStr = ", patternStr
				#print "meantStr = ", meantStr
				#matchNum += 1
				#print "MATCHING...", matchNum
				matches, score, lengthSum = varMatches(patternStr, strippedStr, trials=5, subTrials=100, earlyQuit=True)
				#print "score=", score
				if score > confidence:
					if setting('DEBUG'):
						print "MATCHES:", matches, "confidence:", score, "with: ", patternStr, "cmd:", cmd[0]
					confidence = score
					topMatches = matches
					topCmd = cmd[0]

				if score == confidence and lengthSum < smallestLengthSum:
					if setting('DEBUG'):
						print "MATCHES:", matches, "confidence:", score, "with: ", patternStr, "cmd:", cmd[0]
					smallestLengthSum = lengthSum
					topMatches = matches
					topCmd = cmd[0]




	return confidence, topCmd, topMatches

def chatConfidence(inStr):
	topResponse, maxMatch = getChatResponse(inStr)

	CS = correctionScore(["chat"], inStr)
	if CS == 1.0:
		maxMatch = 1.0
	if CS == 0.0:
		maxMatch = 0.0

	return maxMatch, topResponse

def engineConfidence(inStr):

	# list of engine functions
	engines=[["getEviAnswer", "evi"],
			["getBingAnswer", "bing"],
			["getWolframAnswer", "wolfram"]]#,
			#["getWikiHowAnswer", "wikihow"]]
	isEqn = "+" in inStr or "-" in inStr or "*" in inStr or "/" in inStr or "=" in inStr
	if isEqn: engines[0], engines[2] = engines[2], engines[0]

	isHowTo = "how to" in inStr or "how do" in inStr
	#if isHowTo: engines[0], engines[3] = engines[3], engines[0]
	if isHowTo: engines.append(["getWikiHowAnswer", "wikihow"])

	gotResult=False
	engineTry=0
	answer=""
	while not gotResult and engineTry < len(engines):
		if correctionScore([engines[engineTry][1]], inStr) != 0.0:
			#print "trying ", engines[engineTry][1]

			try:
				answer = eval(engines[engineTry][0]+"("+"inStr"+")")
				#print "answer: ", answer
			except TimedOutExc:
				#say("(Timeout on "+engines[engineTry][1]+")", more=False, speak=False)
				pass
			except:
				pass
				#return none
			
			answer = answer.lstrip()
			answer = answer.rstrip()
			if answer != "":
				#print [engines[engineTry][1]],"  ", inStr, "  ", correctionScore([engines[engineTry][1]], inStr)
				if len(answer) >= 800:
					#retStr = html
					topStrs = k.importantSentences(k.loadString(answer), SEN_NUM=3, CHRON=True)
					topStrs = [item[0] for item in topStrs]
					answer = ' '.join(topStrs)
				


				#say(answer, more=False, speak=setting("SPEAK"))
				#retVal, function="new prompt", "engine" #engines[engineTry][1]
				gotResult=True

			#else:
				#engineTry += 1
		engineTry += 1

	if gotResult:
		return 1.0, answer
	else:
		return 0.0, ""


def correctionScore(cmd, inStr):
	CORRECTIONS = GLOB['CORRECTIONS']

	maxMatch = 0
	retVal = 0.5

	
	for item in CORRECTIONS:
		itemTF = 1.0 if item[0]==True else 0.0

		# how similar inStr is to thing said in past
		simScore = wordSim(k.cleanWord(item[2]), k.cleanWord(inStr), useInScore=True)

		# what to do if we exactly find a phrase match
		# -> return 0 unless cmd == item[1]
		if simScore == 1.0:
			if itemTF == 1.0 and cmd[0] != item[1]:
				return 0.0 # because we arent at the suggested engine yet

			if cmd[0] == item[1]:
				return itemTF

			#if itemTF == 0.0 and cmd[0] != item[1]:


			

		# otherwise, find the best matching phrase
		if simScore >= maxMatch and item[1] == cmd[0]:
			maxMatch = simScore

			retVal = itemTF

	if maxMatch >= 0.9:
		return retVal
	else:
		return 0.5

def autonomousAction(inStr):
	# inStr = string used to send to determinAction

	retVal, cmd = determineFunction(inStr, fromAuto=True)


def addToCmdHist(cmd, inStr):
	# cmd: name of cmd executed
	# inStr: what user said to initiate command

	if cmd.split()[0] == "eval":
		moodAfter=GLOB['MOOD']
		timeStr=datetime.datetime.now().strftime("%r, %A %d. %B %Y")
		GLOB['CMDHIST'].append([timeStr, inStr, cmd, moodAfter])
		return

	if cmd == "fail":
		return

	# update mood with task mood details

	cmdMoodVals=[]
	cmdMoodWeight=[]

	CMD, cmdType = findCMD(cmd, getType=True)

	if cmdType == "CMDS":
		cmdMoodVals = CMD[4]
		cmdMoodWeight = CMD[5]
	elif cmdType == "CMDE":
		cmdMoodVals = CMD[5]
		cmdMoodWeight = CMD[6]

	if cmdType != "none":
		ingest(CMD, inStr="", mood=cmdMoodVals, weight=cmdMoodWeight, isCmd=True)

	# save mood after command
	moodAfter=GLOB['MOOD']

	timeStr=datetime.datetime.now().strftime("%r, %A %d. %B %Y")
	GLOB['CMDHIST'].append([timeStr, inStr, cmd, moodAfter])





	# PERFORM FEATURE FINDING
	'''
	fStart = max(len(GLOB['CMDHIST'])-50, 0)
	pairTests = [[0,i] for i in range(1,13)]
	pairTests += [[1,i] for i in range(2,13)]
	FEATURES = findFeatures(loadHist(HIST=copy.deepcopy(GLOB['CMDHIST'][fStart:])), pairTests=pairTests)
	FEATURES += findFeatures(copy.deepcopy(FEATURES))[1:]
	newFeatures=[]
	for f in FEATURES[1:]:
		if f not in GLOB['FEATURES']:
			# f = ('3th most frequent', 'arousal', '0.8')
			newFeatures.append(f[0]+' '+f[1]+' '+f[2])#+' '+'%s'%f[3])
			GLOB['FEATURES'].append(f)
	if newFeatures != []:
		say('*'+', '.join(newFeatures)+'*', more=False, speak=setting("SPEAK"), moodUpdate=True)
	'''

	return

def findCMD(inStr, getType=False):
	CMDS = GLOB['CMDS']
	CMDE = GLOB['CMDE']

	inStr = inStr.split()[0]

	# given name of function, find the data associated with it
	for cmd in CMDS:
		# need to do a split and get first word b/c ingest cmd has
		#   substance name appended to string
		cmdName = cmd[0].split()[0]
		if inStr == cmdName:
			if getType:
				return cmd, "CMDS"
			else:
				return cmd

	for cmd in CMDE:
		# need to do a split and get first word b/c ingest cmd has
		#   substance name appended to string
		cmdName = cmd[0].split()[0]
		if inStr == cmdName:
			if getType:
				return cmd, "CMDE"
			else:
				return cmd

	return ["", [], ["Error: command not found."]], "none"


def determineFunction(meantStr, histPos=0, fromAuto=False):
	origMeantStr = meantStr

	# if the user just presses enter, give new prompt line
	if len(meantStr.strip()) == 0 and not GLOB['onQuery']:
		sys.stdout.write('>> ')
		GLOB['onQuery']=True
		return "no prompt", "none" # [what to do, function name]

	rotateCircle(index=6, angle=15)
	
	# first check if the user is trying to execute raw code
	if evalConfidence(meantStr) == 1.0:
		#try:
		output=eval(meantStr[6:len(meantStr)-2])
		#except:
		
		#	say("Eval failed.", more=False, speak=setting("SPEAK"), moodUpdate=True)
		#	pass
		#	return "new prompt", "fail"
		
		if output != None and output not in ["no prompt", "new prompt"]:
			#print output
			tkHistCat(output+'\n')

		# when storing cmd in history, get name by stripping non alpha-numeric
		evalType = re.sub(r'\W+', '', meantStr)
		addToCmdHist("eval "+evalType, meantStr)

		if output == "no prompt":
			return "no prompt", "eval" # [what to do, function name]
		else: return "new prompt", "eval" # [what to do, function name]


	confidence=0
	cmdType = ""
	topCmd = ""
	topMatches = [[],[]]

	cmdsConfidence, cmdsFunction, cmdsMatches = cmdConfidence(meantStr, 'CMDS')
	cmdeConfidence, cmdeFunction, cmdeMatches = cmdConfidence(meantStr, 'CMDE', useInScore=False)

	if cmdsConfidence >= cmdeConfidence:
		cmdType = 'CMDS'
		topCmd = cmdsFunction
		topMatches = cmdsMatches
		confidence = cmdsConfidence
	else:
		cmdType = 'CMDE'
		topCmd = cmdeFunction
		topMatches = cmdeMatches
		confidence = cmdeConfidence

	if setting('DEBUG'):
		print "CONFIDENCE = ", confidence

	cmdConfident=(confidence >= 0.975)

	#print topMatches

	worked=False
	returnPair=["new prompt", "none"]


	# first try CMDS or CMDE
	if cmdConfident: # try

		GLOB['contextLocked'] = False

		topMatches = refineMatches(findCMD(topCmd), meantStr, trials = 15, subTrials=300)

		#print "TOP CMD:", topCmd
		if cmdType == "CMDS":
			retVal = executeCMDS(topCmd, meantStr, matches=topMatches, histPos=histPos)
			if retVal[0]: # whether the command was successful or not
				worked=True
				returnPair = [retVal[1], retVal[2]]
		else:
			retVal = executeCMDE(topCmd, meantStr, matches=topMatches)
			if retVal[0]: # whether the command was successful or not
				worked=True
				returnPair = [retVal[1], retVal[2]]



	if worked:
		rotateCircle(index=6, angle=15)

		if setting('DEBUG'):
			print "CMD WORKED"
			print "\ttopMatches", topMatches
			print "\tmeantStr", meantStr
		

		updateContext(topMatches, meantStr, cmdConfidence=(1 if worked else 0))
		#print "CONTEXT:", GLOB['CONTEXT']
		# free the context to be updated
		
		return returnPair



	if setting('CONTEXT'):
		rotateCircle(index=6, angle=15)

		meantStr = substituteContext(meantStr, maxLength=5, reSub=False)
		#meantStr=substituteBiographicMemory(subStr=meantStr)
		#print "DF MEANTSTR:", meantStr


	if setting('DEBUG'):
		print "DF MEANTSTR = ", meantStr
		print "\nTESTING CHAT"


	# now search chat
	if setting('USE_CHAT'):
		rotateCircle(index=6, angle=15)

		confidence, chatStr = chatConfidence(meantStr)
		chatConfident = (confidence >= 0.9)
		if chatConfident:
			#print "CHAT"
			say(chatStr, more=(histPos==0), speak=setting("SPEAK"))
			addToCmdHist("chat", origMeantStr)
			return "no prompt", "chat"




	# now try the engines
	if setting('USE_ENGINES'):
		rotateCircle(index=6, angle=15)

		if setting('DEBUG'):
			print "MEANTSTR = ", meantStr
			print "\nTESTING ENGINES"

		confidence, engineStr = engineConfidence(meantStr)
		engineConfident = (confidence == 1.0)
		if engineConfident:
			say(engineStr, more=(histPos==0), speak=setting("SPEAK"))
			addToCmdHist("engine", origMeantStr)

			GLOB['contextLocked'] = False
			updateContext(inStr=meantStr)

			return "no prompt", "engine"


	# see if aasr has something to say about it
	#qStr, newContext = aasr.handleInput(expandContractions(meantStr), getContext=True)

	qStr, newContext, qType = aasr.handleInput(expandContractions(meantStr),
						factList=GLOB['FACTUAL_MEMORY'],
						factFileName = DATA_DIR+'factual_memory.txt',
						getContext=True, queries=True, save=True)

	rotateCircle(index=6, angle=15)

	#print "qStr = ", qStr
	if qStr != "":

		if newContext != "":
			GLOB['CONTEXT'] = newContext
			#updateContext(inStr=newContext)

		qStr = swapPronouns(qStr) #.capitalize()

		if qType == "query":
			say(qStr, more=False, moodUpdate=False, describeFace=False, speak=False)
		elif qType == "add":
			say("I'll remember that.", more=False, moodUpdate=False, describeFace=False, speak=False)
	
		addToCmdHist("aasr", origMeantStr)
		return "new prompt", "aasr"

	rotateCircle(index=6, angle=15)

	#if no answer, don't say anything
	if not fromAuto:
		#addToCmdHist("none", inStr)
		addToCmdHist("none", origMeantStr)
		rStr = replaceEnd(swapPronouns(expandContractions(origMeantStr)), '?')

		say(rStr, more=(histPos==0)) # just print a space so it actually shows his mood
		
		GLOB['contextLocked'] = False
		updateContext(inStr=meantStr)
	
	
	return "no prompt", "none"


