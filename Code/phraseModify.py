import difflib


def swapPronouns(inStr):
	#from determineFunction import replaceEnd
	
	inStr = '%s'%inStr

	inStr = inStr.replace('_', ' ')

	inStr = inStr.split()

	newStr = []
	for i in range(len(inStr)):
		word = inStr[i]

		if i-1 >= 0:
			fixedStr = replaceEnd(inStr[i].lower(), cutAll=True)
			if inStr[i-1].lower() == "you" and fixedStr == "are":
				#word = "am" # I am
				word = word.lower().replace("are", "am")
			elif inStr[i-1].lower() == "i" and fixedStr == "am":
				#word = "are" # you are
				word = word.lower().replace("am", "are")
			elif inStr[i-1].lower() == "i" and fixedStr == "was":
				#word = "are" # you are
				word = word.lower().replace("was", "were")
			elif inStr[i-1].lower() == "you" and fixedStr == "were":
				#word = "are" # you are
				word = word.lower().replace("were", "was")

		if i+1 < len(inStr):
			fixedStr = replaceEnd(inStr[i+1].lower(), cutAll=True)
			if inStr[i].lower() == "am" and fixedStr == "i":
				#word = "are" # are you
				word = word.lower().replace("am", "are")
			elif inStr[i].lower() == "are" and fixedStr == "you":
				#word = "am" # ams I
				word = word.lower().replace("are", "am")
			elif inStr[i].lower() == "were" and fixedStr == "you":
				#word = "am" # ams I
				word = word.lower().replace("were", "was")
			elif inStr[i].lower() == "was" and fixedStr == "i":
				#word = "am" # ams I
				word = word.lower().replace("was", "were")

		fixedStr = replaceEnd(word.lower(), cutAll=True)
		if fixedStr == "my":
			word = word.lower().replace("my", "your")
		elif fixedStr == "your":
			word = word.lower().replace("your", "my")
		elif fixedStr == "i":
			word = word.lower().replace("i", "you")
		elif fixedStr == "you":
			word = word.lower().replace("you", "I")
		elif fixedStr == "me":
			word = word.lower().replace("me", "you")
		elif fixedStr == "yourself":
			word = word.lower().replace("yourself", "myself")
		elif fixedStr == "myself":
			word = word.lower().replace("myself", "yourself")

		newStr.append(word)

	newStr = ' '.join(newStr)

	# recapitalize it
	
	if '.' in newStr:
		sents = newStr.split('. ')
		sents = [s.strip() for s in sents]
		sents = [s.capitalize() for s in sents]
		newStr = '. '.join(sents)
	

	return newStr

def getStatePronoun(index, positive=True):
	if positive:
		if index == 0:
			return "happy"
		elif index == 1:
			return "excited"
		elif index == 2:
			return "in control"
		elif index == 3:
			return "healthy"
		elif index == 4:
			return "safe"
		elif index == 5:
			return "loved"
		elif index == 6:
			return "educated"
		elif index == 7:
			return "dedicated"
		elif index == 8:
			return "relaxed"
		elif index == 9:
			return "imaginative"
		elif index == 10:
			return "confident"
		elif index == 11:
			return "free"
	else: # negative
		if index == 0:
			return "sad"
		elif index == 1:
			return "tired"
		elif index == 2:
			return "submissive"
		elif index == 3:
			return "unhealthy"
		elif index == 4:
			return "unsafe"
		elif index == 5:
			return "neglected"
		elif index == 6:
			return "unintelligent"
		elif index == 7:
			return "incapable"
		elif index == 8:
			return "troubled"
		elif index == 9:
			return "unoriginal"
		elif index == 10:
			return "inferior"
		elif index == 11:
			return "restrained"
	return "unknown"

def listize(S, aux=False):
	if len(S) == 0:
		return ""
	elif len(S) == 1:
		return S[0]
	elif len(S) == 2:
		#if aux:
		#	S = [addAuxVerb(item, toEnd=False) for item in S]
		return S[0]+' and '+S[1]
	else:
		#if aux:
		#	S = [addAuxVerb(item, toEnd=False) for item in S]
		return ', '.join(S[:len(S)-1])+', and '+S[len(S)-1]

def addAuxVerb(inStr, toEnd=True, nextStr=""):
	from textblob import TextBlob

	if len(inStr.strip()) == 0:
		return inStr
	#print "ADDING TO:", inStr

	# see if there is already an aux verb
	aVList = ["do", "does", "is", "am", "are", "did", "was", "were"]
	prepList = ["at", "in", "on"]
	posAdjList = ["my", "your", "our", "his", "her", "its", "your", "their", "whose"]
	articleList = ["a", "the", "an"]

	if inStr.split()[0] in aVList and toEnd==False:
		return inStr

	if nextStr != "":
		#print "NEXTSTR = ", nextStr
		#print "INSTR = ", inStr
		if nextStr.split()[0].lower() in prepList:
			#print "UNMODDED"
			return inStr+' is'

		if nextStr.split()[0].lower() in posAdjList:
			#print "UNMODDED"
			return inStr+' is'

		if nextStr.split()[0].lower() in articleList:
			#print "UNMODDED"
			return inStr+' is'
		if nextStr.split()[0].isdigit():
			#print "UNMODDED"
			return inStr+' is'

	aV = ""

	# textblob has trouble singularizing "your"
	if "your" in inStr.lower().split():
		inStr = inStr.lower().replace('your', TextBlob('your').words.singularize()[0])

	#print "ADDING AUX:", inStr
	inStrL = inStr.lower()
	if inStrL in ["you", "we", "they"]:
		#return inStr+' are'
		aV = "are"
	elif inStrL == "i":
		#return inStr+' am'
		aV = "am"
	elif TextBlob(inStrL).words.singularize() != TextBlob(inStrL).words:
		#return inStr+' are'
		#print "NON-SINGULAR:", TextBlob(inStrL).words.singularize(), "vs", TextBlob(inStrL).words
		aV = "are"
	else:
		#return inStr+' is'
		T = TextBlob(inStr).tags
		if T[0][1][0] == 'N':
			aV = "is a"
		else:
			aV = "is"

	inStr = inStr.replace('ymy', 'your')

	if toEnd:
		return inStr+' '+aV
	else:
		return aV+' '+inStr


def replaceEnd(inStr, newEnd='?', cutAll=False):
	if cutAll:
		while inStr[len(inStr)-1] in ['.', '!', '?']:
			inStr = inStr[:len(inStr)-1]
		return inStr

	if inStr[len(inStr)-1] in ['.', '!', '?']:
		inStr = inStr[:len(inStr)-1]+newEnd
	else:
		inStr = inStr+newEnd

	# recapitalize it

	return inStr

def expandContractions(inStr):
	inStr = inStr.split()

	for i in range(len(inStr)):
		word = inStr[i]
		wordL = word.lower()

		if "'ll" in wordL:
			word = wordL.replace("'ll",' will')
		elif "'m" in wordL:
			word = wordL.replace("'m",' am')
		elif "n't" in wordL:
			if "won't" in wordL: # irregular contraction
				word = wordL.replace("won't", "will not")
			else:
				word = wordL.replace("n't",' not')
		elif "'re" in wordL:
			word = wordL.replace("'re",' are')
		elif "'s" in wordL:
			word = wordL.replace("'s",' is')
		elif "'ve" in wordL:
			word = wordL.replace("'ve",' have')
		elif "'d" in wordL:
			word = wordL.replace("'d",' had')

		inStr[i] = word

	return ' '.join(inStr)

def removeStrange(inStr):
	inStr.replace('\n', ' ')

	newStr = []
	for i in range(len(inStr)):
		c = inStr[i]
		if ord(c) < 32 or ord(c) > 126:
			newStr.append(' ')
		else:
			newStr.append(c)

	return ''.join(newStr)

def processResponse(inStr, replacements, syns=True):
	# inStr: the string to be processed
	# replacements: list of things to go into ##'s
	for i in range(len(replacements)):
		inStr = inStr.replace('#'+'%s'%i+'#', replacements[i])

	return inStr

def wordSim(wA, wB, useInScore=False, basic=False):

	if wA.strip() == wB.strip():
		return 1.0
	# calculate word/sting similarity using combinaion of techniques
	raw = difflib.SequenceMatcher(a=wA.lower(), b=wB.lower()).ratio()

	if basic: return raw

	lA, lB = len(wA), len(wB)
	if lA == 0 or lB == 0: return 0
	lavg=pow(lA*lB, 0.5)
	score = pow(raw, 1.0 + 2.0/lavg)

	sA, sB = set(wA.lower().split()), set(wB.lower().split())
	shareWords=len(list(sA & sB))
	pctShared = shareWords*2.0 / (len(wA.split()) + len(wB.split()))

	lwavg=pow(len(wA.split())*len(wB.split()), 0.5)
	inSideScore=0
	inSideWeight = 1.0*lwavg/7.0 


	if useInScore:
		if wA in wB: inSideScore +=1
		if wB in wA: inSideScore +=1

	if not useInScore:
		return pow(pctShared, 0.5)*0.5 + 0.5*score
	else:
		return (inSideScore*inSideWeight  + score) / (1.0 + inSideScore*inSideWeight)

def split2(string):

	# return list of words with start and end indices of each
	words = []

	# 65 - 90
	# 97 - 122

	inWord=False
	start = 0
	end = 0
	for i in range(len(string)):

		if not inWord and string[i].isalpha():
			inWord = True
			start = i
			end = 0
		elif inWord and not string[i].isalpha():
			inWord = False
			end = i
			words.append([string[start:end], start, end])
		elif inWord and i == len(string)-1:
			end = i+1
			words.append([string[start:end], start, end])

	return words
