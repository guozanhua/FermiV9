from header import *
from graphics import *

def setting(setStr):
	# search settings for setStr and return value
	for s in GLOB['SETTINGS']:
		if s[0]==setStr:
			return s[1]
	return ""

def linTrans(x, fixedPts):
	x1 = fixedPts[0][0]
	y1 = fixedPts[0][1]

	x2 = fixedPts[1][0]
	y2 = fixedPts[1][1]

	m = 1.0*(y2-y1)/(x2-x1)

	return m*(x - x1) + y1

def getVecDiffSum(vA, vB):
	# subtract vectors

	if len(vA) != len(vB):
		print "ERROR: vectors not same dimension"
		return 1.0

	dim = len(vA)

	diffSum = 0

	for v in zip(vA, vB):
		diffSum += abs(v[0] - v[1])

	return diffSum

def getVecDiffLen(vA, vB, normalize=True, maxDiff=1.0):
	if len(vA) != len(vB):
		print "ERROR: vectors not same dimension"
		return 1.0

	dim = len(vA)

	diff = [vA[i]-vB[i] for i in range(0, dim)] 
	diffSq= [diff[i]*diff[i] for i in range(0, dim)]

	if normalize:
		return pow(sum(diffSq), 0.5)/ (maxDiff*pow(dim, 0.5))
	else:
		return pow(sum(diffSq), 0.5)

def getYesNo(inStr):
	inStr2=inStr.lower()
	yesStrs = ["yes", "yeah", "affirmative", "sure", "okay"]
	noStrs  = ["no", "nope", "negative", "not"]
	
	yesInStr= bool(set(inStr2.split()) & set(yesStrs))
	noInStr = bool(set(inStr2.split()) & set(noStrs))
	
	if yesInStr and not noInStr:
		return True
	else:
		return ("y" == inStr2)

def getChatResponse(inStr, fromAI=False):
	from emotions import getMood, getMoodDiff

	# load misc chat file and find response
	CHATDATA = GLOB['CHATDATA']
	MOOD = GLOB['MOOD']

	if not fromAI:
		topMatch=""
		topResponse=""
		maxMatch=0

		for i in range(len(CHATDATA)):
			line = CHATDATA[i][0]
			if line[0:2] == "Q:":
				matchScore = wordSim(line[3:], inStr, basic=True)
				if matchScore >= maxMatch:
					maxMatch = matchScore
					topMatch=CHATDATA[i][0]
					topResponse=CHATDATA[i+1][0]
		
		#print topMatch
		return topResponse.replace('\n', ''), maxMatch
	else:
		topMatch=""
		topResponse=""
		minDist=10 # init val is higher than possible

		for i in range(len(CHATDATA)):
			line = CHATDATA[i][0]
			if line[0:2] == "Q:":
				lineMood = getMood(line, fromAI=True)
				moodDist = getMoodDiff(MOOD, lineMood) #difference between line mood and current MOOD
				if moodDist <= minDist:
					minDist = moodDist
					topMatch=CHATDATA[i][0]
					topResponse=CHATDATA[i+1][0] # also store the response to the query

		return topMatch.replace('Q: ','').replace('\n', ''), topResponse, minDist

def getResponse(inCmd, inStr=""):
	# analyze CMD's for response
	rNum = randint(0,len(inCmd[2])-1) # inclusive set
	return inCmd[2][rNum]

def slowType(inStr):
	MOOD = GLOB['MOOD']
	# print characters one by one
	mval=MOOD[1] # use arousal value to determine speed

	# experimentally determined
	minSpeed = 0.068
	maxSpeed = 0.04
	midSpeed = 0.5*(minSpeed + maxSpeed)

	typeSpeed = mval*0.5*(maxSpeed-minSpeed) + midSpeed

	for c in inStr:
		#sys.stdout.write( '%s' % c )
		#sys.stdout.flush()
		kHistCat('%s' % c)
		time.sleep(typeSpeed)
	#print
	tkHistCat('\n')

def say(inStr, more=True, speak=False, moodUpdate=True, fromAuto=False, describeFace=False, location="history", PAUSE_SEND=False):
	from emotions import getFace, getMood, updateMood

	MOOD = GLOB['MOOD']
	PREVMOOD = GLOB['PREVMOOD']

	toSay=inStr
	if toSay == "" and not GLOB['onQuery']:
		return
	
	if moodUpdate:
		newMood = getMood(toSay)
		GLOB['PREVMOOD']=copy.deepcopy(GLOB['MOOD'])

		# more confident -> more weight on what he says
		mWeight = 0.5*(1.0 + GLOB['MOOD'][2])
		mWeight = [mWeight]*3+[0]*(GLOB['MOODDIM']-3)

		GLOB['MOOD']=updateMood(newMood, weight= mWeight)

	# calculate mood string
	face=getFace(MOOD)
	moodStr=""
	if face[0]=="":
		moodStr="("+getFace(MOOD)[2]+")" # use the description
	else: 		
		moodStr=getFace(MOOD)[0] # use the emoticon

	if describeFace:
		moodStr = moodStr+" - ("+face[2]+")"

	#print ("\n["+setting("YOUR_NAME")+" "+moodStr+"] "),
	setFace(face=face[2])
	#tkHistCat("["+setting("YOUR_NAME")+" "+moodStr+"] ")

	toWriteStr=""

	if location != "top":
		#writeToLocation("["+setting("YOUR_NAME")+"] ", location)
		toWriteStr+="["+setting("YOUR_NAME")+"] "

	if speak == True:
		pitchMod=int(30.0*MOOD[0]) # happiness
		speedMod=int(50.0*MOOD[1]) # excitement
		if setting("YOUR_GENDER") == "female":
			speed=190 + speedMod #arousal value
			pitch=70 +pitchMod #valence value
			voice = "-a 20 -v english_rp+f5 -p "+'%s'%pitch+" -s "+'%s'%speed
		else:
			speed=190 + speedMod #arousal value
			pitch=30 +pitchMod #valence value
			voice = "-a 20 -v english_rp+m5 -p "+'%s'%pitch+" -s "+'%s'%speed
		
		cmd = "echo \""+inStr+"\" > toSay.txt; espeak "+voice+" -f toSay.txt >/dev/null 2>&1 &"
		subprocess.call(cmd, shell=True)

	if setting("SLOW_TYPE"): 
		slowType(toSay)
	else: 
		#writeToLocation(toSay+'\n', location)
		toWriteStr += toSay+'\n'
		writeToLocation(toWriteStr, location, PAUSE_SEND=PAUSE_SEND)

	rotateCircle(index=1, angle=30)

def playSound(soundName="default", delay=0):
	rotateCircle(index=4, angle=30)

	sDir = DATA_DIR+"/sounds/"
	if soundName == "default":
		subprocess.call("play -v 0.25 "+sDir+"Looking\ Up.mp3 >/dev/null 2>&1 &", shell=True)
	elif soundName == "intro":
		subprocess.call("play -v 0.25 "+sDir+"Looking\ Up.mp3 >/dev/null 2>&1 &", shell=True)
	elif soundName == "recurring":
		subprocess.call("play -v 0.5 "+sDir+"Connected.mp3 >/dev/null 2>&1 &", shell=True)

	if not setting('CHIRP') or setting('QUIET'):
		return



	fileName="chirp1"
	numChirpFiles=3
	if "chirp" in soundName:
		fileName = "chirp"+'%s'%randint(1,numChirpFiles)+".mp3"
	delayStr = "delay "+'%s'%delay

	#print fileName
	sadMod=""
	if soundName == "chirp-happy":
		sadMod = "pitch 50"
	elif soundName == "chirp-sad":
		# make sad
		sadMod = "reverse pitch -600"
	else:
		sadMod = ""

	subprocess.call("play -v 0.5 "+sDir+fileName+" "+sadMod+' '+delayStr+" >/dev/null 2>&1 &", shell=True)

	return