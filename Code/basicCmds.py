from common import *
from memory import *
from fileIO import jsonLoad, jsonSave

from graphics import *

# IN CMDS
def help(inCmd, inStr, matches=[[],[]]):
	CMDS = GLOB['CMDS']
	CMDE = GLOB['CMDE']

	# print out contents of CMDS
	for cmd in CMDS:
		helpStr=cmd[3][0]
		if helpStr != "": 
			#print helpStr
			tkHistCat(helpStr+'\n')
	
	if "extend" not in inStr:
		return True
	
	#print
	tkHistCat('\n')
	
	for cmd in CMDE:
		helpStr=cmd[4][0]
		if helpStr != "":
			#print helpStr
			tkHistCat('\n')

	return True

# IN CMDS
def update(inCmd, inStr, speak=True, partialChat=False, onlyChat=False, matches=[[],[]]):

	#global CMDS, CMDE, SETTINGS, EMOTIONS, CHATDATA, BLACKLIST

	if speak and not onlyChat:
		say(getResponse(inCmd), more=False, speak=setting("SPEAK"))

	# only load part of chat file for speed reasons
	
	if partialChat:
		GLOB['CHATDATA']=[]
		allChatData = load(DATA_DIR+"chatList.txt", LPC=1, addQuotes=True)

		i=0
		while i < len(allChatData)-1:
			# decide whether to include next two lines
			if randint(0,19) <= 4: # load a random 25% of the lines
				GLOB['CHATDATA'].append(allChatData[i])
				GLOB['CHATDATA'].append(allChatData[i+1])
			i += 2	
	else:
		GLOB['CHATDATA'] = load(DATA_DIR+"chatList.txt", LPC=1, addQuotes=True)

	if onlyChat: return True

	GLOB['CORRECTIONS'] = load(DATA_DIR+"corrections.txt", LPC=1)
	GLOB['CORRECTIONS']=[s[0] for s in GLOB['CORRECTIONS']]

	GLOB['CMDS']=load(SETS_DIR+"CMDS.txt", LPC=6)
	GLOB['CMDE']=load(SETS_DIR+"CMDE.txt", LPC=7)

	GLOB['SETTINGS']=load(SETS_DIR+"settings.txt", LPC=1)
	GLOB['SETTINGS']=[s[0] for s in GLOB['SETTINGS']]

	GLOB['EMOTIONS']=load(SETS_DIR+"emotions.txt", LPC=1)
	GLOB['EMOTIONS']=[s[0] for s in GLOB['EMOTIONS']]

	GLOB['FACTUAL_MEMORY'] = jsonLoad(DATA_DIR+'factual_memory.txt')
	GLOB['AUTOBIOGRAPHIC_MEMORY'] = jsonLoad(DATA_DIR+'autobiographic_memory.txt')
	if GLOB['AUTOBIOGRAPHIC_MEMORY'] == {}: GLOB['AUTOBIOGRAPHIC_MEMORY'] = []


	return True

# IN CMDS
def playMusic(inCmd, inStr, matches=[[],[]]):
	from determineFunction import refineMatches
	# clean up query string by removing extras (ex. "play the song")
	#matches = refineMatches(inCmd, inStr)
	
	#print "MATCHES = ", matches
	matches = substituteBiographicMemory(matches, queryType='what is')


	if setting('DEBUG'):
		print "MUSIC MATCHES:", matches

	if "youtube" in inStr and len(matches[0]) != 0:

		#say("Searching YouTube for \""+newStr+"\".", more=False, speak=setting("SPEAK"))
		#cmdStr=setting("WEB_BROWSER")+" https://www.youtube.com/results?search_query="+newStr.replace(' ','+')+" > /dev/null 2>&1 &"

		say("Searching YouTube for \""+matches[0][0]+"\".", more=False, speak=setting("SPEAK"))
		cmdStr=setting("WEB_BROWSER")+" https://www.youtube.com/results?search_query="+matches[0][0].replace(' ','+')+" > /dev/null 2>&1 &"
		subprocess.call(cmdStr, shell=True)
		return True

	#containsShuf= ("random" in inStr) or ("shuffle" in inStr)
	containsShuf = False
	if len(matches[1]) >= 1:
		containsShuf = ("random" in matches[1]) or ("shuffle" in matches[1])

	if len(matches[0]) == 0 and not containsShuf:
		# get song name from user
		say("Enter song name:", more=True, speak=setting("SPEAK"))
		newStr= questionBox("Enter song name:") #raw_input("")
		if newStr == "xx":
			return True
		else:
			matches[0].append(newStr)

	if len(matches[0]) == 0:
		matches[0].append(inStr)

	# generate song list to analyse
	process = subprocess.Popen(("ls "+setting("MUSIC_LOC")).split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]

	# separate into song list
	output2=output.split('\n')

	# remove .mp3 extension
	output3 =[song.replace('.mp3', '') for song in output2]

	playingSong=False

	maxMatch=0
	topSong=""
	for i in range(len(output3)):
		song=output3[i]
		#matchScore=wordSim(song, newStr)
		matchScore=wordSim(song, matches[0][0])
		if matchScore > maxMatch:
			maxMatch=matchScore
			topSong=output2[i]

	if maxMatch >= 0.6: # approx min threshold for all good queries
		playingSong=True
		cmd="vlc "+setting("MUSIC_LOC")+"\""+topSong+"\""
		subprocess.call(cmd+" >/dev/null 2>&1 &", shell=True)
	else:
		if containsShuf:
			playingSong=True
			topSong="[shuffle]"
			subprocess.call("vlc --random "+setting("MUSIC_LOC")+" >/dev/null 2>&1 &", shell=True)

	if playingSong:
		rStr = processResponse(getResponse(inCmd), [topSong])
		say(rStr, more=False, speak=setting("SPEAK"))
	else:
		say("Song not found. Perhaps you meant "+topSong.replace('.mp3', '')+".", more=False, speak=setting("SPEAK"))
		say("Searching YouTube for "+matches[0][0]+".", more=False, speak=setting("SPEAK"))
		subprocess.call(setting("WEB_BROWSER")+" https://www.youtube.com/results?search_query="+matches[0][0].replace(' ','+')+" > /dev/null 2>&1 &", shell=True)

	return True

# IN CMDS
def KTInterface(inCmd, inStr, matches=[[],[]]):
	#print "KTI"
	from determineFunction import refineMatches, updateContext

	inStr = inStr.replace('\"', '').replace('\'','')

	#matches = refineMatches(inCmd, inStr)

	matches = substituteBiographicMemory(matches, queryType='what is')

	inStr = inStr.lower()

	setFace(face="thinking_animation")

	# check if summarizing clipboard
	if "clipboard" in inStr and len(matches[0]) == 0:
		say("Summarizing data in clipboard.", more=False, speak=setting("SPEAK"), moodUpdate=False, PAUSE_SEND=True)

		CLIPBOARD = k.loadClipboard()

		#k.summary(CLIPBOARD, SEN_NUM=3, TYPE="short", CHRON=True)
		top5=k.importantSentences(CLIPBOARD, SEN_NUM=5, CHRON=True)
		top5 = [sen[0] for sen in top5]
		topTrimmed = []

		lenSum = 0
		for sen in top5:
			if lenSum < 75: # max words
				topTrimmed.append(sen)
				lenSum += len(sen.split())
			else:
				break

		topStr = ' '.join(topTrimmed)

		#print top3Str
		tkHistCat(topStr+'\n')

		#k.summary(k.loadClipboard())

		# now update the context
		if len(CLIPBOARD[0]) != 0:
			Freqs = k.getWordFreqs(k.filter(CLIPBOARD, lemmatize=True))
			if len(Freqs) != 0: 
				#print "new context: ", Freqs[0][0]
				updateContext(inStr=Freqs[0][0])

		return True

	
	if len(matches[0]) == 0:
		say(getResponse(findCMD("rephrase")), more=False, speak=setting("SPEAK"), moodUpdate=False)
		return False

	# now figure out query type
	if ("in common" in inStr or "similar" in inStr):
		if len(matches[0]) != 2:
			say("I was expecting two terms to compare.", more=False, speak=setting("SPEAK"))
			return False
		# get the word frequency intersection and return top few words

		timedOut=False
		try:
			A1, A2 = k.learn(matches[0][0]), k.learn(matches[0][1])
		except TimedOutExc:
			say("Unable to get data from Wikipedia.", more=False, speak=setting("SPEAK"))
			timedOut = True
			return True
			pass
		

		if len(A1) <= 2 and not timedOut:
			#say("Wikipedia article "+matches[0][0]+" not found.", more=True, speak=setting("SPEAK"))
			#sys.stdout.flush()
			return False
		if len(A2) <= 2 and not timedOut:
			#say("Wikipedia article "+matches[0][1]+" not found.", more=True, speak=setting("SPEAK"))
			#sys.stdout.flush()
			return False

		# say something like "let me think about this"
		say(getResponse(inCmd), more=False, speak=setting("SPEAK"), PAUSE_SEND=True)


		# get the top 3
		top3Str=', '.join([c[0] for c in k.wordIntersection(A1, A2)[0:3]])
		strProcessed=processResponse("Things #0# and #1# have in common: #2#.", replacements=[matches[0][0], matches[0][1], top3Str])
		say(strProcessed, more=False, speak=setting("SPEAK"))
		return True

	if ("tell me about" in inStr) or ("know about" in inStr) or ("teach me" in inStr) or ("learn about" in inStr):

		#print "inSTR = ", inStr
		retVal = False
		for topic in matches[0]: # already checked to be non-zero

			timedOut = False
			try:
				A = k.learn(topic)
				#if setting('DEBUG'):
					#print A
			except:# TimedOutExc:
				say("Unable to get data from Wikipedia.", more=False, speak=setting("SPEAK"))
				timedOut = True
				pass
				return True

			if len(A)<=2 and not timedOut:
				#say("Wikipedia article "+topic+" not found.", more=False, speak=setting("SPEAK"))
				retVal = False
			else:	
				say(getResponse(inCmd), more=False, speak=setting("SPEAK"), PAUSE_SEND=True)
				# get top 3 sentences on topic
				top2=k.importantSentences(A, SEN_NUM=2, CHRON=True)
				topStrs=[sen[0] for sen in top2]
				strProcessed=processResponse("Let me tell you about \"#0#\": \n\t- #1# #2#", replacements=[topic, topStrs[0], topStrs[1]])
				say(strProcessed, more=False, speak=setting("SPEAK"))
				retVal = True
		return retVal

	if "word web" in inStr:
		if len(matches[0]) != 1:
			say("I was expecting only one term in \"\"'s.", more=False, speak=setting("SPEAK"))
			return False

		say(getResponse(inCmd), more=False, speak=setting("SPEAK"), PAUSE_SEND=True)
		
		try:
			A = k.learn(matches[0][0])
		except TimedOutExc:
			say("Unable to get data from Wikipedia.", more=False, speak=setting("SPEAK"))
			pass
			return True
			
		except:
			pass
			return True
			
		if len(A) <= 2:
			say("Wikipedia article "+matches[0][0]+" not found.", more=False, speak=setting("SPEAK"))
			return False
		else:	
			k.wordWeb(A)
			return True
		
	if ("draw" in inStr) or ("paint" in inStr) or ("painting" in inStr):
		if len(matches[0]) != 1:
			say("I was expecting only one term.", more=False, speak=setting("SPEAK"))
			return False
		say(getResponse(inCmd), more=False, speak=setting("SPEAK"), PAUSE_SEND=True)
		#print "word:"+qWords[0]
		try:
			k.paintImage(k.learn(matches[0][0]))
			return True
		except TimedOutExc:
			say("Unable to get data from Wikipedia.", more=False, speak=setting("SPEAK"))
			pass

		return False

	return False

# IN CMDS
def newInput(inCmd, inStr="", matches=[[],[]]):
	# ask user for new task
	say(getResponse(inCmd), speak=False)

# IN CMDS
def goodbye(inCmd, inStr, matches=[[],[]]):

	GLOB['CONTEXT'] = "goodbye"
	GLOB['contextLocked'] = True

	# say goodbye
	say(getResponse(inCmd), more=False, speak=setting("SPEAK"))
	return True

# IN CMDS
def currentTime(inCmd, inStr, matches=[[],[]]):

	GLOB['CONTEXT'] = "time"
	GLOB['contextLocked'] = True
	# get the current time
	numStr=0
	mostRecent=""
	comboStr=""
	replacements=[]

	if ("time" in inStr or "time" in matches[0]) and not "time of" in inStr:
		timeStr=datetime.datetime.now().strftime("%r")
		mostRecent, comboStr="time", timeStr
		numStr += 1

	if ("day" in inStr or "day" in matches[0]) and not "date" in inStr:
		dayStr=datetime.datetime.now().strftime("%A %d")
		if numStr != 0: comboStr = comboStr + ", " +dayStr
		else: mostRecent, comboStr = "day", dayStr	
		numStr += 1

	if ("month" in inStr or "month" in matches[0]) and not "date" in inStr:
		monthStr=datetime.datetime.now().strftime("%B")
		comboStr += monthStr
		if numStr !=0: comboStr = comboStr + ", " +monthStr
		else: mostRecent, comboStr="month", monthStr
		numStr += 1

	if ("year" in inStr or "year" in matches[0]) and not "date" in inStr:
		yearStr=datetime.datetime.now().strftime("%Y")
		if numStr != 0: comboStr = comboStr + ", " +yearStr
		else: mostRecent, comboStr="year", yearStr
		numStr += 1

	if "date" in inStr or "date" in matches[0]:
		dateStr=datetime.datetime.now().strftime("%A %d. %B %Y")	
		if numStr != 0: comboStr = comboStr + ", " +dateStr
		else: mostRecent, comboStr="date", dateStr
		numStr += 1

	rStr=""
	if numStr == 1:
		rStr = processResponse("The #0# is #1#.", [mostRecent, comboStr])
	elif numStr >= 1:
		rStr = processResponse(getResponse(inCmd), [comboStr])
	else:
		dateStr=datetime.datetime.now().strftime("%r, %A %d. %B %Y")
		rStr = processResponse(getResponse(inCmd), [dateStr])

	say(rStr, more=False, speak=setting("SPEAK"))
	return True

# IN CMDS
def lastCmd(inCmd, inStr, histPos=0, matches=[[],[]]):
	from determineFunction import determineFunction
	CMDHIST = GLOB['CMDHIST']
	if histPos == 0:
		say(getResponse(inCmd), more=False, speak=setting("SPEAK"))

	hNum = len(CMDHIST)
	if hNum == 0:
		say("No previous commands.", more=False, speak=setting("SPEAK"))
		return

	determineFunction(CMDHIST[hNum-1-histPos][1], histPos=histPos+1)

	return True