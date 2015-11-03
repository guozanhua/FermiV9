# File: Fermi.py
# Emotive personal assistant program


from common import *
from searchEngines import *
from emotions import *
from reminders import *
from satisfactionMaximization import *
from determineFunction import *
from fileIO import *

from graphics import *
#from featureFinding import *


def stateSummary(mood=[], short=False):

	if mood == []:
		mood = copy.deepcopy(GLOB['MOOD'])

	IMVEC = IV(mood)

	mood = fullMoodVec(mood)

	COMBO = zip(mood, IMVEC)

	#print "                            MOOD | IMMEDIACY VEC"
	tkSideCatStr=""
	tkHistCatStr=""
	if short:
		tkSideCatStr="                   MOOD\n"
	else:
		tkHistCatStr="                            MOOD | IMMEDIACY VEC\n"

	# make visual interpretation of levels
	barList = []
	for item in COMBO:
		Mlvl = item[0][1] # range from -1 to 1
		Wlvl = item[1] # ranges from 0 to 1

		barSize = 11
		
		# CALCULATE MOOD BAR
		Mstr = [' ' for i in range(barSize)]
		mid = int(math.floor(0.5*barSize))
		pos = int(math.floor(0.5*(Mlvl + 1.0)*barSize))
		Mstr[pos] = '|'

		if Mlvl > 0:
			for i in range(mid,pos):
				Mstr[i]='|'
		if Mlvl < 0:
			for i in range(pos+1, mid):
				Mstr[i]='|'
		
		Mstr[mid] = '|'

		Mstr = ''.join(Mstr)
		Mstr = '['+Mstr+']'

		# CALCULATE WEIGHT BAR
		Wstr = [' ' for i in range(barSize)]
		pos =int(math.floor(Wlvl*barSize))
		Wstr[pos] = '|'
		
		for i in range(0,pos):
			Wstr[i]='|'
		
		Wstr = ''.join(Wstr)
		Wstr = '['+Wstr+']'

		barList.append([item[0][0], Mstr, Wstr])

	for bar in barList:
		#print "%15s\t   "%bar[0], "%s"%bar[1], "%s"%bar[2]
		if short:
			#barStr= "%.6s\t"%bar[0]+" %s"%bar[1]+" %s"%bar[2]+'\n'
			#barStr= "%.13s\t"%(bar[0]+"      ")+" %s"%bar[2]+'\n'
			barStr= "%.13s\t"%(bar[0]+"      ")+" %s"%bar[1]+'\n'
			tkSideCatStr+=barStr
		else:
			barStr= "%15s\t   "%bar[0]+" %s"%bar[1]+" %s"%bar[2]+'\n'
			tkHistCatStr += barStr
			#tkHistCat(barStr)
		
	if short:
		tkSideCatStr+='\n'
	else:
		tkHistCatStr+='\n'

	# print current suggestions
	cmdList, nameList = generateCmdList()
	topCmd, topDelta, topUserCmd = longTermSatisfactionMaximization(cmdList, nameList)

	'''
	print
	print "SUGGESTION"
	print "   TOP CMD:", topCmd
	print " TOP DELTA:", topDelta
	print "TOP PROMPT:", topUserCmd
	'''
	tkSideCatStr+=" TOP CMD: "+topCmd+'\n'
	tkSideCatStr+=" TOP IMM: "+'%s'%round(topDelta, 3)+'\n'

	if short:
		tkSideClear()
		tkSideCat(tkSideCatStr)
	else:
		tkHistCat(tkHistCatStr)

	return

def updateSettings(varName, value, newSetting=False):

	rStr=""

	if newSetting:
		auxVerb = 'is'
		lemVarName = varName.lower().replace('_', ' ')
		if k.lemmatizer(lemVarName) != lemVarName:
			# assuming it is pluralized
			auxVerb = 'are'

		rStr = "I'll remember that "+swapPronouns(varName)+' '+auxVerb+' '+swapPronouns(value)+"."
		varName = varName.upper().replace(' ','_')
		GLOB['SETTINGS'].append((varName, value))
		
		#rStr = "Adding setting "+varName+" and setting to "+'%s'%value+"."
	else:

		# search settings for setStr and modify value
		prevVal = ""
		worked = False
		for i in range(len(GLOB['SETTINGS'])):
			if GLOB['SETTINGS'][i][0]==varName:
				worked = True
				prevVal = GLOB['SETTINGS'][i][1]
				GLOB['SETTINGS'][i] = (varName, value)

		#rStr = "Changing "+varName+" setting from "+'%s'%prevVal+" to "+'%s'%value+"."
		auxVerb = 'is'

		lemVarName = varName.lower().replace('_', ' ')
		if k.lemmatizer(lemVarName) != lemVarName:
			# assuming it is pluralized
			auxVerb = 'are'

		rStr = "I'll remember that "+swapPronouns(varName)+' '+auxVerb+' '+'%s'%swapPronouns(value)+" instead of "+swapPronouns(prevVal)+"."





	f = open(SETS_DIR+'settings.txt', 'w')
	for item in GLOB['SETTINGS']:
		isLast = GLOB['SETTINGS'].index(item) == len(GLOB['SETTINGS'])-1

		f.write("\"%s\", " % (item[0]))
		if isinstance(item[1], type("")) or isinstance(item[1], unicode):
			#print "STRING", item[1]
			f.write("\"%s\"\n" % (item[1]))
		else:
			#print "NOT STRING", item[1], type(item[1])
			f.write("%s\n" % ('%s'%item[1]))

		if not isLast:
			f.write("\n")

	f.close()

	say(rStr, more=False, speak=setting("SPEAK"))

	resizeLayout()
	updateColour()
	return

# IN CMDS
def changeSettings(inCmd, inStr, matches=[[],[]]):
	from determineFunction import refineMatches, findCMD


	if len(matches[0]) != 2:
		return ["", False]

	topSetting = ""
	topSettingType = type(True)
	topScore = 0
	for i in range(len(GLOB['SETTINGS'])):
		
		score = wordSim(GLOB['SETTINGS'][i][0].replace('_',' '), matches[0][0], basic=True)
		
		if score > topScore:
			topScore = score
			topSetting = GLOB['SETTINGS'][i][0]
			topSettingType = type(GLOB['SETTINGS'][i][1])


	
	if setting('DEBUG'):
		print "CHANGE SETTINGS\n\ttopSetting:", topSetting, "score:", topScore
		print "\tqueryStr:", matches[0][0]

	if topScore < 0.9:
		return ["", False]


	newSetting = matches[0][1]
	if isinstance(True, topSettingType):

		# its a boolean setting
		if wordSim(matches[0][1], "True", basic=True) >= wordSim(matches[0][1], "False", basic=True):
			newSetting = True
		else:
			newSetting = False

	elif isinstance(1.0, topSettingType) or isinstance(1, topSettingType):
	
		# its a number
		valMatches = re.findall("[-+]?\d+[\.]?\d*", inStr)
		if len(valMatches) != 1:
			say(getResponse(findCMD("rephrase")), more=False, speak=setting("SPEAK"), moodUpdate=True)
			return ["", False]
		else:
			newSetting = float(valMatches[0])
	#else:
		# must be a string?



	#print "changing:", topSetting
	#print "to:", newSetting

	try:
		updateSettings(topSetting, newSetting)
	except:
		say(getResponse(findCMD("rephrase")), more=False, speak=setting("SPEAK"), moodUpdate=True)
		pass
		return ["", False]

	return [topSetting+'-'+'_'.join(('%s'%newSetting).split()), True]

# IN CMDS
def querySettings(inCmd, inStr, matches=[[],[]], rawData=False):
	from determineFunction import refineMatches
	
	if matches == [[],[]]:
		matches = refineMatches(inCmd, inStr)

	if len(matches[0]) != 1 or len(matches[1]) < 1:
		return False

	queryStr = matches[0][0].replace(' ', '_').replace('?', '')

	topSetting = ""
	topValue = ""
	topSettingType = type(True)
	topScore = 0
	for i in range(len(GLOB['SETTINGS'])):
		
		score = wordSim(GLOB['SETTINGS'][i][0], queryStr, basic=True)
		
		if score > topScore:
			topScore = score
			topSetting = GLOB['SETTINGS'][i][0]
			#topSettingType = type(GLOB['SETTINGS'][i][1])
			topValue = GLOB['SETTINGS'][i][1]

	if setting('DEBUG'):
		print "\tscore = ", topScore, "guess = ", topValue
		print "\tqueryStr = ", queryStr
		print "\ttopSetting = ", topSetting

	if topScore >= 0.9:
		#say("I believe it is "+'%s'%topValue+'.', more=False, speak=setting("SPEAK"), moodUpdate=True)
		topSetting = swapPronouns(topSetting)

		topValue = '%s'%topValue
		topValue = swapPronouns(topValue)

		if rawData:
			return topValue

		auxVerb = 'is'
		lemVarName = topSetting.lower().replace('_', ' ')
		if k.lemmatizer(lemVarName) != lemVarName:
			# assuming it is pluralized
			auxVerb = 'are'

		replacements = [topSetting.capitalize(), auxVerb, topValue]
		rStr = processResponse(getResponse(inCmd), replacements)
		

		say(rStr, more=False, speak=setting("SPEAK"))
	else:
		if rawData:
			return ""
		return False


	if rawData:
		return ""

	return True

def generateCmdList():
	CMDHIST = GLOB['CMDHIST']

	# history entry:
	# [time, "user string", "cmd name", moodAfter (VAD)]

	# we want to find what causes the largest increase in mood
	# note: not* what we did when we were happiest

	# first, create list of occurences of each command
	cmdList=[]
	nameList=[] # list of command names currently in cmdList
	for cmd in CMDHIST:
		ignore = cmd[2] in ["start", "none", "wrongCmd", "update", "lastCmd"]
		if cmd[2] not in nameList and not ignore:
			nameList.append(cmd[2])
			cmdList.append([])	
		
		if not ignore:
			cmdList[nameList.index(cmd[2])].append(cmd)

	return cmdList, nameList

# IN CMDS
def suggestCommand(inCmd=[], inStr="", perform=False, fromAuto=False, matches=[[],[]]):
	CMDHIST = GLOB['CMDHIST']

	if not perform:
		perform = wordSim(inStr, "do what you want") >= 0.85

	cmdList, nameList = generateCmdList()

	if len(cmdList) == 0:
		if not fromAuto:
			say("I'm not sure what to do.", more=False, moodUpdate=True, speak=setting("SPEAK"))
		return True

	topCmd, topDelta, topUserCmd = longTermSatisfactionMaximization(cmdList, nameList)
	
	# only do something autonomously if the need has enough weight
	#   and you are not too lazy

	if not perform:
		
		rStr=processResponse(getResponse(inCmd), [topCmd])

		#print "top cmd: ", topUserCmd 
		rStr += ' ('+'%s'%k.sf(topDelta,2)+')'
		say(rStr, more=False, moodUpdate=True, speak=setting("SPEAK"))

	else:
		# say same thing as user when he issued command
		#print "top cmd: ", topUserCmd
		# only do thing if outcome is expected to be positive
		offLimits = ["suggestCommand", "none", "wrongCmd", "goodbye", "reminders"] # not allowed to do these
		if topDelta >= setting('LAZINESS') and topCmd not in offLimits:
			#print "performing: ", topUserCmd
			toSay='*'+topUserCmd+'*'
			say(toSay, more=False, moodUpdate=True, fromAuto=False, describeFace=True, speak=False, location="top")

			
			if fromAuto:

				# AI manually calls determineFunction
				retVal, cmd = determineFunction(topUserCmd)
				if retVal == "new prompt":
					newInput(findCMD("newInput"))
			else:
				# suggestion was called by determineFunction
				return [topUserCmd, True]

		else:
			if not fromAuto:
				retStr = "I'm okay."
				say(retStr, more=False, moodUpdate=True, speak=setting("SPEAK"))

	return True

def periodicAnimations():
	
	rotateCircle(index=3, angle=30)

	isAsleep = "asleep" == GLOB['curFace']

	elapsed_time = time.time() - GLOB['prevUsageTime']

	if elapsed_time >= 5 and elapsed_time < 30 and not isAsleep:
		blinkingAnimation(mood=GLOB['MOOD'])

	elif elapsed_time >= 30 and not isAsleep:
		if random() <= 0.5:
			blinkingAnimation(mood=GLOB['MOOD'])
		else:
			lookAnimation(holdLook=random()*3.0, moveDt=random()*0.1)

	t = threading.Timer(randint(6, 20), periodicAnimations)
	t.daemon = True
	t.start()

def recurring():
	#try:

	rotateCircle(index=3, angle=30)

	checkReminders()

	MOOD = GLOB['MOOD']
	PREVMOOD = GLOB['PREVMOOD']

	cycleTime = 50 #seconds -- note: briefly uses ~25% of cpu

	faceBefore=getFace(MOOD)
	
	elapsed_time = time.time() - GLOB['prevUsageTime']
	chatStr=internalMonologue()

	faceAfter=getFace(MOOD)



	#if elapsed_time > 120 and not setting('QUIET'):
	if not setting('QUIET'):
		toSay=" "
		if GLOB['remindersSent'] == 0:
			toSay+='*'+chatStr+'*'
			GLOB['remindersSent'] += 1
		if faceBefore != faceAfter or toSay != ' ':
			playSound("recurring")
			say(toSay, more=True, moodUpdate=False, fromAuto=True, describeFace=True, speak=False, location="top")
			blinkingAnimation(mood=MOOD)

	# choose command ~ every 10 minutes
	#print "max IV = ", max(IV())
	if setting("AUTONOMOUS") and elapsed_time > 60 and not setting('QUIET') and max(IV()) >= random():
		suggestCommand(perform=True, fromAuto=True)

	# update chat data ~ every 10 minutes
	if randint(0,(40*cycleTime)-1) <= cycleTime:
		#print "updating chat at "+datetime.datetime.now().strftime("%r, %A %d. %B %Y")
		update([], "", speak=False, partialChat=True, onlyChat=True)

	
	t = threading.Timer(cycleTime, recurring)
	t.daemon = True
	t.start()
	#except:
	#	print "ERROR: RECUR FAILED"
	#	pass

# IN CMDS
def intro():
	cmd=findCMD("intro")
	replacements=[]
	hour=datetime.datetime.now().hour

	# good morning
	if hour >= 5 and hour <= 11: 		replacements.append("Good morning")
	elif hour > 11 and hour <= 1+12:	replacements.append("Hello")
	elif hour > 1+12 and hour <= 4+12:	replacements.append("Good afternoon")
	elif hour > 4+12 and hour <= 24:	replacements.append("Good evening")
	else:								replacements.append("Good to see you")

	timeStr=datetime.datetime.now().strftime("%r, %A %d")
	replacements.append(timeStr)
	rStr=processResponse(getResponse(cmd), replacements)


	introAnimation()
	initCC()

	say(rStr, more=True, speak=setting("SPEAK"), moodUpdate=False)

def init():

	graphicsInit()

	playSound("intro")

	# perform initial load of data
	update([], "", speak=False, partialChat=True)

	GLOB['MOOD']=partMoodVec(setting("DEFAULT_MOOD"))
	GLOB['MOOD']=updateMood(GLOB['MOOD'], weight=[0]*GLOB['MOODDIM'], instant=False)
	GLOB['PREVMOOD']=copy.deepcopy(GLOB['MOOD']) # nothing before first mood, so just copy first mood

	# note: don't want to load cmdhist in update(), otherwise we
	#   could lose recent history on update
	# have to be careful so this file doesn't store duplications
	GLOB['CMDHIST'] = yamlLoad(DATA_DIR+"history.txt", maxLen=200)
	if GLOB['CMDHIST'] == {}:
		GLOB['CMDHIST'] = []

	GLOB['INGESTED'] = yamlLoad(DATA_DIR+"ingested.txt", maxLen=200)
	if GLOB['INGESTED'] == {}:
		GLOB['INGESTED'] = []

	resizeLayout()

	# LOAD PAST SET OF FEATURES
	#fStart = max(len(GLOB['CMDHIST'])-50, 0)
	#pairTests = [[0,i] for i in range(1,13)]
	#pairTests += [[1,i] for i in range(2,13)]
	#GLOB['FEATURES'] = findFeatures(loadHist(HIST=copy.deepcopy(GLOB['CMDHIST'][fStart:])), pairTests=pairTests)
	#GLOB['FEATURES'] += findFeatures(copy.deepcopy(GLOB['FEATURES']))[1:] # get 2nd order awareness

	# converge mood

	for i in range(10):
		GLOB['MOOD']=updateMood(mood=[0]*GLOB['MOODDIM'], weight=[0]*GLOB['MOODDIM'], instant=False)


	# save initial mood in cmdHist for future calculation
	timeStr=datetime.datetime.now().strftime("%r, %A %d. %B %Y")

	GLOB['CMDHIST'].append([timeStr, "", "start", GLOB['MOOD']])

	intro()


	updateColour()
	recurring()
	periodicAnimations()
	ccRotateAnimation()

def extractCommands(inStr):
	# extract recursive commands
	
	while inStr != correctedStr(inStr):
		if setting('DEBUG'):
			print "CORRECTING STR:", inStr, "->", correctedStr(inStr)
		inStr = correctedStr(inStr)

	if not setting('MULTITASK'):
		return [inStr]

	# get list of tasks in inStr
	tasks = getCommands(inStr)

	if len(tasks) == 1:
		return tasks

	cmdsCon, cmdsCmd, cmdsMatches = cmdConfidence(inStr, 'CMDS')
	if cmdsCon >= 0.95 and cmdsCmd == "wrongCmd":
		if setting('DEBUG'):
			print "SKIPPING MULTITASK:", inStr
		return [inStr]

	# get what we mean by those potential tasks
	newTasks=[]
	for i in range(len(tasks)):
		newTasks = newTasks+extractCommands(tasks[i])
		
	if setting('DEBUG'):
		print "EXTRACTED COMMANDS:", newTasks

	return newTasks

def newInstr(input_var):

	newMood=getMood(input_var) # update mood based on user input

	GLOB['PREVMOOD']=copy.deepcopy(GLOB['MOOD'])
	inputWeight = 1.0 - GLOB['MOOD'][2] # more confident -> less impact by other people
	GLOB['MOOD']=updateMood(newMood, weight=[inputWeight]*3+[0]*(GLOB['MOODDIM']-3))

	retVal, cmd = "", ""
	for task in extractCommands(input_var):
		retVal, cmd =determineFunction(task)

		if len(task.strip()) == 0: continue

		memAdded = addAutobiographicMemory()
		if not memAdded:
			mem, conf, memType = autobiographicRecall()
			recalled = rememberMemory(mem, conf, memType)

	if cmd == "none":
		confusedAnimation()
	else:
		deltaMoodQuery(fromAuto=True)

	face=getFace(GLOB['MOOD'])
	setFace(face=face[2])

	blinkingAnimation(mood=GLOB['MOOD'])
			
	GLOB['prevUsageTime'] = time.time()
	GLOB['remindersSent'] = 0

	if retVal == "exit":
		exitEvent()

def graphicsInit():
	tk_user_input.focus()
	tk_user_input.bind("<KeyRelease-Return>",(lambda event: reply(tk_user_input.get("0.0",END))))
	tk_face.bind("<Button-1>", (lambda event: blinkingAnimation()))
	tk_root.bind("<Configure>", resizeLayout)

def reply(inStr):

	rotateCircle(index=0, angle=45)

	tk_user_input.delete("0.0", END)

	if inStr.find('!!T') == 0:
		inStr = inStr[4:]
		GLOB['SEND_TEXT'] = True

	if inStr.find('!!I') == 0:
		inStr = inStr[4:]
		tkHistCat('\n>> '+' '.join(inStr.split())+'\n\n')
		return

	tkHistCat('\n>> '+' '.join(inStr.split())+'\n\n')

	tk_root.update()

	if inStr.strip() == "":
		return

	newInstr(inStr.strip())
	
if __name__ == "__main__":
	init()
	tk_root.mainloop()
